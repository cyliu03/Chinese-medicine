"""
V16 模型 - 数据增强 + LSAN + 标签相关性

结合多种优化:
  1. 经典方剂数据增强
  2. Label-Specific Attention
  3. 标签相关性建模
  4. 更好的损失函数
"""

import os
import sys
import json
import argparse
import time
import random
from datetime import datetime
from collections import defaultdict

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts


CLASSIC_FORMULAS = {
    "麻黄汤": {"symptoms": ["咳嗽", "发热", "恶寒", "头痛", "无汗"], "herbs": ["麻黄", "桂枝", "杏仁", "甘草"]},
    "桂枝汤": {"symptoms": ["发热", "恶寒", "头痛", "汗出"], "herbs": ["桂枝", "白芍", "生姜", "大枣", "甘草"]},
    "四君子汤": {"symptoms": ["气短", "乏力", "食欲不振"], "herbs": ["人参", "白术", "茯苓", "甘草"]},
    "四物汤": {"symptoms": ["头晕", "心悸", "失眠"], "herbs": ["当归", "熟地黄", "白芍", "川芎"]},
    "六君子汤": {"symptoms": ["气短", "乏力", "食欲不振", "腹胀", "咳嗽", "痰多"], "herbs": ["人参", "白术", "茯苓", "甘草", "陈皮", "半夏"]},
    "归脾汤": {"symptoms": ["心悸", "失眠", "健忘", "乏力", "食欲不振"], "herbs": ["人参", "白术", "茯苓", "当归", "龙眼肉", "酸枣仁", "远志", "木香", "甘草"]},
    "逍遥散": {"symptoms": ["胁痛", "口苦", "食欲不振", "月经不调"], "herbs": ["柴胡", "当归", "白芍", "白术", "茯苓", "薄荷", "甘草"]},
    "补中益气汤": {"symptoms": ["气短", "乏力", "头晕", "自汗", "食欲不振"], "herbs": ["黄芪", "人参", "白术", "当归", "陈皮", "升麻", "柴胡", "甘草"]},
    "肾气丸": {"symptoms": ["腰痛", "畏寒", "乏力", "头晕", "耳鸣"], "herbs": ["熟地黄", "山药", "山茱萸", "茯苓", "泽泻", "牡丹皮", "附子", "肉桂"]},
    "理中丸": {"symptoms": ["腹痛", "腹泻", "恶心", "呕吐", "食欲不振", "畏寒"], "herbs": ["人参", "白术", "干姜", "甘草"]},
    "二陈汤": {"symptoms": ["咳嗽", "痰多", "恶心", "呕吐", "胸闷"], "herbs": ["半夏", "陈皮", "茯苓", "甘草"]},
    "平胃散": {"symptoms": ["腹胀", "食欲不振", "恶心", "呕吐", "乏力"], "herbs": ["苍术", "厚朴", "陈皮", "甘草"]},
    "银翘散": {"symptoms": ["发热", "咳嗽", "咽干", "头痛", "口干"], "herbs": ["金银花", "连翘", "桔梗", "薄荷", "牛蒡子", "荆芥", "甘草"]},
    "桑菊饮": {"symptoms": ["咳嗽", "发热", "口干", "头痛"], "herbs": ["桑叶", "菊花", "杏仁", "连翘", "薄荷", "桔梗", "芦根", "甘草"]},
    "小柴胡汤": {"symptoms": ["口苦", "口干", "胁痛", "食欲不振", "恶心"], "herbs": ["柴胡", "黄芩", "人参", "半夏", "生姜", "大枣", "甘草"]},
    "玉屏风散": {"symptoms": ["自汗", "畏寒", "乏力", "气短"], "herbs": ["黄芪", "白术", "防风"]},
    "酸枣仁汤": {"symptoms": ["失眠", "心悸", "头晕", "盗汗"], "herbs": ["酸枣仁", "茯苓", "知母", "川芎", "甘草"]},
    "天王补心丹": {"symptoms": ["心悸", "失眠", "健忘", "口干"], "herbs": ["人参", "玄参", "丹参", "茯苓", "远志", "桔梗", "当归", "五味子", "麦冬", "天冬", "柏子仁", "酸枣仁"]},
    "血府逐瘀汤": {"symptoms": ["头痛", "胸痛", "失眠", "心悸"], "herbs": ["桃仁", "红花", "当归", "生地黄", "川芎", "赤芍", "牛膝", "桔梗", "柴胡", "枳壳", "甘草"]},
    "半夏泻心汤": {"symptoms": ["腹胀", "恶心", "呕吐", "腹泻"], "herbs": ["半夏", "黄芩", "干姜", "人参", "黄连", "大枣", "甘草"]},
}

