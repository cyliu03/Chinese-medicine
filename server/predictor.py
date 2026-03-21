"""
TCM Formula Predictor

Uses LSAN model for formula recommendation
Supports both classic formula model and ChatMed model
"""

import os
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
    
    def forward(self, H):
        batch_size, seq_len, hidden_dim = H.shape
        label_query = self.label_query.expand(batch_size, -1)
        label_query_expanded = label_query.unsqueeze(1).expand(-1, seq_len, -1)
        combined = torch.cat([H, label_query_expanded], dim=-1)
        attention_weights = self.attention(combined).squeeze(-1)
        attention_weights = F.softmax(attention_weights, dim=-1)
        context = torch.bmm(attention_weights.unsqueeze(1), H).squeeze(1)
        return context


class LSANPlus(nn.Module):
    def __init__(self, num_symptoms, num_herbs, embed_dim=256, hidden_dim=512, num_heads=8, dropout=0.3):
        super().__init__()
        self.symptom_embedding = nn.Embedding(num_symptoms, embed_dim)
        self.herb_embedding = nn.Embedding(num_herbs, embed_dim)
        
        self.symptom_encoder = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
        )
        
        self.label_attention = LabelSpecificAttention(hidden_dim, embed_dim)
        
        self.multihead_attention = nn.MultiheadAttention(hidden_dim, num_heads, dropout=dropout, batch_first=True)
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_herbs),
        )
        
        self.herb_query = nn.Parameter(torch.randn(1, num_herbs, hidden_dim) * 0.02)
        
    def forward(self, symptom_ids):
        batch_size = symptom_ids.size(0)
        
        symptom_embeds = self.symptom_embedding(symptom_ids)
        H = self.symptom_encoder(symptom_embeds)
        
        label_context = self.label_attention(H)
        
        herb_query = self.herb_query.expand(batch_size, -1, -1)
        attn_output, _ = self.multihead_attention(herb_query, H, H)
        attn_output = attn_output.mean(dim=1)
        
        combined = torch.cat([label_context, attn_output], dim=-1)
        logits = self.classifier(combined)
        
        return logits


class TCMFormulaPredictor:
    def __init__(self, model_path, vocab_dir, device="cuda"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        
        meta_path = os.path.join(vocab_dir, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            self.symptom_vocab = meta.get("symptom2idx", {})
            self.herb_vocab = meta.get("herb2idx", {})
            self.use_chatmed = True
        else:
            with open(os.path.join(vocab_dir, "symptom_vocab.json"), "r", encoding="utf-8") as f:
                self.symptom_vocab = json.load(f)
            with open(os.path.join(vocab_dir, "herb_vocab.json"), "r", encoding="utf-8") as f:
                self.herb_vocab = json.load(f)
            self.use_chatmed = False
        
        self.idx_to_herb = {v: k for k, v in self.herb_vocab.items()}
        
        num_symptoms = len(self.symptom_vocab)
        num_herbs = len(self.herb_vocab)
        
        self.model = LSANPlus(num_symptoms, num_herbs)
        
        ckpt = torch.load(model_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(ckpt['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        print(f"LSAN Predictor loaded (ChatMed: {self.use_chatmed})")
        print(f"  Best F1: {ckpt.get('best_f1', 0):.4f}")
        print(f"  Symptoms: {num_symptoms}, Herbs: {num_herbs}")
    
    def predict(self, symptoms, threshold=0.3, min_herbs=3, max_herbs=12):
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        
        valid_symptoms = []
        symptom_ids = []
        
        for s in symptoms:
            s_clean = s.strip()
            if s_clean in self.symptom_vocab:
                symptom_ids.append(self.symptom_vocab[s_clean])
                valid_symptoms.append(s_clean)
        
        if not symptom_ids:
            return {
                "herbs": [],
                "predicted_count": 0,
                "valid_symptoms": [],
                "error": "No valid symptoms found"
            }
        
        max_symptoms = 20
        symptom_tensor = torch.zeros(max_symptoms, dtype=torch.long)
        symptom_tensor[:len(symptom_ids)] = torch.tensor(symptom_ids[:max_symptoms])
        symptom_tensor = symptom_tensor.unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            logits = self.model(symptom_tensor)
            herb_probs = torch.sigmoid(logits[0])
        
        above_threshold = (herb_probs > threshold).nonzero().squeeze(-1)
        
        if len(above_threshold) < min_herbs:
            top_k_indices = torch.topk(herb_probs, min_herbs).indices
        elif len(above_threshold) > max_herbs:
            top_k_indices = torch.topk(herb_probs, max_herbs).indices
        else:
            top_k_indices = above_threshold
        
        herbs = []
        for idx in top_k_indices:
            idx_item = idx.item()
            herb_name = self.idx_to_herb.get(idx_item, f"unknown_{idx_item}")
            prob = herb_probs[idx_item].item()
            if prob > threshold or len(herbs) < min_herbs:
                dosage = max(3, min(15, 6 + prob * 6))
                herbs.append({
                    "name": herb_name,
                    "probability": prob,
                    "dosage": f"{dosage:.1f}g"
                })
        
        herbs.sort(key=lambda x: x["probability"], reverse=True)
        
        return {
            "herbs": herbs[:max_herbs],
            "predicted_count": len(herbs[:max_herbs]),
            "valid_symptoms": valid_symptoms,
        }
    
    def predict_simple(self, symptoms):
        result = self.predict(symptoms)
        return [h["name"] for h in result["herbs"]]
