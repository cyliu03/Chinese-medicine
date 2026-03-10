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
    中医自动开方神经网络 (TCM Doctor Model)

    多任务学习:
      - Task 1: 药材预测 (预测针对这些症状应该开什么药材, multi-label)
      - Task 2: 剂量回归 (预测每味药的推荐剂量)
    """

    def __init__(
        self,
        num_symptoms,
        num_herbs,
        embed_dim=256,
        num_heads=8,
        num_layers=4,
        dim_feedforward=512,
        dropout=0.1,
    ):
        super().__init__()

        self.num_symptoms = num_symptoms
        self.num_herbs = num_herbs
        self.embed_dim = embed_dim

        # 症状嵌入
        self.symptom_embed = SymptomEmbedding(num_symptoms, embed_dim, dropout)

        # 将嵌入展开为序列 (用于Transformer)
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

        # Task 1: 药材预测头 (multi-label sigmoid)
        self.herb_head = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim, num_herbs),
        )

        # Task 2: 剂量回归头
        self.dosage_head = nn.Sequential(
            nn.Linear(embed_dim + num_herbs, embed_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim // 2, num_herbs),
            nn.ReLU(),  # 预测的是 log(1+dosage)，为非负
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
            herb_logits: (batch, num_herbs) 药材预测 logits
            dosage_pred: (batch, num_herbs) 剂量预测 (log scale)
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
        herb_logits = self.herb_head(pooled)

        # 剂量预测需要知道哪些药材被选中
        herb_probs = torch.sigmoid(herb_logits).detach()
        dosage_input = torch.cat([pooled, herb_probs], dim=-1)
        dosage_pred = self.dosage_head(dosage_input)

        return herb_logits, dosage_pred

    def predict(self, symptoms):
        """
        推理模式：给定症状，返回推荐药材和剂量

        Returns:
            herb_selected: 预测的药材索引列表 (multi-hot)
            herb_probs: 药材概率
            dosages: 预测真实剂量(克)
        """
        self.eval()
        with torch.no_grad():
            herb_logits, dosage_pred_log = self.forward(symptoms)

            # 药材预测 (概率 > 0.5 的被选中)
            herb_probs = torch.sigmoid(herb_logits)
            herb_selected = (herb_probs > 0.5).long()

            # 还原真实剂量: exp(x) - 1
            dosages = torch.expm1(dosage_pred_log)

            return {
                'herb_selected': herb_selected,
                'herb_probs': herb_probs,
                'dosages': dosages,
            }


class MultiTaskLoss(nn.Module):
    """
    多任务学习损失函数

    自动平衡两个任务的损失权重 (Uncertainty Weighting)
    """

    def __init__(self):
        super().__init__()
        # 可学习的任务权重 (log variance)
        self.log_var_herb = nn.Parameter(torch.zeros(1))
        self.log_var_dosage = nn.Parameter(torch.zeros(1))

    def forward(self, herb_logits, dosage_pred_log, herb_target, dosage_target):
        """
        Args:
            herb_logits: (batch, num_herbs)
            dosage_pred_log: (batch, num_herbs) log scale
            herb_target: (batch, num_herbs) multi-hot
            dosage_target: (batch, num_herbs) 真实剂量标签 (克)
        """
        # Task 1: 药材预测 — Binary Cross Entropy
        # 针对极度不平衡问题：4400种药材中，每张处方通常只有 10 种左右 (正负比例约 1:400)
        # 为防止模型偷懒全部预测 0，给正样本施加巨大的 loss 权重
        # TODO: 未来可以根据数据集中各药材的真实先验频率做动态平衡
        pos_weight = torch.tensor([400.0], device=herb_logits.device)
        loss_herb = F.binary_cross_entropy_with_logits(
            herb_logits, herb_target, pos_weight=pos_weight
        )

        # Task 2: 剂量回归 — MSE (只在有药材的位置计算, 目标转为 log1p 避免极大Loss)
        mask = herb_target > 0
        if mask.any():
            dosage_target_log = torch.log1p(dosage_target[mask])
            loss_dosage = F.mse_loss(dosage_pred_log[mask], dosage_target_log)
        else:
            loss_dosage = torch.tensor(0.0, device=herb_logits.device)

        # 不确定性加权 (Kendall et al., 2018)
        precision_herb = torch.exp(-self.log_var_herb)
        precision_dosage = torch.exp(-self.log_var_dosage)

        total_loss = (
            precision_herb * loss_herb + self.log_var_herb +
            precision_dosage * loss_dosage + self.log_var_dosage
        )

        return total_loss, {
            'loss_herb': loss_herb.item(),
            'loss_dosage': loss_dosage.item(),
            'total_loss': total_loss.item(),
        }
