# 🏥 岐黄AI — 中医智能辅助诊疗系统

基于深度学习的中医四诊合参智能系统，通过望闻问切采集患者信息，AI辅助推荐经典方剂，医生审核确保安全有效。

## ✨ 功能特性

| 模块 | 功能 |
|------|------|
| **患者端** | 望诊（面色/舌象/拍照识图）→ 闻诊 → 问诊（25种症状多选）→ 切诊（19种脉象） |
| **AI引擎** | 证候标签提取 + Transformer方剂匹配 + 自动加减建议 |
| **结果页** | 推荐Top3方剂，标注来源（作者/典籍）、匹配度、修改理由 |
| **医生端** | 待审列表 → 双栏审核详情 → 批准/修改/驳回 |
| **知识库** | 120味中药材 + 45个经典方剂（伤寒论/金匮/温病条辨等） |

## 🛠️ 技术栈

- **前端**: Next.js + React + Vanilla CSS（中国风水墨主题）
- **AI引擎**: PyTorch Transformer（多任务学习）
- **数据**: 中药材/方剂 JSON 知识库

## 🚀 快速开始

### 前端 (Web界面)

```bash
npm install
npm run dev
# 访问 http://localhost:3000
```

### 深度学习训练 (需要 GPU)

```bash
cd training
pip install -r requirements.txt

# 1. 预处理数据
python scripts/prepare_data.py

# 2. 训练模型
python scripts/train.py --device cuda --epochs 200

# 3. 评估模型
python scripts/evaluate.py --checkpoint checkpoints/best_model.pt

# 4. 导出模型
python scripts/export_model.py --checkpoint checkpoints/best_model.pt
```

### 5090 GPU 推荐训练参数

```bash
python scripts/train.py \
    --device cuda \
    --epochs 500 \
    --batch_size 64 \
    --lr 0.0005 \
    --embed_dim 512 \
    --num_layers 6 \
    --dim_feedforward 1024
```

## 📁 项目结构

```
├── src/                    # Next.js 前端
│   ├── app/                # 页面路由
│   │   ├── page.js         # 首页
│   │   ├── patient/        # 患者问诊
│   │   ├── result/         # AI结果
│   │   └── doctor/         # 医生审核
│   ├── components/         # React 组件
│   ├── context/            # 全局状态
│   ├── data/               # 中药知识库
│   └── lib/                # AI引擎 (规则匹配)
├── training/               # 深度学习训练
│   ├── models/             # 模型定义
│   │   ├── tcm_net.py      # TCMFormulaNet
│   │   └── dataset.py      # 数据集
│   ├── scripts/            # 训练脚本
│   │   ├── prepare_data.py # 数据预处理
│   │   ├── train.py        # 训练
│   │   ├── evaluate.py     # 评估
│   │   └── export_model.py # 导出
│   └── requirements.txt    # Python 依赖
```

## ⚠️ 免责声明

本系统仅供学习研究和辅助参考使用，**不替代专业医疗诊断**。所有AI推荐的处方必须经执业中医师审核后方可使用。
