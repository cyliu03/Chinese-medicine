"""
测试模型在独立测试集上的表现
"""

import os
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import defaultdict


class LSANPlus(torch.nn.Module):
    def __init__(self, num_symptoms, num_herbs, embed_dim=256, hidden_dim=512, label_dim=128, dropout=0.3, max_herbs=20):
        super().__init__()
        self.num_herbs = num_herbs
        self.max_herbs = max_herbs
        
        self.symptom_embed = torch.nn.Sequential(
            torch.nn.Linear(num_symptoms, embed_dim),
            torch.nn.LayerNorm(embed_dim),
            torch.nn.GELU(),
            torch.nn.Dropout(dropout),
        )
        
        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(embed_dim, hidden_dim),
            torch.nn.LayerNorm(hidden_dim),
            torch.nn.GELU(),
            torch.nn.Dropout(dropout),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.LayerNorm(hidden_dim),
            torch.nn.GELU(),
        )
        
        self.label_embed = torch.nn.Parameter(torch.randn(num_herbs, label_dim) * 0.02)
        
        self.label_attention = LabelSpecificAttention(hidden_dim, label_dim)
        self.label_correlation = torch.nn.MultiheadAttention(hidden_dim, num_heads=8, batch_first=True, dropout=dropout)
        
        self.herb_head = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim, hidden_dim // 2),
            torch.nn.GELU(),
            torch.nn.Dropout(dropout),
            torch.nn.Linear(hidden_dim // 2, 1),
        )
        
        self.global_head = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim, hidden_dim // 2),
            torch.nn.GELU(),
            torch.nn.Dropout(dropout),
            torch.nn.Linear(hidden_dim // 2, num_herbs),
        )
        
        self.count_head = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim, hidden_dim // 2),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim // 2, max_herbs),
        )
        
        self.dosage_head = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim + num_herbs, hidden_dim // 2),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim // 2, num_herbs),
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
    
    def predict(self, symptoms, min_herbs=3, max_herbs=12):
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


class LabelSpecificAttention(torch.nn.Module):
    def __init__(self, hidden_dim, label_dim):
        super().__init__()
        self.label_query = torch.nn.Parameter(torch.randn(1, label_dim) * 0.02)
        self.attention = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim + label_dim, hidden_dim // 2),
            torch.nn.Tanh(),
            torch.nn.Linear(hidden_dim // 2, 1),
        )
    
    def forward(self, x, label_embed):
        batch_size, num_labels, label_dim = label_embed.shape
        x_expanded = x.unsqueeze(1).expand(-1, num_labels, -1)
        combined = torch.cat([x_expanded, label_embed], dim=-1)
        attention_weights = self.attention(combined).squeeze(-1)
        attention_weights = F.softmax(attention_weights, dim=-1)
        label_specific = torch.einsum('bl,bld->bld', attention_weights, x_expanded)
        return label_specific


def load_model(checkpoint_path, device):
    checkpoint = torch.load(checkpoint_path, weights_only=False)
    
    symptom_vocab = checkpoint['symptom_vocab']
    herb_vocab = checkpoint['herb_vocab']
    idx_to_herb = {v: k for k, v in herb_vocab.items()}
    
    model = LSANPlus(len(symptom_vocab), len(herb_vocab))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    return model, symptom_vocab, herb_vocab, idx_to_herb


def test_model(model, test_data, symptom_vocab, herb_vocab, idx_to_herb, device):
    results = []
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_pred_count = 0
    total_target_count = 0
    
    for item in test_data:
        symptom_vec = torch.zeros(len(symptom_vocab))
        for s in item['symptoms']:
            if s in symptom_vocab:
                symptom_vec[symptom_vocab[s]] = 1.0
        
        target_herbs = set(h['name'] for h in item['herbs'])
        
        symptom_vec = symptom_vec.unsqueeze(0).to(device)
        result = model.predict(symptom_vec, min_herbs=3, max_herbs=12)
        
        herb_probs = result['herb_probs'][0]
        predicted_count = result['predicted_count']
        
        top_indices = torch.topk(herb_probs, predicted_count).indices
        pred_herbs = set(idx_to_herb[idx.item()] for idx in top_indices)
        
        tp = len(pred_herbs & target_herbs)
        fp = len(pred_herbs - target_herbs)
        fn = len(target_herbs - pred_herbs)
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_pred_count += len(pred_herbs)
        total_target_count += len(target_herbs)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        results.append({
            'formula': item['formula_name'],
            'symptoms': item['symptoms'],
            'target_herbs': sorted(target_herbs),
            'pred_herbs': sorted(pred_herbs),
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'precision': precision,
            'recall': recall,
            'f1': f1,
        })
    
    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0
    
    return results, {
        'precision': overall_precision,
        'recall': overall_recall,
        'f1': overall_f1,
        'avg_pred_count': total_pred_count / len(test_data),
        'avg_target_count': total_target_count / len(test_data),
    }


def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    print("=" * 70)
    print("  TCM Formula Model Test")
    print("=" * 70)
    
    checkpoint_path = 'checkpoints/best_model.pt'
    model, symptom_vocab, herb_vocab, idx_to_herb = load_model(checkpoint_path, device)
    
    print(f"\nModel loaded")
    print(f"  Symptom vocab: {len(symptom_vocab)}")
    print(f"  Herb vocab: {len(herb_vocab)}")
    
    with open('data/test_data.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    print(f"\n测试集: {len(test_data)} 个经典方剂")
    
    results, overall = test_model(model, test_data, symptom_vocab, herb_vocab, idx_to_herb, device)
    
    print("\n" + "-" * 70)
    print("  各方剂测试结果")
    print("-" * 70)
    
    for r in results:
        print(f"\n【{r['formula']}】")
        print(f"  症状: {', '.join(r['symptoms'])}")
        print(f"  目标药材: {', '.join(r['target_herbs'])}")
        print(f"  预测药材: {', '.join(r['pred_herbs'])}")
        print(f"  正确: {r['tp']}, 多开: {r['fp']}, 漏开: {r['fn']}")
        print(f"  P={r['precision']:.2f}, R={r['recall']:.2f}, F1={r['f1']:.2f}")
    
    print("\n" + "=" * 70)
    print("  整体测试结果")
    print("=" * 70)
    print(f"\n  Precision: {overall['precision']:.4f}")
    print(f"  Recall: {overall['recall']:.4f}")
    print(f"  F1 Score: {overall['f1']:.4f}")
    print(f"  平均预测药材数: {overall['avg_pred_count']:.2f}")
    print(f"  平均目标药材数: {overall['avg_target_count']:.2f}")


if __name__ == '__main__':
    main()
