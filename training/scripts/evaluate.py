"""
评估脚本 — 加载训练好的模型并评估性能

用法:
    python scripts/evaluate.py --checkpoint checkpoints/best_model.pt
"""

import os
import sys
import json
import argparse

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.tcm_net import TCMFormulaNet
from models.dataset import TCMDataset


def main():
    parser = argparse.ArgumentParser(description='评估中医方剂推荐模型')
    parser.add_argument('--checkpoint', type=str, required=True, help='模型检查点路径')
    parser.add_argument('--data_dir', type=str, default='data')
    parser.add_argument('--device', type=str, default='auto')
    parser.add_argument('--top_k', type=int, default=3, help='Top-K 准确率')
    args = parser.parse_args()

    if args.device == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(args.device)

    print('=' * 60)
    print('  🏥 中医方剂推荐 — 模型评估')
    print('=' * 60)

    # 加载检查点
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    saved_args = ckpt['args']
    meta = ckpt['meta']

    # 加载词表
    with open(os.path.join(args.data_dir, 'symptom_vocab.json'), 'r', encoding='utf-8') as f:
        symptom_vocab = json.load(f)
    with open(os.path.join(args.data_dir, 'herb_vocab.json'), 'r', encoding='utf-8') as f:
        herb_vocab = json.load(f)

    # 反转词表
    idx_to_herb = {v: k for k, v in herb_vocab.items()}

    # 构建模型
    model = TCMFormulaNet(
        num_symptoms=len(symptom_vocab),
        num_herbs=len(herb_vocab),
        embed_dim=saved_args.get('embed_dim', 256),
        num_heads=saved_args.get('num_heads', 8),
        num_layers=saved_args.get('num_layers', 4),
        dim_feedforward=saved_args.get('dim_feedforward', 512),
        dropout=0,  # 评估时不需要dropout
    ).to(device)

    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()

    print(f'\n✅ 模型加载成功 (epoch {ckpt["epoch"]})')
    print(f'   训练时最佳验证损失: {ckpt["best_val_loss"]:.4f}')

    # 加载验证集
    val_dataset = TCMDataset(
        os.path.join(args.data_dir, 'val_data.json'),
        symptom_vocab, herb_vocab, augment=False
    )
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    # 评估
    total = 0
    herb_tp, herb_fp, herb_fn = 0, 0, 0

    print("⏳ 正在评估验证集...")
    with torch.no_grad():
        for batch in val_loader:
            symptoms = batch['symptoms'].to(device)
            herb_target = batch['herb_target'].to(device)

            herb_logits, dosage_pred = model(symptoms)

            # 药材 Precision / Recall / F1
            herb_pred = (torch.sigmoid(herb_logits) > 0.5).float()
            herb_tp += (herb_pred * herb_target).sum().item()
            herb_fp += (herb_pred * (1 - herb_target)).sum().item()
            herb_fn += ((1 - herb_pred) * herb_target).sum().item()

            total += symptoms.size(0)

    precision = herb_tp / max(herb_tp + herb_fp, 1)
    recall = herb_tp / max(herb_tp + herb_fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-8)

    print(f'\n📊 评估结果 ({total} 个样本):')
    print(f'   药材预测 Precision (查准率): {precision:.3f}')
    print(f'   药材预测 Recall    (查全率): {recall:.3f}')
    print(f'   药材预测 F1 Score         : {f1:.3f}')

    # 交互式测试
    print('\n' + '=' * 60)
    print('  🧪 交互式测试 (输入症状标签，空行退出)')
    print('=' * 60)
    print(f'  可用症状示例: {", ".join(list(symptom_vocab.keys())[:15])}...')

    while True:
        try:
            raw = input('\n输入症状 (逗号分隔): ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            break

        if raw == "test1": 
            raw = "发热,恶寒,头痛,无汗"
            print(f" (自动填充测试1: {raw})")
        
        if raw == "test2": 
            raw = "恶心,呕吐,腹痛,腹泻"
            print(f" (自动填充测试2: {raw})")

        symptoms_input = [s.strip() for s in raw.split(',')]
        symptom_vec = torch.zeros(1, len(symptom_vocab))
        valid_symptoms = []
        for s in symptoms_input:
            if s in symptom_vocab:
                symptom_vec[0, symptom_vocab[s]] = 1.0
                valid_symptoms.append(s)
            else:
                print(f'   ⚠️ 未知症状: {s}')

        print(f"👉 确认症状: {', '.join(valid_symptoms)}")

        symptom_vec = symptom_vec.to(device)
        result = model.predict(symptom_vec)

        # 推荐药材
        herb_probs = result['herb_probs'][0]
        dosages = result['dosages'][0]
        selected = (herb_probs > 0.5).nonzero(as_tuple=True)[0]
        
        if len(selected) > 0:
            print(f'\n  💊 AI 中医师 开具处方:')
            print(f'  {"药材":<10} | {"剂量":<8} | {"置信度":<8}')
            print('  ' + '-'*35)
            
            # 按概率排序
            prescriptions = []
            for idx in selected:
                idx = idx.item()
                name = idx_to_herb.get(idx, f'药{idx}')
                prob = herb_probs[idx].item()
                dose = dosages[idx].item()
                # 过滤掉低于 1g 的微小剂量预测
                if dose >= 1.0:
                    prescriptions.append((name, dose, prob))
            
            prescriptions.sort(key=lambda x: x[2], reverse=True)
            
            for name, dose, prob in prescriptions:
                print(f'  {name:<10} | {dose:>5.1f}g   | {prob*100:>5.1f}%')
        else:
            print(f'\n  ⚠️ 症状信息不足，AI 认为暂不需要服药。')

    print('\n👋 评估结束')


if __name__ == '__main__':
    main()
