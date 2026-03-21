"""
中医方剂推荐系统 - 预测测试脚本
"""
import os
import sys
import json
import torch
import torch.nn as nn
import torch.nn.functional as F

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
    def __init__(self, num_symptoms, num_herbs, embed_dim=256, hidden_dim=512, label_dim=128, dropout=0.3, max_herbs=20):
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


def main():
    print("=" * 70)
    print("  中医方剂推荐系统 - 预测测试")
    print("=" * 70)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n设备: {device}")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    checkpoint_path = os.path.join(base_dir, 'checkpoints', 'best_model.pt')
    
    print("\n加载词表...")
    with open(os.path.join(data_dir, 'symptom_vocab.json'), 'r', encoding='utf-8') as f:
        symptom_vocab = json.load(f)
    with open(os.path.join(data_dir, 'herb_vocab.json'), 'r', encoding='utf-8') as f:
        herb_vocab = json.load(f)
    
    idx_to_herb = {v: k for k, v in herb_vocab.items()}
    print(f"  症状词表: {len(symptom_vocab)} 个")
    print(f"  药材词表: {len(herb_vocab)} 味")
    
    print("\n加载模型...")
    model = LSANPlus(len(symptom_vocab), len(herb_vocab))
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    print(f"  最佳F1: {checkpoint.get('best_f1', 0):.4f}")
    
    print("\n" + "-" * 70)
    print("  预测测试")
    print("-" * 70)
    
    test_cases = [
        {
            "name": "麻黄汤证",
            "symptoms": ["恶寒", "发热", "无汗", "头痛", "身痛", "喘"],
            "expected_herbs": ["麻黄", "桂枝", "杏仁", "甘草"]
        },
        {
            "name": "桂枝汤证",
            "symptoms": ["发热", "恶风", "汗出", "头痛"],
            "expected_herbs": ["桂枝", "白芍", "生姜", "大枣", "甘草"]
        },
        {
            "name": "四君子汤证",
            "symptoms": ["气短", "乏力", "面色萎黄", "食欲不振"],
            "expected_herbs": ["人参", "白术", "茯苓", "甘草"]
        },
        {
            "name": "小柴胡汤证",
            "symptoms": ["寒热往来", "胸胁苦满", "口苦", "咽干", "目眩"],
            "expected_herbs": ["柴胡", "黄芩", "人参", "半夏", "生姜", "大枣", "甘草"]
        },
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【案例 {i}】{case['name']}")
        print(f"  症状: {', '.join(case['symptoms'])}")
        print(f"  预期药材: {', '.join(case['expected_herbs'])}")
        
        symptom_vec = torch.zeros(len(symptom_vocab))
        valid_symptoms = []
        for s in case['symptoms']:
            if s in symptom_vocab:
                symptom_vec[symptom_vocab[s]] = 1.0
                valid_symptoms.append(s)
        
        symptom_vec = symptom_vec.unsqueeze(0).to(device)
        
        with torch.no_grad():
            herb_logits, count_logits, dosage_pred = model(symptom_vec)
            herb_probs = torch.sigmoid(herb_logits[0])
            predicted_count = torch.argmax(count_logits[0]).item() + 1
        
        final_count = max(3, min(12, predicted_count))
        top_k_indices = torch.topk(herb_probs, final_count).indices
        
        pred_herbs = []
        for idx in top_k_indices:
            idx_item = idx.item()
            herb_name = idx_to_herb.get(idx_item, f"未知_{idx_item}")
            prob = herb_probs[idx_item].item()
            dosage = dosage_pred[0][idx_item].item()
            pred_herbs.append((herb_name, prob, dosage))
        
        print(f"  预测药材:")
        for herb_name, prob, dosage in pred_herbs:
            match = "✓" if herb_name in case['expected_herbs'] else " "
            print(f"    {match} {herb_name}: {prob:.2%} (剂量: {dosage:.1f}g)")
        
        pred_set = set(h[0] for h in pred_herbs)
        expected_set = set(case['expected_herbs'])
        tp = len(pred_set & expected_set)
        fp = len(pred_set - expected_set)
        fn = len(expected_set - pred_set)
        
        if tp + fp > 0 and tp + fn > 0:
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            print(f"  匹配: 正确={tp}, 多开={fp}, 漏开={fn}, F1={f1:.2f}")
    
    print("\n" + "=" * 70)
    print("  测试完成!")
    print("=" * 70)


if __name__ == '__main__':
    main()
