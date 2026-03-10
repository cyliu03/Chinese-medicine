"""
TCMFormulaNet — 中医方剂推荐深度学习模型

多任务学习架构:
  症状输入 → Embedding → Transformer Encoder → 方剂分类 + 药材预测 + 剂量回归
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class SymptomEmbedding(nn.Module):
    """症状嵌入层：将 multi-hot 症状向量映射到连续向量空间"""

    def __init__(self, num_symptoms, embed_dim, dropout=0.1):
        super().__init__()
        self.embedding = nn.Linear(num_symptoms, embed_dim)
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # x: (batch, num_symptoms) multi-hot vector
        out = self.embedding(x)
        out = self.layer_norm(out)
        out = F.gelu(out)
        out = self.dropout(out)
        return out


class TransformerBlock(nn.Module):
    """Transformer Encoder Block with self-attention"""

    def __init__(self, d_model, nhead, dim_feedforward, dropout=0.1):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout, batch_first=True)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, dim_feedforward),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim_feedforward, d_model),
            nn.Dropout(dropout),
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # Self attention
        attn_out, _ = self.self_attn(x, x, x)
        x = self.norm1(x + self.dropout(attn_out))
        # Feed forward
        ff_out = self.feed_forward(x)
        x = self.norm2(x + ff_out)
        return x


class TCMFormulaNet(nn.Module):
    """
    中医方剂推荐神经网络

    多任务学习:
      - Task 1: 方剂分类 (从知识库中选择最匹配的经典方剂)
      - Task 2: 药材预测 (预测处方中应包含哪些药材, multi-label)
      - Task 3: 剂量回归 (预测每味药的推荐剂量)
    """

    def __init__(
        self,
        num_symptoms,
        num_formulas,
        num_herbs,
        embed_dim=256,
        num_heads=8,
        num_layers=4,
        dim_feedforward=512,
        dropout=0.1,
    ):
        super().__init__()

        self.num_symptoms = num_symptoms
        self.num_formulas = num_formulas
        self.num_herbs = num_herbs
        self.embed_dim = embed_dim

        # 症状嵌入
        self.symptom_embed = SymptomEmbedding(num_symptoms, embed_dim, dropout)

        # 将嵌入展开为序列 (用于Transformer)
        # 使用可学习的 position tokens
        self.num_tokens = 8  # 将症状信息分散到8个token中
        self.token_proj = nn.Linear(embed_dim, self.num_tokens * embed_dim)
        self.pos_embed = nn.Parameter(torch.randn(1, self.num_tokens, embed_dim) * 0.02)

        # Transformer Encoder
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, dim_feedforward, dropout)
            for _ in range(num_layers)
        ])

        # 全局池化后的表示
        self.pool_norm = nn.LayerNorm(embed_dim)

        # Task 1: 方剂分类头
        self.formula_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim // 2, num_formulas),
        )

        # Task 2: 药材预测头 (multi-label sigmoid)
        self.herb_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim, num_herbs),
        )

        # Task 3: 剂量回归头
        self.dosage_head = nn.Sequential(
            nn.Linear(embed_dim + num_herbs, embed_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim // 2, num_herbs),
            nn.ReLU(),  # 剂量不能为负
        )

        self._init_weights()

    def _init_weights(self):
        """Xavier初始化"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, symptoms):
        """
        Args:
            symptoms: (batch, num_symptoms) multi-hot 症状向量

        Returns:
            formula_logits: (batch, num_formulas) 方剂分类 logits
            herb_logits: (batch, num_herbs) 药材预测 logits
            dosage_pred: (batch, num_herbs) 剂量预测 (克)
        """
        batch_size = symptoms.size(0)

        # 1. 症状嵌入
        embed = self.symptom_embed(symptoms)  # (batch, embed_dim)

        # 2. 展开为token序列
        tokens = self.token_proj(embed)  # (batch, num_tokens * embed_dim)
        tokens = tokens.view(batch_size, self.num_tokens, self.embed_dim)
        tokens = tokens + self.pos_embed

        # 3. Transformer编码
        for block in self.transformer_blocks:
            tokens = block(tokens)

        # 4. 全局平均池化
        pooled = tokens.mean(dim=1)  # (batch, embed_dim)
        pooled = self.pool_norm(pooled)

        # 5. 多任务输出
        formula_logits = self.formula_head(pooled)
        herb_logits = self.herb_head(pooled)

        # 剂量预测需要知道哪些药材被选中
        herb_probs = torch.sigmoid(herb_logits).detach()
        dosage_input = torch.cat([pooled, herb_probs], dim=-1)
        dosage_pred = self.dosage_head(dosage_input)

        return formula_logits, herb_logits, dosage_pred

    def predict(self, symptoms, top_k=3):
        """
        推理模式：给定症状，返回top_k方剂推荐

        Returns:
            formula_indices: top_k 方剂索引
            formula_probs: top_k 方剂概率
            herb_indices: 预测的药材索引列表
            herb_probs: 药材概率
            dosages: 预测剂量
        """
        self.eval()
        with torch.no_grad():
            formula_logits, herb_logits, dosage_pred = self.forward(symptoms)

            # 方剂 Top-K
            formula_probs = F.softmax(formula_logits, dim=-1)
            top_probs, top_indices = torch.topk(formula_probs, k=min(top_k, self.num_formulas), dim=-1)

            # 药材预测 (概率 > 0.5 的被选中)
            herb_probs = torch.sigmoid(herb_logits)
            herb_selected = (herb_probs > 0.5).long()

            return {
                'formula_indices': top_indices,
                'formula_probs': top_probs,
                'herb_selected': herb_selected,
                'herb_probs': herb_probs,
                'dosages': dosage_pred,
            }