HERB_PAIRS = [
    ("人参", "白术"), ("人参", "茯苓"), ("白术", "茯苓"),
    ("当归", "白芍"), ("当归", "川芎"), ("白芍", "川芎"),
    ("柴胡", "黄芩"), ("半夏", "陈皮"), ("麻黄", "桂枝"),
    ("金银花", "连翘"), ("熟地黄", "山茱萸"), ("黄芪", "当归"),
    ("附子", "干姜"), ("麦冬", "五味子"), ("酸枣仁", "远志"),
    ("苍术", "厚朴"), ("桃仁", "红花"), ("丹参", "当归"),
]


def augment_data(base_data, symptom_vocab, herb_vocab, factor=5):
    augmented = list(base_data)
    
    for formula_name, formula_info in CLASSIC_FORMULAS.items():
        symptoms = [s for s in formula_info["symptoms"] if s in symptom_vocab]
        herbs = [h for h in formula_info["herbs"] if h in herb_vocab]
        
        if len(symptoms) >= 2 and len(herbs) >= 2:
            for _ in range(factor * 2):
                aug_herbs = [{'name': h, 'dosage': random.choice([6, 9, 12, 15])} for h in herbs]
                augmented.append({
                    'symptoms': symptoms,
                    'herbs': aug_herbs,
                    'source': f'classic_{formula_name}',
                    'formula_name': formula_name,
                    'is_classic': True,
                })
    
    for item in base_data:
        for _ in range(factor - 1):
            new_herbs = [{'name': h['name'], 'dosage': h.get('dosage', 9.0)} for h in item['herbs']]
            
            herb_names = [h['name'] for h in new_herbs]
            for h1, h2 in HERB_PAIRS:
                if h1 in herb_names and h2 not in herb_names and h2 in herb_vocab:
                    if random.random() < 0.3:
                        new_herbs.append({'name': h2, 'dosage': 9.0})
            
            augmented.append({
                'symptoms': list(item['symptoms']),
                'herbs': new_herbs,
                'source': item.get('source', '') + '_aug',
                'formula_name': item.get('formula_name', ''),
                'is_classic': item.get('is_classic', False),
            })
    
    return augmented


class LabelSpecificAttention(nn.Module):
    def __init__(self, hidden_dim, label_dim):
        super().__init__()
        self.label_query = nn.Parameter(torch.randn(1, label_dim) * 0.02)
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim + label_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1),
        )
    
    def forward(self, x, label_embed):
        batch_size, num_labels, label_dim = label_embed.shape
        
        x_expanded = x.unsqueeze(1).expand(-1, num_labels, -1)
        combined = torch.cat([x_expanded, label_embed], dim=-1)
        
        attention_weights = self.attention(combined).squeeze(-1)
        attention_weights = F.softmax(attention_weights, dim=-1)
        
        label_specific = torch.einsum('bl,bld->bld', attention_weights, x_expanded)
        return label_specific


