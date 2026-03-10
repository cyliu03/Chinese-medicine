"""
模型导出脚本 — 将训练好的模型导出为可部署格式

用法:
    python scripts/export_model.py --checkpoint checkpoints/best_model.pt --output models/tcm_model.pt
"""

import os
import sys
import json
import argparse

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.tcm_net import TCMFormulaNet


def main():
    parser = argparse.ArgumentParser(description='导出中医方剂推荐模型')
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--output', type=str, default='models/tcm_model.pt')
    parser.add_argument('--data_dir', type=str, default='data')
    parser.add_argument('--export_onnx', action='store_true', help='同时导出ONNX格式')
    args = parser.parse_args()

    print('=' * 60)
    print('  🏥 中医方剂推荐 — 模型导出')
    print('=' * 60)

    # 加载
    ckpt = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
    saved_args = ckpt['args']
    meta = ckpt['meta']

    with open(os.path.join(args.data_dir, 'symptom_vocab.json'), 'r', encoding='utf-8') as f:
        symptom_vocab = json.load(f)
    with open(os.path.join(args.data_dir, 'herb_vocab.json'), 'r', encoding='utf-8') as f:
        herb_vocab = json.load(f)
    with open(os.path.join(args.data_dir, 'formula_vocab.json'), 'r', encoding='utf-8') as f:
        formula_vocab = json.load(f)

    model = TCMFormulaNet(
        num_symptoms=len(symptom_vocab),
        num_formulas=len(formula_vocab),
        num_herbs=len(herb_vocab),
        embed_dim=saved_args.get('embed_dim', 256),
        num_heads=saved_args.get('num_heads', 8),
        num_layers=saved_args.get('num_layers', 4),
        dim_feedforward=saved_args.get('dim_feedforward', 512),
        dropout=0,
    )
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()

    # 导出完整推理包
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    export_data = {
        'model_state_dict': model.state_dict(),
        'symptom_vocab': symptom_vocab,
        'herb_vocab': herb_vocab,
        'formula_vocab': formula_vocab,
        'model_config': {
            'num_symptoms': len(symptom_vocab),
            'num_formulas': len(formula_vocab),
            'num_herbs': len(herb_vocab),
            'embed_dim': saved_args.get('embed_dim', 256),
            'num_heads': saved_args.get('num_heads', 8),
            'num_layers': saved_args.get('num_layers', 4),
            'dim_feedforward': saved_args.get('dim_feedforward', 512),
        },
        'train_info': {
            'epoch': ckpt['epoch'],
            'best_val_loss': ckpt['best_val_loss'],
            'val_metrics': ckpt.get('val_metrics', {}),
        },
    }

    torch.save(export_data, args.output)
    file_size = os.path.getsize(args.output) / 1024 / 1024
    print(f'\n✅ PyTorch 模型已导出: {args.output} ({file_size:.1f} MB)')

    # ONNX 导出 (可选)
    if args.export_onnx:
        onnx_path = args.output.replace('.pt', '.onnx')
        dummy_input = torch.zeros(1, len(symptom_vocab))
        try:
            torch.onnx.export(
                model, dummy_input, onnx_path,
                input_names=['symptoms'],
                output_names=['formula_logits', 'herb_logits', 'dosage_pred'],
                dynamic_axes={'symptoms': {0: 'batch'}}
            )
            print(f'✅ ONNX 模型已导出: {onnx_path}')
        except Exception as e:
            print(f'⚠️ ONNX 导出失败: {e}')

    # 导出词表为独立JSON (方便前端使用)
    vocab_dir = os.path.dirname(args.output)
    for name, vocab in [('symptom_vocab', symptom_vocab),
                         ('herb_vocab', herb_vocab),
                         ('formula_vocab', formula_vocab)]:
        path = os.path.join(vocab_dir, f'{name}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(vocab, f, ensure_ascii=False, indent=2)

    print(f'✅ 词表已导出到: {vocab_dir}/')
    print('\n📌 下一步: 将导出的模型集成到 Next.js API 中')
    print('=' * 60)


if __name__ == '__main__':
    main()