class MultiTaskLoss(nn.Module):
    """
    多任务学习损失函数

    自动平衡三个任务的损失权重 (Uncertainty Weighting)
    """

    def __init__(self):
        super().__init__()
        # 可学习的任务权重 (log variance)
        self.log_var_formula = nn.Parameter(torch.zeros(1))
        self.log_var_herb = nn.Parameter(torch.zeros(1))
        self.log_var_dosage = nn.Parameter(torch.zeros(1))

    def forward(self, formula_logits, herb_logits, dosage_pred,
                formula_target, herb_target, dosage_target):
        """
        Args:
            formula_logits: (batch, num_formulas)
            herb_logits: (batch, num_herbs)
            dosage_pred: (batch, num_herbs)
            formula_target: (batch,) 方剂类别索引
            herb_target: (batch, num_herbs) multi-hot
            dosage_target: (batch, num_herbs) 剂量标签 (克)
        """
        # Task 1: 方剂分类 — Cross Entropy
        loss_formula = F.cross_entropy(formula_logits, formula_target)

        # Task 2: 药材预测 — Binary Cross Entropy
        loss_herb = F.binary_cross_entropy_with_logits(herb_logits, herb_target)

        # Task 3: 剂量回归 — MSE (只在有药材的位置计算)
        mask = herb_target > 0
        if mask.any():
            loss_dosage = F.mse_loss(dosage_pred[mask], dosage_target[mask])
        else:
            loss_dosage = torch.tensor(0.0, device=formula_logits.device)

        # 不确定性加权 (Kendall et al., 2018)
        precision_formula = torch.exp(-self.log_var_formula)
        precision_herb = torch.exp(-self.log_var_herb)
        precision_dosage = torch.exp(-self.log_var_dosage)

        total_loss = (
            precision_formula * loss_formula + self.log_var_formula +
            precision_herb * loss_herb + self.log_var_herb +
            precision_dosage * loss_dosage + self.log_var_dosage
        )

        return total_loss, {
            'loss_formula': loss_formula.item(),
            'loss_herb': loss_herb.item(),
            'loss_dosage': loss_dosage.item(),
            'total_loss': total_loss.item(),
        }