class LSANPlus(nn.Module):
    def __init__(
        self,
        num_symptoms,
        num_herbs,
        embed_dim=256,
        hidden_dim=512,
        label_dim=128,
        dropout=0.3,
        max_herbs=20,
    ):
        super().__init__()
        
        self.num_herbs = num_herbs
        self.max_herbs = max_herbs
        
        self.symptom_embed = nn.Sequential(
            nn.Linear(num_symptoms, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        
        self.encoder = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
        )
        
        self.label_embed = nn.Parameter(torch.randn(num_herbs, label_dim) * 0.02)
        
        self.label_attention = LabelSpecificAttention(hidden_dim, label_dim)
        
        self.label_correlation = nn.MultiheadAttention(hidden_dim, num_heads=8, batch_first=True, dropout=dropout)
        
        self.herb_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
        )
        
        self.global_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_herbs),
        )
        
        self.count_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, max_herbs),
        )
        
        self.dosage_head = nn.Sequential(
            nn.Linear(hidden_dim + num_herbs, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, num_herbs),
        )
    
    def forward(self, symptoms):
        batch_size = symptoms.size(0)
        
        symptom_embed = self.symptom_embed(symptoms)
        encoded = self.encoder(symptom_embed)
        
        label_embed_expanded = self.label_embed.unsqueeze(0).expand(batch_size, -1, -1)
        
        label_specific = self.label_attention(encoded, label_embed_expanded)
        
        label_corr, _ = self.label_correlation(label_specific, label_specific, label_specific)
        label_specific = label_specific + label_corr
        
        label_logits = self.herb_head(label_specific).squeeze(-1)
        
        global_logits = self.global_head(encoded)
        
        herb_logits = label_logits + global_logits
        
        count_logits = self.count_head(encoded)
        
        herb_probs = torch.sigmoid(herb_logits).detach()
        dosage_input = torch.cat([encoded, herb_probs], dim=-1)
        dosage_pred = self.dosage_head(dosage_input)
        
        return herb_logits, count_logits, dosage_pred
    
    def predict(self, symptoms, min_herbs=5, max_herbs=12):
        self.eval()
        with torch.no_grad():
            herb_logits, count_logits, dosage_pred = self.forward(symptoms)
            herb_probs = torch.sigmoid(herb_logits)
            
            predicted_count = torch.argmax(count_logits, dim=-1)[0].item() + 1
            predicted_count = max(min_herbs, min(max_herbs, predicted_count))
            
            top_k_indices = torch.topk(herb_probs[0], predicted_count).indices
            herb_selected = torch.zeros_like(herb_probs[0])
            herb_selected[top_k_indices] = 1
            
            return {
                'herb_probs': herb_probs,
                'herb_selected': herb_selected.unsqueeze(0),
                'predicted_count': predicted_count,
                'dosages': dosage_pred[0],
            }


class AsymmetricLoss(nn.Module):
    def __init__(self, alpha_fp=0.15, alpha_fn=0.85, gamma=2.0):
        super().__init__()
        self.alpha_fp = alpha_fp
        self.alpha_fn = alpha_fn
        self.gamma = gamma
    
    def forward(self, logits, targets):
        probs = torch.sigmoid(logits).clamp(min=1e-6, max=1-1e-6)
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        pt = torch.where(targets == 1, probs, 1 - probs)
        focal = (1 - pt) ** self.gamma
        
        fn_mask = (targets == 1).float()
        fp_mask = (targets == 0).float()
        weight = self.alpha_fn * fn_mask + self.alpha_fp * fp_mask
        
        return (weight * focal * bce).mean()


class CombinedLoss(nn.Module):
    def __init__(self, alpha_fp=0.15, alpha_fn=0.85):
        super().__init__()
        self.focal = AsymmetricLoss(alpha_fp, alpha_fn)
    
    def forward(self, herb_logits, count_logits, dosage_pred, herb_target, dosage_target):
        focal_loss = self.focal(herb_logits, herb_target)
        
        probs = torch.sigmoid(herb_logits).clamp(min=1e-6, max=1-1e-6)
        intersection = (probs * herb_target).sum(dim=1)
        cardinality = probs.sum(dim=1) + herb_target.sum(dim=1)
        dice_loss = (1 - (2 * intersection + 1) / (cardinality + 1)).mean()
        
        target_count = herb_target.sum(dim=1)
        target_class = torch.clamp(target_count.long() - 1, min=0, max=19)
        count_loss = F.cross_entropy(count_logits, target_class)
        
        mask = herb_target > 0
        dosage_loss = F.mse_loss(dosage_pred[mask], dosage_target[mask].clamp(0.5, 50)) if mask.any() else torch.tensor(0.0, device=herb_logits.device)
        
        total = 0.3 * focal_loss + 0.35 * dice_loss + 0.25 * count_loss + 0.1 * dosage_loss
        
        return total, {'focal': focal_loss.item(), 'dice': dice_loss.item(), 'count': count_loss.item()}


