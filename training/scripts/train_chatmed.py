import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import json
import os
import numpy as np
from tqdm import tqdm
import random

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

class TCMDataset(Dataset):
    def __init__(self, data, num_symptoms, num_herbs, max_symptoms=20):
        self.data = data
        self.num_symptoms = num_symptoms
        self.num_herbs = num_herbs
        self.max_symptoms = max_symptoms
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        symptom_ids = item['symptom_ids'][:self.max_symptoms]
        
        symptom_tensor = torch.zeros(self.max_symptoms, dtype=torch.long)
        symptom_tensor[:len(symptom_ids)] = torch.tensor(symptom_ids)
        
        herb_label = torch.zeros(self.num_herbs, dtype=torch.float)
        for herb_id in item['herb_ids']:
            herb_label[herb_id] = 1.0
        
        return symptom_tensor, herb_label

class AsymmetricLoss(nn.Module):
    def __init__(self, alpha_fn=0.85, alpha_fp=0.15):
        super().__init__()
        self.alpha_fn = alpha_fn
        self.alpha_fp = alpha_fp
    
    def forward(self, logits, targets):
        probs = torch.sigmoid(logits)
        
        fn_loss = self.alpha_fn * targets * torch.pow(1 - probs, 2) * torch.log(probs + 1e-8)
        fp_loss = self.alpha_fp * (1 - targets) * torch.pow(probs, 2) * torch.log(1 - probs + 1e-8)
        
        loss = -torch.mean(fn_loss + fp_loss)
        return loss

def train_model():
    print("加载ChatMed数据集...")
    
    with open('../../data/chatmed/train_data.json', 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    with open('../../data/chatmed/meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    num_symptoms = meta['num_symptoms']
    num_herbs = meta['num_herbs']
    
    print(f"数据集统计:")
    print(f"  总样本数: {len(all_data)}")
    print(f"  症状种类: {num_symptoms}")
    print(f"  中药种类: {num_herbs}")
    
    random.seed(42)
    random.shuffle(all_data)
    
    train_size = int(len(all_data) * 0.6)
    val_size = int(len(all_data) * 0.2)
    
    train_data = all_data[:train_size]
    val_data = all_data[train_size:train_size + val_size]
    test_data = all_data[train_size + val_size:]
    
    print(f"\n数据划分:")
    print(f"  训练集: {len(train_data)}")
    print(f"  验证集: {len(val_data)}")
    print(f"  测试集: {len(test_data)}")
    
    train_dataset = TCMDataset(train_data, num_symptoms, num_herbs)
    val_dataset = TCMDataset(val_data, num_symptoms, num_herbs)
    test_dataset = TCMDataset(test_data, num_symptoms, num_herbs)
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=0)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n使用设备: {device}")
    
    model = LSANPlus(num_symptoms, num_herbs, embed_dim=256, hidden_dim=512, num_heads=8, dropout=0.3)
    model = model.to(device)
    
    criterion = AsymmetricLoss(alpha_fn=0.85, alpha_fp=0.15)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=20, eta_min=1e-6)
    
    best_f1 = 0
    num_epochs = 20
    
    print("\n开始训练...")
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0
        
        for batch_idx, (symptoms, labels) in enumerate(tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}')):
            symptoms = symptoms.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            logits = model(symptoms)
            loss = criterion(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            train_loss += loss.item()
        
        avg_train_loss = train_loss / len(train_loader)
        
        model.eval()
        val_loss = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for symptoms, labels in val_loader:
                symptoms = symptoms.to(device)
                labels = labels.to(device)
                
                logits = model(symptoms)
                loss = criterion(logits, labels)
                val_loss += loss.item()
                
                preds = (torch.sigmoid(logits) > 0.5).float()
                all_preds.append(preds.cpu().numpy())
                all_labels.append(labels.cpu().numpy())
        
        avg_val_loss = val_loss / len(val_loader)
        
        all_preds = np.vstack(all_preds)
        all_labels = np.vstack(all_labels)
        
        tp = np.sum(all_preds * all_labels)
        fp = np.sum(all_preds * (1 - all_labels))
        fn = np.sum((1 - all_preds) * all_labels)
        
        precision = tp / (tp + fp + 1e-8)
        recall = tp / (tp + fn + 1e-8)
        f1 = 2 * precision * recall / (precision + recall + 1e-8)
        
        print(f'\nEpoch {epoch+1}/{num_epochs}:')
        print(f'  Train Loss: {avg_train_loss:.4f}')
        print(f'  Val Loss: {avg_val_loss:.4f}')
        print(f'  Val Precision: {precision:.4f}')
        print(f'  Val Recall: {recall:.4f}')
        print(f'  Val F1: {f1:.4f}')
        
        scheduler.step()
        
        if f1 > best_f1:
            best_f1 = f1
            os.makedirs('../../checkpoints', exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'f1': f1,
                'num_symptoms': num_symptoms,
                'num_herbs': num_herbs,
            }, '../../checkpoints/best_model.pt')
            print(f'  保存最佳模型 (F1={f1:.4f})')
    
    print("\n在测试集上评估...")
    checkpoint = torch.load('../../checkpoints/best_model.pt', weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for symptoms, labels in test_loader:
            symptoms = symptoms.to(device)
            labels = labels.to(device)
            
            logits = model(symptoms)
            preds = (torch.sigmoid(logits) > 0.5).float()
            all_preds.append(preds.cpu().numpy())
            all_labels.append(labels.cpu().numpy())
    
    all_preds = np.vstack(all_preds)
    all_labels = np.vstack(all_labels)
    
    tp = np.sum(all_preds * all_labels)
    fp = np.sum(all_preds * (1 - all_labels))
    fn = np.sum((1 - all_preds) * all_labels)
    
    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1 = 2 * precision * recall / (precision + recall + 1e-8)
    
    print(f'\n测试集结果:')
    print(f'  Precision: {precision:.4f}')
    print(f'  Recall: {recall:.4f}')
    print(f'  F1 Score: {f1:.4f}')
    
    meta['train_samples'] = len(train_data)
    meta['val_samples'] = len(val_data)
    meta['test_samples'] = len(test_data)
    meta['best_f1'] = float(f1)
    
    with open('../../data/chatmed/meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print("\n训练完成!")

if __name__ == '__main__':
    train_model()
