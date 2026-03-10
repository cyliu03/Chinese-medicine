# 🏥 岐黄AI — 中医智能辅助诊疗系统

基于深度学习的中医四诊合参智能系统，通过望闻问切采集患者信息，AI辅助推荐经典方剂，医生审核确保安全有效。

<p align="center">
  <strong>望诊 → 闻诊 → 问诊 → 切诊 → AI分析 → 方剂推荐 → 医生审核</strong>
</p>

---

## ✨ 功能特性

### 🧑‍⚕️ 患者端 — 四诊信息采集

| 诊法 | 功能说明 |
|------|----------|
| **望诊** | 面色/舌象/拍照识图，AI辅助分析面色和舌苔 |
| **闻诊** | 声音/气味等信息录入 |
| **问诊** | 25 种常见症状多选，涵盖全身/头面/胸腹/四肢等 |
| **切诊** | 19 种脉象选择（浮/沉/迟/数/弦/滑等） |

### 🤖 AI 引擎 — 智能辨证论治

- **证候标签提取**: 从四诊信息中提取中医证候标签
- **Transformer 方剂匹配**: 基于多任务学习的深度学习模型，同时预测方剂、药材和剂量
- **自动加减建议**: 根据兼症推荐药物加减

### 📋 结果页

- 推荐 Top3 方剂，标注来源（作者/典籍）、匹配度、修改理由
- 详细展示方剂组成、剂量、功效和主治

### 👨‍⚕️ 医生端 — 处方审核

- 待审列表 → 双栏审核详情 → 批准/修改/驳回
- 确保所有 AI 推荐经过专业医师审核

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Next.js + React | 中国风水墨主题 UI，Vanilla CSS |
| **AI 模型** | PyTorch + Transformer | TCMFormulaNet 多任务学习架构 |
| **训练数据** | PTM 数据集 (TKDE 2018) | 98,000+ 真实中医处方 |
| **知识库** | JSON | 120 味中药材 + 45 个经典方剂 |

### 模型架构

```
症状 (multi-hot) → Embedding → Transformer Encoder (6层) → 方剂分类头
                                                          → 药材预测头
                                                          → 剂量回归头
```

---

## 📊 数据集

本项目使用两个数据源用于深度学习训练：

### 1. PTM 处方数据集（主要数据源）

| 项目 | 详情 |
|------|------|
| **论文** | Liang Yao et al., "A Topic Modeling Approach for Traditional Chinese Medicine Prescriptions", IEEE TKDE 2018 |
| **GitHub** | [yao8839836/PTM](https://github.com/yao8839836/PTM) |
| **规模** | **98,334** 条真实中医处方，含症状描述和药材组成 |
| **来源** | 中国工程科学知识中心 (CKCEST) |
| **许可** | ⚠️ 仅限研究用途，禁止商业使用 |

### 2. 经典方剂知识库（项目自带）

| 项目 | 详情 |
|------|------|
| **方剂** | 45 个经典方剂（伤寒论 / 金匮要略 / 温病条辨 / 太平惠民和剂局方等） |
| **药材** | 120 味常用中药，含性味归经、功效、用量等详细信息 |
| **格式** | 结构化 JSON，含 symptomTags、证候分类、剂量、加减法 |

### 训练数据统计

| 指标 | 数量 |
|------|------|
| 合并处方总数 | 97,508 |
| 训练样本 (含数据增强) | ~390,000 |
| 药材种类 | ~47,000 |
| 症状标签 | ~70,000 |

---

## 🚀 快速开始

### 环境要求

- **前端**: Node.js 18+
- **训练**: Python 3.10+, PyTorch 2.0+, NVIDIA GPU (推荐 RTX 5090, CUDA 13.0)

### 1️⃣ 前端 Web 界面

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

### 2️⃣ 深度学习训练

```bash
cd training

# 安装 PyTorch (RTX 5090 需要 CUDA 13.0)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt

# Step 1: 下载数据集 — 从 GitHub 获取 PTM 98K 处方数据
python scripts/download_dataset.py

# Step 2: 预处理 — 转换为训练格式，生成词表和训练/验证集
python scripts/prepare_data.py --use_raw

# Step 3: 训练模型 — RTX 5090 推荐参数 (~11小时)
python scripts/train.py \
    --device cuda \
    --epochs 200 \
    --batch_size 64 \
    --lr 0.0005 \
    --embed_dim 512 \
    --num_layers 6 \
    --dim_feedforward 1024

# Step 4: 评估模型
python scripts/evaluate.py --checkpoint checkpoints/best_model.pt

# Step 5: 导出为 API 可用模型
python scripts/export_model.py --checkpoint checkpoints/best_model.pt --output models/tcm_model.pt
```

> **提示**: 如果仅需快速测试，可用 CPU 模式运行少量 epoch:
> ```bash
> python scripts/train.py --device cpu --epochs 10 --batch_size 8
> ```

---

## 📁 项目结构

```
Chinese-medicine/
├── README.md                    # 本文件
├── package.json                 # Node.js 依赖
├── next.config.mjs              # Next.js 配置
│
├── src/                         # === 前端 (Next.js) ===
│   ├── app/                     # 页面路由
│   │   ├── page.js              # 首页
│   │   ├── patient/             # 患者四诊问诊流程
│   │   ├── result/              # AI 推荐结果页
│   │   └── doctor/              # 医生审核端
│   ├── components/              # React 组件库
│   ├── context/                 # 全局状态 (React Context)
│   ├── data/                    # 中药知识库 (JSON)
│   │   ├── herbs.json           # 120 味中药材详情
│   │   ├── formulas.json        # 45 个经典方剂
│   │   └── symptoms.json        # 症状/证候分类
│   └── lib/                     # AI 引擎 (规则匹配层)
│
├── training/                    # === 深度学习训练 ===
│   ├── README.md                # 训练模块说明
│   ├── requirements.txt         # Python 依赖
│   ├── scripts/
│   │   ├── download_dataset.py  # 数据集下载 (PTM 98K)
│   │   ├── prepare_data.py      # 数据预处理
│   │   ├── train.py             # 模型训练
│   │   ├── evaluate.py          # 模型评估
│   │   └── export_model.py      # 模型导出
│   ├── models/
│   │   ├── tcm_net.py           # TCMFormulaNet 模型定义
│   │   └── dataset.py           # PyTorch Dataset
│   ├── data/                    # 训练数据 (git ignored)
│   ├── checkpoints/             # 模型检查点 (git ignored)
│   └── logs/                    # TensorBoard 日志
│
└── public/                      # 静态资源
```

---

## 📜 引用

如使用本项目中的 PTM 数据集进行研究，请引用原始论文：

```bibtex
@article{yao2018topic,
  title     = {A Topic Modeling Approach for Traditional Chinese Medicine Prescriptions},
  author    = {Yao, Liang and Zhang, Yin and Wei, Baogang and Zhang, Wenjin and Jin, Zhe},
  journal   = {IEEE Transactions on Knowledge and Data Engineering},
  volume    = {30},
  number    = {6},
  pages     = {1007--1021},
  year      = {2018},
  publisher = {IEEE}
}
```

---

## ⚠️ 免责声明

本系统仅供**学习研究**和**辅助参考**使用，**不替代专业医疗诊断**。

- 所有 AI 推荐的处方必须经**执业中医师审核**后方可使用
- PTM 数据集版权归 CKCEST 所有，仅限研究用途，禁止商业使用
- 本项目不对任何因使用本系统产生的医疗后果承担责任

---

## 📄 License

本项目代码部分采用 MIT License。数据集部分遵循各自的许可协议。