def compute_metrics(herb_probs, herb_target, threshold=0.5):
    pred = (herb_probs > threshold).float()
    tp = (pred * herb_target).sum(dim=1)
    fp = (pred * (1 - herb_target)).sum(dim=1)
    fn = ((1 - pred) * herb_target).sum(dim=1)
    p = (tp / (tp + fp).clamp(min=1)).mean()
    r = (tp / (tp + fn).clamp(min=1)).mean()
    f1 = 2 * p * r / (p + r + 1e-8)
    return {
        'precision': p.item(),
        'recall': r.item(),
        'f1': f1.item(),
        'over': fp.mean().item(),
        'under': fn.mean().item(),
        'pred_count': pred.sum(dim=1).float().mean().item(),
        'target_count': herb_target.sum(dim=1).float().mean().item(),
    }


class TCMDataset(Dataset):
    def __init__(self, data, symptom_vocab, herb_vocab):
        self.data = data
        self.symptom_vocab = symptom_vocab
        self.herb_vocab = herb_vocab
        self.num_symptoms = len(symptom_vocab)
        self.num_herbs = len(herb_vocab)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        symptom_vec = torch.zeros(self.num_symptoms)
        for s in item['symptoms']:
            if s in self.symptom_vocab:
                symptom_vec[self.symptom_vocab[s]] = 1.0
        herb_target = torch.zeros(self.num_herbs)
        dosage_target = torch.zeros(self.num_herbs)
        for h in item['herbs']:
            name = h['name']
            dosage = h.get('dosage', 9.0)
            if isinstance(dosage, str):
                try:
                    dosage = float(dosage.replace('g', ''))
                except:
                    dosage = 9.0
            if name in self.herb_vocab:
                herb_target[self.herb_vocab[name]] = 1.0
                dosage_target[self.herb_vocab[name]] = dosage
        return {'symptoms': symptom_vec, 'herb_target': herb_target, 'dosage_target': dosage_target}


def train_epoch(model, loader, criterion, optimizer, device, scaler):
    model.train()
    total_loss = 0
    metrics = defaultdict(float)
    n = 0
    for batch in loader:
        symptoms = batch['symptoms'].to(device)
        herb_target = batch['herb_target'].to(device)
        dosage_target = batch['dosage_target'].to(device)
        optimizer.zero_grad()
        if scaler:
            with torch.amp.autocast('cuda'):
                herb_logits, count_logits, dosage_pred = model(symptoms)
                loss, _ = criterion(herb_logits, count_logits, dosage_pred, herb_target, dosage_target)
            if loss is not None and not torch.isnan(loss).any():
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
        else:
            herb_logits, count_logits, dosage_pred = model(symptoms)
            loss, _ = criterion(herb_logits, count_logits, dosage_pred, herb_target, dosage_target)
            if loss is not None and not torch.isnan(loss).any():
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
        if loss is not None and not torch.isnan(loss).any():
            total_loss += loss.item()
            with torch.no_grad():
                probs = torch.sigmoid(herb_logits.float())
                m = compute_metrics(probs, herb_target)
                for k, v in m.items():
                    metrics[k] += v * symptoms.size(0)
            n += symptoms.size(0)
    return total_loss / max(len(loader), 1), {k: v/max(n,1) for k,v in metrics.items()}


