# 中医AI方剂推荐 — 深度学习训练模块

## 环境要求

- Python 3.10+
- PyTorch 2.0+ (CUDA 12.x for GPU training)
- NVIDIA GPU (推荐 RTX 5090)

## 快速开始

### 1. 安装依赖

```bash
cd training
pip install -r requirements.txt
```

### 2. 准备数据

训练数据来自 `src/data/` 目录下的中药知识库 JSON 文件。运行以下脚本将其转换为训练格式：

```bash
python scripts/prepare_data.py
```

这会在 `training/data/` 下生成：
- `herb_vocab.json` — 药材词表
- `symptom_vocab.json` — 症状/证候词表
- `train_data.json` — 训练数据集
- `val_data.json` — 验证数据集

### 3. 开始训练

```bash
# GPU 训练（推荐）
python scripts/train.py --device cuda --epochs 200 --batch_size 32 --lr 0.001

# CPU 训练（测试用）
python scripts/train.py --device cpu --epochs 10 --batch_size 8
```

### 4. 评估模型

```bash
python scripts/evaluate.py --checkpoint checkpoints/best_model.pt
```

### 5. 导出为 API 可用模型

```bash
python scripts/export_model.py --checkpoint checkpoints/best_model.pt --output models/tcm_model.pt
```

## 模型架构

```
症状标签 (multi-hot) → Embedding → Transformer Encoder → 方剂分类头
                                                       → 药材预测头
                                                       → 剂量回归头
```

### TCMFormulaNet

- **输入层**: 症状/证候的 multi-hot 编码向量
- **症状嵌入层**: 将离散症状映射到连续向量空间
- **Transformer Encoder**: 学习症状之间的复杂关系（自注意力机制）
- **方剂分类头**: 预测最匹配的经典方剂
- **药材预测头**: 预测处方中应包含的药材组合
- **剂量回归头**: 预测每味药的推荐剂量

### 训练策略

1. **多任务学习**: 同时优化方剂分类、药材预测和剂量回归
2. **数据增强**: 对症状组合进行随机dropout模拟不完整问诊
3. **课程学习**: 先学简单的单一证候，逐步增加复杂组合
4. **知识蒸馏**: 利用规则引擎的输出作为软标签辅助训练

## 目录结构

```
training/
├── README.md           # 本说明文件
├── requirements.txt    # Python 依赖
├── scripts/
│   ├── prepare_data.py # 数据预处理
│   ├── train.py        # 训练脚本
│   ├── evaluate.py     # 评估脚本
│   └── export_model.py # 模型导出
├── models/
│   ├── tcm_net.py      # 模型定义
│   └── dataset.py      # 数据集类
├── data/               # 处理后的训练数据
├── checkpoints/        # 模型检查点
└── logs/               # 训练日志
```

## 后续扩展

- [ ] 从互联网爬取更多方剂数据扩充训练集
- [ ] 加入图像识别分支（舌象/面色识别）
- [ ] 使用预训练中文医学BERT增强语义理解
- [ ] 对接 Next.js 前端 API
