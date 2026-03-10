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
    with open(os.path.join(args.data_dir, 'formula_vocab.json'), 'r', encoding='utf-8') as f:
        formula_vocab = json.load(f)

    # 反转词表
    idx_to_formula = {v: k for k, v in formula_vocab.items()}
    idx_to_herb = {v: k for k, v in herb_vocab.items()}

    # 构建模型
    model = TCMFormulaNet(
        num_symptoms=len(symptom_vocab),
        num_formulas=len(formula_vocab),
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
        symptom_vocab, herb_vocab, formula_vocab, augment=False
    )
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    # 评估
    correct_top1 = 0
    correct_topk = 0
    total = 0
    herb_tp, herb_fp, herb_fn = 0, 0, 0

    with torch.no_grad():
        for batch in val_loader:
            symptoms = batch['symptoms'].to(device)
            formula_target = batch['formula_target'].to(device)
            herb_target = batch['herb_target'].to(device)

            formula_logits, herb_logits, dosage_pred = model(symptoms)

            # Top-1 准确率
            pred = formula_logits.argmax(dim=-1)
            correct_top1 += (pred == formula_target).sum().item()

            # Top-K 准确率
            _, topk_pred = formula_logits.topk(args.top_k, dim=-1)
            for i in range(symptoms.size(0)):
                if formula_target[i] in topk_pred[i]:
                    correct_topk += 1

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
    print(f'   方剂分类 Top-1 准确率: {correct_top1/total*100:.1f}%')
    print(f'   方剂分类 Top-{args.top_k} 准确率: {correct_topk/total*100:.1f}%')
    print(f'   药材预测 Precision:     {precision:.3f}')
    print(f'   药材预测 Recall:        {recall:.3f}')
    print(f'   药材预测 F1:            {f1:.3f}')

    # 交互式测试
    print('\n' + '=' * 60)
    print('  🧪 交互式测试 (输入症状标签，空行退出)')
    print('=' * 60)
    print(f'  可用症状: {", ".join(list(symptom_vocab.keys())[:20])}...')

    while True:
        try:
            raw = input('\n输入症状 (逗号分隔): ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            break

        symptoms_input = [s.strip() for s in raw.split(',')]
        symptom_vec = torch.zeros(1, len(symptom_vocab))
        for s in symptoms_input:
            if s in symptom_vocab:
                symptom_vec[0, symptom_vocab[s]] = 1.0
            else:
                print(f'   ⚠️ 未知症状: {s}')

        symptom_vec = symptom_vec.to(device)
        result = model.predict(symptom_vec, top_k=3)

        print(f'\n  📋 推荐方剂:')
        for i in range(result['formula_indices'].size(1)):
            idx = result['formula_indices'][0, i].item()
            prob = result['formula_probs'][0, i].item()
            name = idx_to_formula.get(idx, f'方剂{idx}')
            print(f'     {i+1}. {name} (置信度: {prob*100:.1f}%)')

        # 推荐药材
        herb_probs = result['herb_probs'][0]
        dosages = result['dosages'][0]
        selected = (herb_probs > 0.5).nonzero(as_tuple=True)[0]
        if len(selected) > 0:
            print(f'\n  💊 推荐药材:')
            for idx in selected:
                idx = idx.item()
                name = idx_to_herb.get(idx, f'药{idx}')
                prob = herb_probs[idx].item()
                dose = dosages[idx].item()
                print(f'     · {name} {dose:.0f}g (概率: {prob:.2f})')

    print('\n👋 评估结束')


if __name__ == '__main__':
    main()