@torch.no_grad()
def validate(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    metrics = defaultdict(float)
    n = 0
    for batch in loader:
        symptoms = batch['symptoms'].to(device)
        herb_target = batch['herb_target'].to(device)
        dosage_target = batch['dosage_target'].to(device)
        herb_logits, count_logits, dosage_pred = model(symptoms)
        loss, _ = criterion(herb_logits, count_logits, dosage_pred, herb_target, dosage_target)
        total_loss += loss.item()
        probs = torch.sigmoid(herb_logits)
        m = compute_metrics(probs, herb_target)
        for k, v in m.items():
            metrics[k] += v * symptoms.size(0)
        n += symptoms.size(0)
    return {'loss': total_loss / max(len(loader), 1), **{k: v/max(n,1) for k,v in metrics.items()}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='data')
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints')
    parser.add_argument('--epochs', type=int, default=500)
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--patience', type=int, default=100)
    parser.add_argument('--augment', type=int, default=5)
    args = parser.parse_args()
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    print('=' * 70)
    print('  TCM Formula Recommendation - LSAN Model')
    print('  Label-Specific Attention Network with Label Correlation')
    print('=' * 70)
    print(f'  Device: {device}, Augment: {args.augment}x')
    print(f'  Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 70)
    
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    
    with open(os.path.join(args.data_dir, 'meta.json'), 'r', encoding='utf-8') as f:
        meta = json.load(f)
    with open(os.path.join(args.data_dir, 'symptom_vocab.json'), 'r', encoding='utf-8') as f:
        symptom_vocab = json.load(f)
    with open(os.path.join(args.data_dir, 'herb_vocab.json'), 'r', encoding='utf-8') as f:
        herb_vocab = json.load(f)
    with open(os.path.join(args.data_dir, 'train_data.json'), 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    with open(os.path.join(args.data_dir, 'val_data.json'), 'r', encoding='utf-8') as f:
        val_data = json.load(f)
    
    print(f'\nOriginal: {len(train_data)} train, {len(val_data)} val')
    
    random.seed(42)
    train_data = augment_data(train_data, symptom_vocab, herb_vocab, args.augment)
    random.shuffle(train_data)
    
    print(f'Augmented: {len(train_data)} train')
    
    train_set = TCMDataset(train_data, symptom_vocab, herb_vocab)
    val_set = TCMDataset(val_data, symptom_vocab, herb_vocab)
    
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, pin_memory=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size, pin_memory=True)
    
    model = LSANPlus(len(symptom_vocab), len(herb_vocab)).to(device)
    print(f'\nModel params: {sum(p.numel() for p in model.parameters()):,}')
    
    criterion = CombinedLoss(alpha_fp=0.15, alpha_fn=0.85)
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=0.05)
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=30, T_mult=2, eta_min=1e-6)
    scaler = torch.amp.GradScaler('cuda') if device.type == 'cuda' else None
    
    best_f1 = 0
    patience_counter = 0
    
    print('\nTraining...')
    print('-' * 70)
    
    for epoch in range(args.epochs):
        t0 = time.time()
        train_loss, train_m = train_epoch(model, train_loader, criterion, optimizer, device, scaler)
        scheduler.step()
        val_m = validate(model, val_loader, criterion, device)
        elapsed = time.time() - t0
        
        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f'Epoch {epoch+1:4d}/{args.epochs} | Loss: {train_loss:.4f} | P: {val_m["precision"]:.3f} | R: {val_m["recall"]:.3f} | F1: {val_m["f1"]:.3f} | Over: {val_m["over"]:.2f} | Under: {val_m["under"]:.2f} | {elapsed:.1f}s')
        
        if val_m['f1'] > best_f1:
            best_f1 = val_m['f1']
            patience_counter = 0
            torch.save({'model_state_dict': model.state_dict(), 'best_f1': best_f1, 'val_metrics': val_m, 'symptom_vocab': symptom_vocab, 'herb_vocab': herb_vocab}, os.path.join(args.checkpoint_dir, 'best_model.pt'))
            print(f'   ★ New best F1: {best_f1:.4f}')
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                print(f'\nEarly stopping at epoch {epoch+1}')
                break
    
    print('-' * 70)
    print(f'Best F1: {best_f1:.4f}')
    
    ckpt = torch.load(os.path.join(args.checkpoint_dir, 'best_model.pt'), weights_only=False)
    model.load_state_dict(ckpt['model_state_dict'])
    final = validate(model, val_loader, criterion, device)
    print(f'\nFinal: P={final["precision"]:.4f}, R={final["recall"]:.4f}, F1={final["f1"]:.4f}')


if __name__ == '__main__':
    main()
