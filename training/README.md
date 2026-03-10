# 中医AI方剂推荐 — 深度学习训练模块

## 环境要求

- Python 3.10+
- PyTorch 2.0+ (CUDA 13.0 for RTX 5090)
- NVIDIA GPU (推荐 RTX 5090, 32GB VRAM)

## 数据来源

### PTM 处方数据集 (主要数据源)

| 项目 | 详情 |
|------|------|
| **名称** | PTM (Prescription Topic Model) |
| **论文** | Liang Yao et al., IEEE TKDE 2018 |
| **仓库** | [yao8839836/PTM](https://github.com/yao8839836/PTM) |
| **数据量** | 98,334 原始中医处方 (预处理后 33,765 条) |
| **内容** | 症状描述 → 药材组成 + 剂量 |
| **来源** | 中国工程科学知识中心 (CKCEST) |
| **许可** | ⚠️ **仅限研究用途**，禁止商业使用 |

### 经典方剂知识库 (项目自带)

| 项目 | 详情 |
|------|------|
| **位置** | `src/data/formulas.json`, `herbs.json`, `symptoms.json` |
| **方剂** | 45 个经典方剂 (伤寒论/金匮/温病条辨等) |
| **药材** | 120 味常用中药 |
| **特点** | 结构化数据，含 symptomTags、证候、剂量、加减法 |

### 合并数据集统计

| 指标 | 数量 |
|------|------|
| 总处方数 | ~97,500+ (清洗后保留 ~257,000 高质量增强样本) |
| 核心药材种类 | ~4,400 (过滤低频) |
| 核心症状标签 | ~3,300 (过滤低频) |
| 训练数据 | 218,451 条 |
| 验证数据 | 38,550 条 |

## 快速开始

### 1. 安装依赖

```bash
cd training

# 安装 PyTorch (CUDA 13.0, RTX 5090)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# 安装其他依赖
pip install -r requirements.txt
```

### 2. 下载数据集

```bash
# 从 GitHub 下载 PTM 数据集并转换为 JSON 格式
python scripts/download_dataset.py
```

这会下载并处理：
- PTM 98K 原始处方 → `data/raw/ptm_prescriptions.json`
- 合并经典方剂 → `data/raw/merged_prescriptions.json`
- 药材/症状词表 → `data/raw/all_herbs.json`, `all_symptoms.json`

### 3. 预处理训练数据

```bash
# 使用大规模数据集 (PTM + 经典方剂)
python scripts/prepare_data.py --use_raw

# 或仅使用项目自带的 45 个经典方剂
python scripts/prepare_data.py
```

### 4. 开始训练

```bash
# RTX 5090 推荐参数
python scripts/train.py \
    --device cuda \
    --epochs 200 \
    --batch_size 64 \
    --lr 0.0005 \
    --embed_dim 512 \
    --num_layers 6 \
    --dim_feedforward 1024

# CPU 快速测试
python scripts/train.py --device cpu --epochs 10 --batch_size 8
```

### 5. 评估模型

```bash
python scripts/evaluate.py --checkpoint checkpoints/best_model.pt
```

### 6. 导出为 API 可用模型

```bash
python scripts/export_model.py --checkpoint checkpoints/best_model.pt --output models/tcm_model.pt
```

## 模型架构

```
症状标签 (multi-hot) → Embedding → Transformer Encoder → 药材预测头 (Multi-label)
                                                       → 剂量回归头 (Log Scale)
```

### TCMFormulaNet

- **输入层**: 症状/证候的 multi-hot 编码向量
- **症状嵌入层**: 将离散症状映射到连续向量空间
- **Transformer Encoder**: 学习症状之间的复杂关系（自注意力机制）
- **药材预测头**: 多标签二分类 (BCE Loss)，预测处方中应包含哪些核心药材
- **剂量回归头**: 预测每味选中药材的推荐剂量 (基于 Log1p 的 MSE Loss 防止梯度爆炸)

### 训练策略

1. **多任务学习**: 同时优化药材组成和用药剂量
2. **知识提纯**: 去除极低频噪声药物和症状，构建核心中医知识库
3. **数据增强**: 对症状组合进行随机dropout模拟不完整问诊
4. **损失平衡**: 使用 Uncertainty Weighting 自动平衡不同任务间的 Loss 权重

## 目录结构

```
training/
├── README.md                # 本说明文件
├── requirements.txt         # Python 依赖
├── scripts/
│   ├── download_dataset.py  # 数据集下载与转换 (PTM 98K)
│   ├── prepare_data.py      # 数据预处理
│   ├── train.py             # 训练脚本
│   ├── evaluate.py          # 评估脚本
│   └── export_model.py      # 模型导出
├── models/
│   ├── tcm_net.py           # 模型定义
│   └── dataset.py           # 数据集类
├── data/
│   ├── raw/                 # 下载的原始数据
│   │   ├── ptm_raw/         # PTM 原始文件
│   │   ├── ptm_prescriptions.json
│   │   ├── merged_prescriptions.json
│   │   └── ...
│   ├── train_data.json      # 训练数据
│   ├── val_data.json        # 验证数据
│   └── *.vocab.json         # 词表
├── checkpoints/             # 模型检查点
└── logs/                    # 训练日志 (TensorBoard)
```

## 引用

如使用 PTM 数据集，请引用：

```bibtex
@article{yao2018topic,
  title={A Topic Modeling Approach for Traditional Chinese Medicine Prescriptions},
  author={Yao, Liang and Zhang, Yin and Wei, Baogang and Zhang, Wenjin and Jin, Zhe},
  journal={IEEE Transactions on Knowledge and Data Engineering},
  volume={30},
  number={6},
  pages={1007--1021},
  year={2018}
}
```

