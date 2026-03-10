"""
训练脚本 — 中医方剂推荐模型训练

用法:
    python scripts/train.py --device cuda --epochs 200 --batch_size 32 --lr 0.001

在5090上建议:
    python scripts/train.py --device cuda --epochs 500 --batch_size 64 --lr 0.0005 --embed_dim 512 --num_layers 6
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts

# 添加项目根目录到path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.tcm_net import TCMFormulaNet, MultiTaskLoss
from models.dataset import TCMDataset

try:
    from torch.utils.tensorboard import SummaryWriter
    HAS_TENSORBOARD = True
except ImportError:
    HAS_TENSORBOARD = False


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    loss_details = {'loss_formula': 0, 'loss_herb': 0, 'loss_dosage': 0}
    num_batches = 0

    for batch in dataloader:
        symptoms = batch['symptoms'].to(device)
        formula_target = batch['formula_target'].to(device)
        herb_target = batch['herb_target'].to(device)
        dosage_target = batch['dosage_target'].to(device)

        optimizer.zero_grad()

        formula_logits, herb_logits, dosage_pred = model(symptoms)
        loss, details = criterion(
            formula_logits, herb_logits, dosage_pred,
            formula_target, herb_target, dosage_target
        )

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item()
        for k in loss_details:
            loss_details[k] += details.get(k, 0)
        num_batches += 1

    avg_loss = total_loss / max(num_batches, 1)
    for k in loss_details:
        loss_details[k] /= max(num_batches, 1)

    return avg_loss, loss_details


@torch.no_grad()
def validate(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0
    correct_formula = 0
    total_samples = 0
    herb_precision_sum = 0
    herb_recall_sum = 0
    num_batches = 0

    for batch in dataloader:
        symptoms = batch['symptoms'].to(device)
        formula_target = batch['formula_target'].to(device)
        herb_target = batch['herb_target'].to(device)
        dosage_target = batch['dosage_target'].to(device)

        formula_logits, herb_logits, dosage_pred = model(symptoms)
        loss, _ = criterion(
            formula_logits, herb_logits, dosage_pred,
            formula_target, herb_target, dosage_target
        )

        total_loss += loss.item()

        # 方剂分类准确率
        pred_formula = formula_logits.argmax(dim=-1)
        correct_formula += (pred_formula == formula_target).sum().item()
        total_samples += symptoms.size(0)

        # 药材预测 Precision / Recall
        herb_pred = (torch.sigmoid(herb_logits) > 0.5).float()
        tp = (herb_pred * herb_target).sum(dim=-1)
        pred_pos = herb_pred.sum(dim=-1).clamp(min=1)
        true_pos = herb_target.sum(dim=-1).clamp(min=1)
        herb_precision_sum += (tp / pred_pos).sum().item()
        herb_recall_sum += (tp / true_pos).sum().item()

        num_batches += 1

    n = max(total_samples, 1)
    return {
        'val_loss': total_loss / max(num_batches, 1),
        'formula_accuracy': correct_formula / n,
        'herb_precision': herb_precision_sum / n,
        'herb_recall': herb_recall_sum / n,
    }


def main():
    parser = argparse.ArgumentParser(description='中医方剂推荐模型训练')
    parser.add_argument('--data_dir', type=str, default='data', help='训练数据目录')
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints')
    parser.add_argument('--log_dir', type=str, default='logs')
    parser.add_argument('--device', type=str, default='auto',
                        choices=['auto', 'cuda', 'cpu', 'mps'],
                        help='训练设备')
    parser.add_argument('--epochs', type=int, default=200)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--weight_decay', type=float, default=0.01)
    parser.add_argument('--embed_dim', type=int, default=256)
    parser.add_argument('--num_heads', type=int, default=8)
    parser.add_argument('--num_layers', type=int, default=4)
    parser.add_argument('--dim_feedforward', type=int, default=512)
    parser.add_argument('--dropout', type=float, default=0.1)
    parser.add_argument('--save_every', type=int, default=20, help='每N轮保存一次')
    parser.add_argument('--resume', type=str, default=None, help='从checkpoint恢复')
    args = parser.parse_args()

    # 设备选择
    if args.device == 'auto':
        if torch.cuda.is_available():
            device = torch.device('cuda')
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device('mps')
        else:
            device = torch.device('cpu')
    else:
        device = torch.device(args.device)

    print('=' * 60)
    print('  🏥 中医方剂推荐 — 深度学习训练')
    print('=' * 60)
    print(f'  设备: {device}')
    if device.type == 'cuda':
        print(f'  GPU:  {torch.cuda.get_device_name(0)}')
        gpu_mem = getattr(torch.cuda.get_device_properties(0), 'total_memory', None) or getattr(torch.cuda.get_device_properties(0), 'total_mem', 0)
        print(f'  显存: {gpu_mem / 1e9:.1f} GB')
    print(f'  时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)

    os.makedirs(args.checkpoint_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)

    # 加载词表和元数据
    print('\n📂 加载数据...')
    with open(os.path.join(args.data_dir, 'meta.json'), 'r', encoding='utf-8') as f:
        meta = json.load(f)
    with open(os.path.join(args.data_dir, 'symptom_vocab.json'), 'r', encoding='utf-8') as f:
        symptom_vocab = json.load(f)
    with open(os.path.join(args.data_dir, 'herb_vocab.json'), 'r', encoding='utf-8') as f:
        herb_vocab = json.load(f)
    with open(os.path.join(args.data_dir, 'formula_vocab.json'), 'r', encoding='utf-8') as f:
        formula_vocab = json.load(f)

    num_symptoms = len(symptom_vocab)
    num_herbs = len(herb_vocab)
    num_formulas = len(formula_vocab)

    print(f'   症状: {num_symptoms} | 药材: {num_herbs} | 方剂: {num_formulas}')
    print(f'   训练: {meta["train_samples"]} | 验证: {meta["val_samples"]}')

    # 数据集
    train_dataset = TCMDataset(
        os.path.join(args.data_dir, 'train_data.json'),
        symptom_vocab, herb_vocab, formula_vocab, augment=True
    )
    val_dataset = TCMDataset(
        os.path.join(args.data_dir, 'val_data.json'),
        symptom_vocab, herb_vocab, formula_vocab, augment=False
    )

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True,
                              num_workers=0, pin_memory=(device.type == 'cuda'))
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False,
                            num_workers=0, pin_memory=(device.type == 'cuda'))

    # 模型
    print(f'\n🧠 构建模型 (embed={args.embed_dim}, heads={args.num_heads}, layers={args.num_layers})...')
    model = TCMFormulaNet(
        num_symptoms=num_symptoms,
        num_formulas=num_formulas,
        num_herbs=num_herbs,
        embed_dim=args.embed_dim,
        num_heads=args.num_heads,
        num_layers=args.num_layers,
        dim_feedforward=args.dim_feedforward,
        dropout=args.dropout,
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f'   参数量: {total_params:,} (可训练: {trainable_params:,})')

    criterion = MultiTaskLoss().to(device)
    optimizer = AdamW(
        list(model.parameters()) + list(criterion.parameters()),
        lr=args.lr, weight_decay=args.weight_decay
    )
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=20, T_mult=2, eta_min=1e-6)

    # TensorBoard
    writer = None
    if HAS_TENSORBOARD:
        writer = SummaryWriter(log_dir=args.log_dir)

    # 恢复训练
    start_epoch = 0
    best_val_loss = float('inf')
    if args.resume and os.path.exists(args.resume):
        print(f'\n📥 恢复训练: {args.resume}')
        ckpt = torch.load(args.resume, map_location=device)
        model.load_state_dict(ckpt['model_state_dict'])
        optimizer.load_state_dict(ckpt['optimizer_state_dict'])
        start_epoch = ckpt.get('epoch', 0)
        best_val_loss = ckpt.get('best_val_loss', float('inf'))
        print(f'   从 epoch {start_epoch} 恢复, 最佳验证损失: {best_val_loss:.4f}')

    # 训练循环
    print(f'\n🚀 开始训练 (epochs={args.epochs}, batch_size={args.batch_size}, lr={args.lr})')
    print('-' * 60)

    for epoch in range(start_epoch, args.epochs):
        t0 = time.time()

        # 训练
        train_loss, train_details = train_one_epoch(model, train_loader, criterion, optimizer, device)
        scheduler.step()

        # 验证
        val_metrics = validate(model, val_loader, criterion, device)

        elapsed = time.time() - t0

        # 打印日志
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f'Epoch {epoch+1:4d}/{args.epochs} | '
                  f'Train: {train_loss:.4f} | '
                  f'Val: {val_metrics["val_loss"]:.4f} | '
                  f'Acc: {val_metrics["formula_accuracy"]*100:.1f}% | '
                  f'P: {val_metrics["herb_precision"]:.3f} | '
                  f'R: {val_metrics["herb_recall"]:.3f} | '
                  f'{elapsed:.1f}s')

        # TensorBoard
        if writer:
            writer.add_scalar('Loss/train', train_loss, epoch)
            writer.add_scalar('Loss/val', val_metrics['val_loss'], epoch)
            writer.add_scalar('Accuracy/formula', val_metrics['formula_accuracy'], epoch)
            writer.add_scalar('Metrics/herb_precision', val_metrics['herb_precision'], epoch)
            writer.add_scalar('Metrics/herb_recall', val_metrics['herb_recall'], epoch)
            writer.add_scalar('LR', optimizer.param_groups[0]['lr'], epoch)

        # 保存最佳模型
        if val_metrics['val_loss'] < best_val_loss:
            best_val_loss = val_metrics['val_loss']
            save_path = os.path.join(args.checkpoint_dir, 'best_model.pt')
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_val_loss': best_val_loss,
                'val_metrics': val_metrics,
                'args': vars(args),
                'meta': meta,
            }, save_path)

        # 定期保存
        if (epoch + 1) % args.save_every == 0:
            save_path = os.path.join(args.checkpoint_dir, f'epoch_{epoch+1}.pt')
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_val_loss': best_val_loss,
                'args': vars(args),
                'meta': meta,
            }, save_path)

    print('-' * 60)
    print(f'✅ 训练完成! 最佳验证损失: {best_val_loss:.4f}')
    print(f'   最佳模型: {os.path.join(args.checkpoint_dir, "best_model.pt")}')

    if writer:
        writer.close()


if __name__ == '__main__':
    main()
