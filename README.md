# 🏥 岐黄AI - 智能中医诊断系统

<div align="center">

![岐黄AI](https://img.shields.io/badge/岐黄AI-智能中医诊断-DC143C?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**传承千年中医智慧，融合现代人工智能技术**

[在线演示](#) | [快速开始](#-快速开始) | [文档](#-文档) | [模型下载](#-模型下载)

</div>

---

## 📖 项目简介

岐黄AI是一个基于深度学习的智能中医诊断系统，通过**推荐系统 + 深度学习模型并行融合**的方式，为患者提供智能问诊服务，并支持医生在线审核处方。

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🩺 **智能问诊** | 患者端支持四诊（望闻问切）信息采集 |
| 🤖 **AI诊断** | LSAN深度学习模型 + 规则匹配双引擎 |
| 👨‍⚕️ **医生审核** | 医生端支持处方审核、编辑、批准 |
| 📚 **知识库** | 内置15首经典名方，支持自定义添加 |
| 🔍 **相似推荐** | 自动推荐相似病情的经典方剂 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    岐黄AI 智能中医诊断系统                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │    患者端        │    │    医生端        │                    │
│  │  ·智能问诊       │    │  ·诊断审核       │                    │
│  │  ·四诊采集       │    │  ·处方编辑       │                    │
│  │  ·AI诊断结果     │    │  ·患者管理       │                    │
│  └────────┬────────┘    └────────┬────────┘                    │
│           └──────────┬───────────┘                              │
│                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              双引擎AI诊断服务                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │ 推荐系统    │  │ 深度学习    │  │ 并行融合    │      │   │
│  │  │ (规则匹配)  │  │ (LSAN模型)  │  │ (加权投票)  │      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

| 软件 | 版本 |
|------|------|
| Python | 3.8+ |
| Node.js | 18+ |
| pip | 最新版 |
| npm | 最新版 |

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/cyliu03/Chinese-medicine.git
cd Chinese-medicine

# 2. 下载模型文件（从ModelScope或HuggingFace）
# 模型文件较大，需要单独下载
# 下载地址见下方"模型下载"章节

# 3. 安装后端依赖
cd server
pip install -r requirements.txt

# 4. 安装前端依赖
cd ..
npm install

# 5. 启动服务
# Windows
start.bat

# Mac/Linux
./start.sh
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 首页 | http://localhost:3000 |
| 患者端 | http://localhost:3000/patient |
| 医生端 | http://localhost:3000/doctor |
| 后端API | http://localhost:8000/docs |

---

## 📥 模型下载

由于模型文件较大（~57MB），我们将其托管在ModelScope和HuggingFace上：

### 方式一：ModelScope（国内推荐）

```python
from modelscope import snapshot_download

# 下载整个模型仓库
model_dir = snapshot_download('cy1750/qihuang-ai-model')
print(f"模型下载到: {model_dir}")
```

### 方式二：HuggingFace

```python
from huggingface_hub import hf_hub_download

# 下载模型文件
model_path = hf_hub_download(
    repo_id="zw1223/qihuang-ai-model",
    filename="best_model.pt",
    local_dir="./training/checkpoints"
)

# 下载词汇表
data_path = hf_hub_download(
    repo_id="zw1223/qihuang-ai-model",
    filename="meta.json",
    local_dir="./data/chatmed"
)
```

**手动下载**
- ModelScope: https://modelscope.cn/models/cy1750/qihuang-ai-model
- HuggingFace: https://huggingface.co/zw1223/qihuang-ai-model

---

## 📊 模型信息

| 指标 | 数值 |
|------|------|
| 模型架构 | LSAN (Label-Specific Attention Network) |
| 训练样本 | 54,204 条 |
| 症状种类 | 9,629 种 |
| 中药种类 | 273 种 |
| 测试集F1 | 0.386 |
| 数据来源 | ChatMed_TCM |

---

## 📁 项目结构

```
Chinese-medicine/
├── src/                    # 前端源代码
│   ├── app/                # 页面
│   │   ├── page.js         # 首页
│   │   ├── patient/        # 患者端
│   │   └── doctor/         # 医生端
│   ├── components/         # 组件
│   ├── context/            # 状态管理
│   ├── lib/                # 工具库
│   │   ├── aiEngine.js     # AI诊断引擎
│   │   └── formulaKnowledge.js  # 药方知识库
│   └── data/               # 静态数据
├── server/                 # 后端服务
│   ├── main.py             # FastAPI主程序
│   ├── predictor.py        # 模型预测器
│   └── requirements.txt    # Python依赖
├── training/               # 训练相关
│   ├── checkpoints/        # 模型权重（需单独下载）
│   ├── models/             # 模型定义
│   ├── scripts/            # 训练脚本
│   └── configs/            # 配置文件
├── data/                   # 数据目录
│   └── chatmed/            # ChatMed数据集
├── docs/                   # 文档
│   ├── 技术文档.md
│   └── 测试文档.md
├── start.bat               # Windows启动脚本
├── start.ps1               # PowerShell启动脚本
├── docker-compose.yml      # Docker部署配置
└── README.md
```

---

## 🔧 技术栈

### 前端
- **框架**: Next.js 16 (React)
- **样式**: CSS Modules
- **状态管理**: React Context

### 后端
- **框架**: FastAPI
- **深度学习**: PyTorch
- **模型**: LSAN (Label-Specific Attention Network)

### AI引擎
- **推荐系统**: 规则匹配 + 症状标签
- **深度学习**: LSAN模型
- **并行融合**: 加权投票

---

## 📚 文档

- [技术文档](docs/技术文档.md) - 详细的系统架构和算法说明
- [测试文档](docs/测试文档.md) - 测试用例和测试报告
- [部署指南](部署指南.md) - 本地部署教程
- [在线部署指南](在线部署指南.md) - 云端部署教程

---

## 🎯 使用流程

### 患者端
1. 填写基本信息
2. 完成四诊采集（望闻问切）
3. 查看AI诊断结果
4. 提交给医生审核

### 医生端
1. 查看待审核诊断列表
2. 审核AI推荐处方
3. 查看相似病情名医药方
4. 编辑处方（可选）
5. 批准或驳回

---

## ⚠️ 免责声明

本系统**仅供学习和研究使用**，不用于实际医疗诊断。AI推荐结果仅供参考，不能替代专业医生的诊断。如有健康问题，请咨询专业医疗机构。

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- 数据来源: [ChatMed_TCM](https://huggingface.co/datasets/michaelwzhu/shenong_tcm_dataset)
- 经典方剂: 《伤寒论》、《太平惠民和剂局方》等

---

## 📞 联系方式

如有问题或建议，欢迎：
- 提交 [Issue](https://github.com/cyliu03/Chinese-medicine/issues)
- 发起 [Pull Request](https://github.com/cyliu03/Chinese-medicine/pulls)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给一个Star支持一下！⭐**

Made with ❤️ by 岐黄AI Team

</div>
