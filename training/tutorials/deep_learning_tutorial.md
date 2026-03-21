# 深度学习工程实践教程：中医方剂推荐系统

## 目录

1. [项目背景与意义](#1-项目背景与意义)
2. [问题定义与建模](#2-问题定义与建模)
3. [数据工程详解](#3-数据工程详解)
4. [评价指标详解](#4-评价指标详解)
5. [深度学习原理与特征提取](#5-深度学习原理与特征提取)
6. [注意力机制详解](#6-注意力机制详解)
7. [模型架构设计](#7-模型架构设计)
8. [损失函数设计详解](#8-损失函数设计详解)
9. [训练流程详解](#9-训练流程详解)
10. [模型评估与分析](#10-模型评估与分析)
11. [工程实践要点](#11-工程实践要点)
12. [常见问题与解决方案](#12-常见问题与解决方案)

---

## 1. 项目背景与意义

### 1.1 中医方剂学的挑战

中医方剂学是中医药学的核心组成部分，它研究方剂的组成、变化和临床运用规律。一个方剂通常由多味药材按照特定比例配伍而成，每味药材在方剂中扮演不同的角色：

```
方剂组成结构：
┌─────────────────────────────────────────────────────────┐
│  麻黄汤（解表剂）                                        │
├─────────────────────────────────────────────────────────┤
│  君药：麻黄 9g  - 发汗解表，宣肺平喘                      │
│  臣药：桂枝 9g  - 解肌发表，温通经脉                      │
│  佐药：杏仁 9g  - 降利肺气，助麻黄平喘                    │
│  使药：甘草 6g  - 调和诸药                                │
└─────────────────────────────────────────────────────────┘
```

**传统方剂推荐面临的挑战：**

1. **知识体系复杂**：中医理论包含阴阳五行、脏腑经络、病因病机等复杂概念，难以用简单规则表达

2. **症状表述多样**：同一症状有多种表述方式
   - "咳嗽" 可表述为：咳、咳痰、干咳、咳嗽痰多、咳逆等
   - "发热" 可表述为：发烧、身热、高热、低热、潮热等

3. **方剂数量庞大**：《方剂学》教材收录方剂约300首，而历代医籍记载方剂超过10万首

4. **配伍规律复杂**：药材之间存在复杂的相互作用
   - 相须：性能功效类似的药物配合使用
   - 相使：以一种药为主，另一种药为辅
   - 相畏：一种药的毒性或副作用能被另一种药减轻或消除

5. **个体化诊疗**：同病异治、异病同治，需要根据具体症状组合灵活调整

### 1.2 为什么选择深度学习？

#### 1.2.1 传统方法的局限性

**规则匹配方法：**
```python
def rule_based_recommend(symptoms):
    """
    基于规则的方剂推荐
    问题：需要手工编写大量规则，难以覆盖所有情况
    """
    if "恶寒" in symptoms and "发热" in symptoms and "无汗" in symptoms:
        return "麻黄汤"
    elif "发热" in symptoms and "恶风" in symptoms and "汗出" in symptoms:
        return "桂枝汤"
    # ... 需要为每个方剂编写规则
    else:
        return "无法识别"
```

**问题分析：**
- 规则数量随方剂数量线性增长，维护困难
- 无法处理症状组合的细微差异
- 无法学习隐含的配伍规律
- 泛化能力差，遇到未见过的症状组合就失效

**统计学习方法（如SVM、随机森林）：**
```python
from sklearn.ensemble import RandomForestClassifier

# 问题：多标签分类需要转换为多个二分类问题
# 无法有效建模标签之间的相关性
model = RandomForestClassifier()
model.fit(X_train, y_train)
```

**问题分析：**
- 需要手工设计特征（特征工程）
- 难以捕捉症状之间的复杂关系
- 无法建模药材之间的配伍规律
- 对数据质量要求高

#### 1.2.2 深度学习的优势

**1. 端到端学习**
```
传统方法：症状 → 特征工程 → 分类器 → 方剂
深度学习：症状 → 神经网络 → 方剂（自动学习特征）
```

**2. 自动特征学习**
```python
# 传统方法需要手工设计特征
features = [
    len(symptoms),                    # 症状数量
    has_cold_symptoms(symptoms),      # 是否有寒证
    has_heat_symptoms(symptoms),      # 是否有热证
    # ... 需要领域专家设计
]

# 深度学习自动学习特征
features = neural_network(symptoms)  # 网络自动学习最有用的特征
```

**3. 建模复杂关系**
- 通过多层非线性变换，学习症状与药材之间的复杂映射
- 通过注意力机制，学习每个药材应该关注哪些症状
- 通过标签相关性建模，学习药材之间的配伍规律

**4. 泛化能力强**
- 训练好的模型可以处理未见过的症状组合
- 通过数据增强提高鲁棒性

### 1.3 项目目标与意义

#### 1.3.1 项目目标

| 目标 | 描述 | 验收标准 |
|------|------|----------|
| 准确性 | 正确推荐方剂药材 | F1 ≥ 0.90 |
| 完整性 | 不遗漏关键药材 | Recall ≥ 0.90 |
| 精确性 | 不多开无关药材 | Precision ≥ 0.90 |
| 可解释性 | 提供推荐理由 | 注意力权重可视化 |

#### 1.3.2 实际意义

**临床辅助诊断：**
- 为年轻中医师提供方剂推荐参考
- 帮助基层医生提高诊疗水平
- 辅助中医教学和培训

**中医药传承：**
- 将名老中医经验数字化
- 保存和传承经典方剂知识
- 促进中医药现代化发展

**科研价值：**
- 探索中医方剂配伍规律
- 发现新的药物组合
- 为中药新药研发提供思路

---

## 2. 问题定义与建模

### 2.1 问题类型分析

#### 2.1.1 输入输出定义

```
输入（症状集合）：
X = {s₁, s₂, ..., sₙ}

其中 sᵢ ∈ 症状词表 Vₛ = {恶寒, 发热, 无汗, 头痛, ...}
共 |Vₛ| = 120 个症状

输出（药材集合）：
Y = {h₁, h₂, ..., hₘ}

其中 hⱼ ∈ 药材词表 Vₕ = {麻黄, 桂枝, 杏仁, 甘草, ...}
共 |Vₕ| = 89 味药材
```

#### 2.1.2 多标签分类问题

这是一个**多标签分类问题**（Multi-label Classification），与传统单标签分类有本质区别：

| 特性 | 单标签分类 | 多标签分类 |
|------|------------|------------|
| 输出类别数 | 1个 | 多个（0到全部） |
| 标签关系 | 互斥 | 可共存、相关 |
| 损失函数 | CrossEntropy | BCEWithLogitsLoss |
| 输出层 | Softmax | Sigmoid（每个标签独立） |
| 评估指标 | Accuracy | Precision, Recall, F1 |

**数学定义：**

单标签分类：
$$P(y = k | x) = \frac{e^{z_k}}{\sum_{j=1}^{K} e^{z_j}}$$

多标签分类：
$$P(y_i = 1 | x) = \sigma(z_i) = \frac{1}{1 + e^{-z_i}}$$

每个标签独立计算概率，互不影响。

### 2.2 标签相关性分析

在方剂推荐中，药材之间存在显著的相关性：

#### 2.2.1 常见配伍组合

```
相须配伍（性能相似，增强疗效）：
┌────────────────────────────────────────┐
│ 麻黄 + 桂枝 → 增强发汗解表             │
│ 石膏 + 知母 → 增强清热泻火             │
│ 金银花 + 连翘 → 增强清热解毒           │
└────────────────────────────────────────┘

相使配伍（主辅配合）：
┌────────────────────────────────────────┐
│ 大黄（主）+ 芒硝（辅）→ 峻下热结       │
│ 黄芩（主）+ 柴胡（辅）→ 和解少阳       │
└────────────────────────────────────────┘

调和诸药：
┌────────────────────────────────────────┐
│ 甘草：调和诸药，缓解药物烈性           │
│ 大枣：调和营卫，保护脾胃               │
│ 生姜：调和药性，解毒                   │
└────────────────────────────────────────┘
```

#### 2.2.2 相关性矩阵

通过统计训练数据，可以计算药材之间的共现概率：

```python
# 药材共现矩阵（部分）
co_occurrence = {
    ("麻黄", "桂枝"): 0.95,   # 麻黄汤等方剂中常同用
    ("麻黄", "杏仁"): 0.88,   # 宣肺平喘配伍
    ("桂枝", "白芍"): 0.82,   # 桂枝汤等调和营卫
    ("人参", "白术"): 0.76,   # 四君子汤等健脾益气
    ("当归", "川芎"): 0.71,   # 四物汤等补血活血
    # ...
}
```

**为什么标签相关性重要？**

1. **提高预测准确性**：如果预测了"麻黄"，那么"桂枝"出现的概率也应该增加
2. **减少不合理组合**：某些药材组合在中医理论中是不合理的
3. **提供可解释性**：通过相关性可以解释为什么推荐这些药材

### 2.3 数学建模

#### 2.3.1 问题形式化

给定症状向量 $\mathbf{x} \in \{0,1\}^{|V_s|}$，预测药材标签集合 $\mathbf{y} \in \{0,1\}^{|V_h|}$：

$$f: \{0,1\}^{|V_s|} \rightarrow \{0,1\}^{|V_h|}$$

#### 2.3.2 概率建模

使用神经网络建模条件概率：

$$P(\mathbf{y}|\mathbf{x}) = \prod_{j=1}^{|V_h|} P(y_j|\mathbf{x})$$

其中：
$$P(y_j=1|\mathbf{x}) = \sigma(f_j(\mathbf{x}))$$

$f_j(\mathbf{x})$ 是神经网络对第 $j$ 个药材的输出logit。

#### 2.3.3 决策边界

对于每个药材，独立判断是否包含：

$$\hat{y}_j = \begin{cases} 1 & \text{if } P(y_j=1|\mathbf{x}) \geq \theta_j \\ 0 & \text{otherwise} \end{cases}$$

其中 $\theta_j$ 是第 $j$ 个药材的决策阈值，通常设为 0.5，但可以根据需要调整。

---

## 3. 数据工程详解

### 3.1 数据来源

#### 3.1.1 经典方剂数据

本项目数据来源于《方剂学》教材收录的经典方剂，这些方剂经过数百年临床验证，配伍严谨、疗效确切。

**数据来源权威性：**
- 《伤寒论》- 东汉张仲景著，收录方剂113首
- 《金匮要略》- 东汉张仲景著，收录方剂262首
- 《温病条辨》- 清代吴鞠通著，创立温病方剂体系
- 《方剂学》教材 - 全国中医药行业高等教育规划教材

#### 3.1.2 数据集统计

```
数据集统计信息：
┌─────────────────────────────────────────────────────┐
│ 总样本数：8,600                                      │
│ ├─ 原始经典方剂样本：600（40方剂 × 15变体）          │
│ └─ 数据增强样本：8,000                               │
│                                                      │
│ 数据集划分：                                         │
│ ├─ 训练集：5,160 样本（60%）                        │
│ ├─ 验证集：1,720 样本（20%）                        │
│ └─ 测试集：1,720 样本（20%）                        │
│                                                      │
│ 词表规模：                                           │
│ ├─ 症状词表：120 个症状                             │
│ └─ 药材词表：89 味药材                              │
│                                                      │
│ 平均统计：                                           │
│ ├─ 平均每样本症状数：4.09 个                        │
│ ├─ 平均每样本药材数：6.47 味                        │
│ ├─ 最少症状数：3 个                                 │
│ ├─ 最多症状数：7 个                                 │
│ ├─ 最少药材数：2 味                                 │
│ └─ 最多药材数：14 味                                │
└─────────────────────────────────────────────────────┘
```

### 3.2 数据清洗详解

#### 3.2.1 原始数据问题

从不同来源收集的原始数据存在以下问题：

```
问题1：症状表述不统一
┌─────────────────────────────────────────────────────┐
│ 同一症状的不同表述：                                 │
│ - "咳嗽" / "咳" / "咳痰" / "咳嗽痰多" / "干咳"      │
│ - "发热" / "发烧" / "身热" / "高热" / "低热"        │
│ - "头痛" / "头疼" / "头风" / "偏头痛"               │
└─────────────────────────────────────────────────────┘

问题2：症状粒度不一致
┌─────────────────────────────────────────────────────┐
│ 有的描述详细，有的描述笼统：                         │
│ - 详细："恶寒发热，无汗，头痛身痛，气喘"             │
│ - 笼统："外感风寒"                                  │
└─────────────────────────────────────────────────────┘

问题3：药材名称不规范
┌─────────────────────────────────────────────────────┐
│ 同一药材的不同名称：                                 │
│ - "甘草" / "生甘草" / "炙甘草"                      │
│ - "半夏" / "法半夏" / "姜半夏" / "清半夏"           │
│ - "熟地" / "熟地黄"                                 │
└─────────────────────────────────────────────────────┘

问题4：剂量单位不统一
┌─────────────────────────────────────────────────────┐
│ 传统剂量：两、钱、分                                 │
│ 现代剂量：克（g）                                    │
│ 需要统一换算                                         │
└─────────────────────────────────────────────────────┘
```

#### 3.2.2 清洗流程

```python
def clean_symptom(symptom):
    """
    症状清洗与标准化
    
    步骤：
    1. 去除空白字符
    2. 统一同义词
    3. 分解复合症状
    """
    symptom = symptom.strip()
    
    # 同义词映射
    SYMPTOM_NORMALIZATION = {
        "咳": "咳嗽",
        "咳痰": "咳嗽",
        "干咳": "咳嗽",
        "咳嗽痰多": "咳嗽",
        "发烧": "发热",
        "身热": "发热",
        "高热": "发热",
        "低热": "发热",
        "头疼": "头痛",
        "头风": "头痛",
        "偏头痛": "头痛",
        "肚子疼": "腹痛",
        "腹中痛": "腹痛",
        "脘腹疼痛": "腹痛",
        "拉肚子": "腹泻",
        "泄泻": "腹泻",
        "大便溏薄": "腹泻",
        "睡不着": "失眠",
        "不寐": "失眠",
        "入睡困难": "失眠",
        "无力": "乏力",
        "疲倦": "乏力",
        "疲乏": "乏力",
        "倦怠": "乏力",
        "气促": "气短",
        "呼吸短促": "气短",
        "头昏": "头晕",
        "眩晕": "头晕",
        "想吐": "恶心",
        "反胃": "恶心",
        "口中苦": "口苦",
        "口中干燥": "口干",
        "口渴": "口干",
        "心慌": "心悸",
        "心跳": "心悸",
        "腰酸": "腰痛",
        "腰膝酸软": "腰痛",
        "夜间出汗": "盗汗",
        "睡后汗出": "盗汗",
        "动则汗出": "自汗",
        "白天出汗": "自汗",
        "不欲饮食": "食欲不振",
        "纳差": "食欲不振",
        "食少": "食欲不振",
    }
    
    return SYMPTOM_NORMALIZATION.get(symptom, symptom)


def clean_herb(herb_name):
    """
    药材名称清洗与标准化
    
    步骤：
    1. 去除炮制方法前缀（保留核心药名）
    2. 统一别名
    3. 去除产地前缀
    """
    herb_name = herb_name.strip()
    
    # 炮制方法标准化
    PROCESSING_NORMALIZATION = {
        "炙甘草": "甘草",
        "生甘草": "甘草",
        "法半夏": "半夏",
        "姜半夏": "半夏",
        "清半夏": "半夏",
        "熟地": "熟地黄",
        "生地": "生地黄",
        "杭白芍": "白芍",
        "川白芍": "白芍",
        "云茯苓": "茯苓",
        "川茯苓": "茯苓",
    }
    
    return PROCESSING_NORMALIZATION.get(herb_name, herb_name)


def clean_dosage(dosage_str):
    """
    剂量清洗与标准化
    
    将传统剂量单位转换为克（g）
    """
    # 传统剂量换算（以汉代度量衡为基准）
    # 1两 ≈ 15.625g
    # 1钱 ≈ 3.125g
    # 1分 ≈ 0.3125g
    
    DOSAGE_CONVERSION = {
        "两": 15.625,
        "钱": 3.125,
        "分": 0.3125,
        "g": 1,
        "克": 1,
    }
    
    import re
    match = re.match(r"(\d+(?:\.\d+)?)\s*([两钱分g克]*)", dosage_str)
    if match:
        value = float(match.group(1))
        unit = match.group(2) or "g"
        return value * DOSAGE_CONVERSION.get(unit, 1)
    return None
```

#### 3.2.3 数据验证

```python
def validate_sample(sample):
    """
    数据验证
    
    检查数据完整性和合理性
    """
    errors = []
    
    # 检查必填字段
    if not sample.get('symptoms'):
        errors.append("缺少症状信息")
    if not sample.get('herbs'):
        errors.append("缺少药材信息")
    
    # 检查症状数量合理性
    if len(sample.get('symptoms', [])) < 2:
        errors.append("症状数量过少（<2）")
    if len(sample.get('symptoms', [])) > 15:
        errors.append("症状数量过多（>15）")
    
    # 检查药材数量合理性
    if len(sample.get('herbs', [])) < 2:
        errors.append("药材数量过少（<2）")
    if len(sample.get('herbs', [])) > 20:
        errors.append("药材数量过多（>20）")
    
    # 检查剂量合理性
    for herb in sample.get('herbs', []):
        dosage = herb.get('dosage', 0)
        if dosage <= 0:
            errors.append(f"药材{herb.get('name')}剂量无效")
        if dosage > 100:
            errors.append(f"药材{herb.get('name')}剂量过大（>100g）")
    
    return errors
```

### 3.3 数据增强详解

#### 3.3.1 为什么需要数据增强？

```
原始数据量：40个经典方剂
直接训练问题：
┌─────────────────────────────────────────────────────┐
│ 1. 样本太少，容易过拟合                              │
│ 2. 模型无法学习症状的多样表达                        │
│ 3. 泛化能力差                                        │
└─────────────────────────────────────────────────────┘

数据增强后：8,600个样本
解决问题：
┌─────────────────────────────────────────────────────┐
│ 1. 样本量充足，减少过拟合                            │
│ 2. 学习症状的同义表达                                │
│ 3. 增强模型鲁棒性                                    │
└─────────────────────────────────────────────────────┘
```

#### 3.3.2 增强策略详解

**策略1：症状同义词替换**

```python
# 症状同义词词典
SYMPTOM_VARIATIONS = {
    "咳嗽": ["咳", "咳痰", "干咳", "咳嗽痰多"],
    "发热": ["发烧", "身热", "高热", "低热"],
    "头痛": ["头疼", "头风", "偏头痛"],
    "腹痛": ["肚子疼", "腹中痛", "脘腹疼痛"],
    "腹泻": ["拉肚子", "泄泻", "大便溏薄"],
    "失眠": ["睡不着", "不寐", "入睡困难"],
    "乏力": ["无力", "疲倦", "疲乏", "倦怠"],
    "气短": ["气促", "呼吸短促"],
    "头晕": ["头昏", "眩晕"],
    "恶心": ["想吐", "反胃"],
    "口苦": ["口中苦"],
    "口干": ["口中干燥", "口渴"],
    "心悸": ["心慌", "心跳"],
    "腰痛": ["腰酸", "腰膝酸软"],
    "盗汗": ["夜间出汗", "睡后汗出"],
    "自汗": ["动则汗出", "白天出汗"],
    "食欲不振": ["不欲饮食", "纳差", "食少"],
}

def synonym_replacement(symptoms, replace_prob=0.3):
    """
    同义词替换增强
    
    以一定概率将症状替换为其同义词
    
    参数：
        symptoms: 原始症状列表
        replace_prob: 每个症状被替换的概率
    
    返回：
        增强后的症状列表
    """
    new_symptoms = []
    for s in symptoms:
        if s in SYMPTOM_VARIATIONS and random.random() < replace_prob:
            # 随机选择一个同义词
            new_symptoms.append(random.choice(SYMPTOM_VARIATIONS[s]))
        else:
            new_symptoms.append(s)
    return new_symptoms

# 示例
original = ["咳嗽", "发热", "头痛"]
augmented = synonym_replacement(original)
# 可能结果：["咳痰", "发烧", "头痛"]
```

**策略2：症状子集采样**

```python
def symptom_subset_sampling(symptoms, min_keep=3):
    """
    症状子集采样
    
    随机保留部分症状，模拟临床诊断中患者描述不完整的情况
    
    参数：
        symptoms: 原始症状列表
        min_keep: 最少保留的症状数量
    
    返回：
        采样后的症状列表
    """
    if len(symptoms) <= min_keep:
        return symptoms.copy()
    
    # 随机选择保留的症状数量
    k = random.randint(min_keep, len(symptoms))
    
    # 随机选择k个症状
    return random.sample(symptoms, k)

# 示例
original = ["恶寒", "发热", "无汗", "头痛", "身痛", "喘"]
augmented = symptom_subset_sampling(original)
# 可能结果：["恶寒", "发热", "无汗", "头痛"]
```

**策略3：症状顺序打乱**

```python
def shuffle_symptoms(symptoms):
    """
    症状顺序打乱
    
    打乱症状的顺序，使模型不依赖于症状的输入顺序
    """
    shuffled = symptoms.copy()
    random.shuffle(shuffled)
    return shuffled

# 示例
original = ["恶寒", "发热", "无汗", "头痛"]
augmented = shuffle_symptoms(original)
# 可能结果：["头痛", "无汗", "发热", "恶寒"]
```

#### 3.3.3 完整增强流程

```python
def augment_data(data, symptom_vocab, herb_vocab, augment_factor=5):
    """
    完整的数据增强流程
    
    参数：
        data: 原始数据列表
        symptom_vocab: 症状词表
        herb_vocab: 药材词表
        augment_factor: 每个样本增强的倍数
    
    返回：
        增强后的数据列表
    """
    augmented = []
    
    for sample in data:
        # 保留原始样本
        augmented.append(sample.copy())
        
        # 生成增强样本
        for _ in range(augment_factor):
            new_sample = {
                'symptoms': sample['symptoms'].copy(),
                'herbs': [h.copy() for h in sample['herbs']],
                'formula_name': sample['formula_name'],
                'source': sample.get('source', '') + '_aug',
            }
            
            # 应用增强策略
            # 1. 同义词替换（30%概率）
            new_sample['symptoms'] = synonym_replacement(
                new_sample['symptoms'], 
                replace_prob=0.3
            )
            
            # 2. 症状子集采样（50%概率）
            if random.random() < 0.5:
                new_sample['symptoms'] = symptom_subset_sampling(
                    new_sample['symptoms'],
                    min_keep=3
                )
            
            # 3. 症状顺序打乱
            new_sample['symptoms'] = shuffle_symptoms(new_sample['symptoms'])
            
            augmented.append(new_sample)
    
    # 打乱增强后的数据
    random.shuffle(augmented)
    
    return augmented
```

### 3.4 数据集划分

#### 3.4.1 划分原则

```
数据集划分原则：
┌─────────────────────────────────────────────────────┐
│ 1. 随机性：使用随机种子确保可复现                     │
│ 2. 独立性：三个数据集之间不能有重叠                   │
│ 3. 分布一致性：各数据集的标签分布应相似               │
│ 4. 时间独立性：测试集模拟"未来"数据                   │
└─────────────────────────────────────────────────────┘
```

#### 3.4.2 划分实现

```python
def split_dataset(data, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, seed=42):
    """
    数据集划分
    
    参数：
        data: 完整数据列表
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        seed: 随机种子
    
    返回：
        train_data, val_data, test_data
    """
    assert train_ratio + val_ratio + test_ratio == 1.0, "比例之和必须为1"
    
    # 设置随机种子
    random.seed(seed)
    
    # 打乱数据
    shuffled_data = data.copy()
    random.shuffle(shuffled_data)
    
    # 计算划分点
    n = len(shuffled_data)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    # 划分数据集
    train_data = shuffled_data[:train_end]
    val_data = shuffled_data[train_end:val_end]
    test_data = shuffled_data[val_end:]
    
    print(f"数据集划分完成：")
    print(f"  训练集：{len(train_data)} 样本 ({len(train_data)/n*100:.1f}%)")
    print(f"  验证集：{len(val_data)} 样本 ({len(val_data)/n*100:.1f}%)")
    print(f"  测试集：{len(test_data)} 样本 ({len(test_data)/n*100:.1f}%)")
    
    return train_data, val_data, test_data
```

#### 3.4.3 为什么是6:2:2？

```
常见划分比例对比：
┌──────────┬────────┬────────┬────────┬─────────────────────┐
│ 比例     │ 训练集 │ 验证集 │ 测试集 │ 适用场景            │
├──────────┼────────┼────────┼────────┼─────────────────────┤
│ 8:1:1    │ 80%    │ 10%    │ 10%    │ 数据量充足时        │
│ 7:1.5:1.5│ 70%    │ 15%    │ 15%    │ 常用比例            │
│ 6:2:2    │ 60%    │ 20%    │ 20%    │ 数据量中等时（本项目）│
│ 5:2.5:2.5│ 50%    │ 25%    │ 25%    │ 数据量较少时        │
└──────────┴────────┴────────┴────────┴─────────────────────┘

本项目选择6:2:2的原因：
1. 数据量中等（8,600样本），需要足够的训练数据
2. 验证集足够大，能可靠评估模型性能
3. 测试集足够大，能提供稳定的最终评估
4. 避免测试集太小导致评估不稳定
```

### 3.5 词表构建

#### 3.5.1 词表的作用

```
词表的作用：
┌─────────────────────────────────────────────────────┐
│ 1. 将文本转换为数值索引                              │
│ 2. 定义模型的输入输出空间                            │
│ 3. 提供从索引到文本的映射                            │
└─────────────────────────────────────────────────────┘

症状词表示例：
┌──────────┬───────┐
│ 症状     │ 索引  │
├──────────┼───────┤
│ 恶寒     │ 0     │
│ 发热     │ 1     │
│ 无汗     │ 2     │
│ 头痛     │ 3     │
│ ...      │ ...   │
│ 喘       │ 119   │
└──────────┴───────┘

药材词表示例：
┌──────────┬───────┐
│ 药材     │ 索引  │
├──────────┼───────┤
│ 麻黄     │ 0     │
│ 桂枝     │ 1     │
│ 杏仁     │ 2     │
│ 甘草     │ 3     │
│ ...      │ ...   │
│ 炙甘草   │ 88    │
└──────────┴───────┘
```

#### 3.5.2 词表构建代码

```python
def build_vocab(data):
    """
    构建症状和药材词表
    
    参数：
        data: 数据列表
    
    返回：
        symptom_vocab: 症状词表 {症状: 索引}
        herb_vocab: 药材词表 {药材: 索引}
    """
    symptom_set = set()
    herb_set = set()
    
    for sample in data:
        # 收集所有症状
        for symptom in sample['symptoms']:
            symptom_set.add(symptom)
        
        # 收集所有药材
        for herb in sample['herbs']:
            herb_set.add(herb['name'])
    
    # 排序后建立映射（排序确保可复现）
    symptom_vocab = {s: i for i, s in enumerate(sorted(symptom_set))}
    herb_vocab = {h: i for i, h in enumerate(sorted(herb_set))}
    
    print(f"词表构建完成：")
    print(f"  症状词表：{len(symptom_vocab)} 个症状")
    print(f"  药材词表：{len(herb_vocab)} 味药材")
    
    return symptom_vocab, herb_vocab
```

### 3.6 数据打包

数据集已打包为JSON格式，包含以下文件：

```
data_external/
├── train_data.json     # 训练集（5,160样本）
├── val_data.json       # 验证集（1,720样本）
├── test_data.json      # 测试集（1,720样本）
├── symptom_vocab.json  # 症状词表（120个症状）
├── herb_vocab.json     # 药材词表（89味药材）
└── meta.json           # 元数据
```

**数据格式示例：**

```json
// train_data.json 中的单个样本
{
  "symptoms": ["恶寒", "发热", "无汗", "头痛", "身痛", "喘"],
  "herbs": [
    {"name": "麻黄", "dosage": 9},
    {"name": "桂枝", "dosage": 9},
    {"name": "杏仁", "dosage": 9},
    {"name": "甘草", "dosage": 6}
  ],
  "formula_name": "麻黄汤",
  "source": "classic_麻黄汤",
  "is_classic": true
}
```

---

## 4. 评价指标详解

### 4.1 为什么需要多个指标？

```
单一指标的局限性：
┌─────────────────────────────────────────────────────┐
│ 假设有100个测试样本，每个样本平均有6味药材           │
│ 总共600个药材预测任务                                │
│                                                      │
│ 情况1：模型预测所有样本都开"甘草"                   │
│ - Accuracy = 600/600 = 100%？不，这是错误的计算     │
│ - 实际上，每个药材是独立的预测任务                   │
│                                                      │
│ 情况2：模型预测每个样本都开所有89味药材             │
│ - Recall = 100%（没有漏开任何药材）                 │
│ - 但Precision很低（多开了大量无关药材）             │
│                                                      │
│ 情况3：模型预测每个样本都不开任何药材               │
│ - Precision无法计算（分母为0）                      │
│ - Recall = 0%（漏开了所有药材）                     │
└─────────────────────────────────────────────────────┘

结论：需要综合考虑Precision和Recall
```

### 4.2 基础概念

#### 4.2.1 混淆矩阵

对于多标签分类，每个标签有独立的混淆矩阵：

```
对于第j个药材的预测：
                    实际值
                 正(Yj=1)   负(Yj=0)
预测值  正(Ŷj=1)    TP        FP
        负(Ŷj=0)    FN        TN

其中：
- TP (True Positive)：正确预测为有该药材
- FP (False Positive)：错误预测为有该药材（多开）
- FN (False Negative)：错误预测为无该药材（漏开）
- TN (True Negative)：正确预测为无该药材
```

#### 4.2.2 多标签场景的聚合

```python
def compute_confusion_matrix(preds, targets):
    """
    计算多标签场景的聚合混淆矩阵
    
    参数：
        preds: 预测结果 [batch_size, num_labels]
        targets: 真实标签 [batch_size, num_labels]
    
    返回：
        tp, fp, fn, tn: 聚合的混淆矩阵值
    """
    # 所有样本、所有标签的聚合
    tp = (preds * targets).sum().item()      # 预测有且实际有
    fp = (preds * (1 - targets)).sum().item() # 预测有但实际无
    fn = ((1 - preds) * targets).sum().item() # 预测无但实际有
    tn = ((1 - preds) * (1 - targets)).sum().item() # 预测无且实际无
    
    return tp, fp, fn, tn
```

### 4.3 Precision（精确率）

#### 4.3.1 定义

$$Precision = \frac{TP}{TP + FP} = \frac{\text{正确预测的药材数}}{\text{预测的药材总数}}$$

**含义**：在模型预测为"有"的药材中，真正应该有的比例。

**中医场景解释**：
- 高Precision：不多开药材，开的都是对症的
- 低Precision：多开了很多不必要的药材

#### 4.3.2 计算示例

```python
def compute_precision(preds, targets):
    """
    计算Precision
    
    示例：
    预测药材：麻黄, 桂枝, 杏仁, 甘草, 黄芩  (5味)
    实际药材：麻黄, 桂枝, 杏仁, 甘草       (4味)
    
    TP = 4 (麻黄, 桂枝, 杏仁, 甘草)
    FP = 1 (黄芩 - 多开了)
    
    Precision = 4 / (4 + 1) = 0.80
    """
    tp = (preds * targets).sum()
    fp = (preds * (1 - targets)).sum()
    
    precision = tp / (tp + fp + 1e-7)  # 加小常数防止除零
    
    return precision.item()
```

### 4.4 Recall（召回率）

#### 4.4.1 定义

$$Recall = \frac{TP}{TP + FN} = \frac{\text{正确预测的药材数}}{\text{实际应有的药材总数}}$$

**含义**：在实际应该有的药材中，被模型正确预测的比例。

**中医场景解释**：
- 高Recall：不漏开药材，该开的都开了
- 低Recall：漏开了很多关键药材

#### 4.4.2 计算示例

```python
def compute_recall(preds, targets):
    """
    计算Recall
    
    示例：
    预测药材：麻黄, 桂枝, 杏仁           (3味)
    实际药材：麻黄, 桂枝, 杏仁, 甘草    (4味)
    
    TP = 3 (麻黄, 桂枝, 杏仁)
    FN = 1 (甘草 - 漏开了)
    
    Recall = 3 / (3 + 1) = 0.75
    """
    tp = (preds * targets).sum()
    fn = ((1 - preds) * targets).sum()
    
    recall = tp / (tp + fn + 1e-7)
    
    return recall.item()
```

### 4.5 F1 Score

#### 4.5.1 定义

$$F1 = \frac{2 \times Precision \times Recall}{Precision + Recall}$$

**含义**：Precision和Recall的调和平均数，综合评价指标。

**为什么用调和平均而不是算术平均？**
```
算术平均：(Precision + Recall) / 2
调和平均：2 * Precision * Recall / (Precision + Recall)

示例：
Precision = 1.0, Recall = 0.01

算术平均 = (1.0 + 0.01) / 2 = 0.505  # 看起来还行
调和平均 = 2 * 1.0 * 0.01 / 1.01 = 0.0198  # 惩罚极端不平衡

调和平均对极端值更敏感，要求两个指标都要高
```

#### 4.5.2 计算示例

```python
def compute_f1(preds, targets):
    """
    计算F1 Score
    
    示例：
    预测药材：麻黄, 桂枝, 杏仁, 黄芩     (4味)
    实际药材：麻黄, 桂枝, 杏仁, 甘草    (4味)
    
    TP = 3 (麻黄, 桂枝, 杏仁)
    FP = 1 (黄芩 - 多开)
    FN = 1 (甘草 - 漏开)
    
    Precision = 3 / 4 = 0.75
    Recall = 3 / 4 = 0.75
    F1 = 2 * 0.75 * 0.75 / (0.75 + 0.75) = 0.75
    """
    tp = (preds * targets).sum()
    fp = (preds * (1 - targets)).sum()
    fn = ((1 - preds) * targets).sum()
    
    precision = tp / (tp + fp + 1e-7)
    recall = tp / (tp + fn + 1e-7)
    
    f1 = 2 * precision * recall / (precision + recall + 1e-7)
    
    return f1.item()
```

### 4.6 指标对比分析

```
不同场景下的指标表现：
┌─────────────────────────────────────────────────────────────────┐
│ 场景1：完美预测                                                  │
│ 预测：麻黄, 桂枝, 杏仁, 甘草                                     │
│ 实际：麻黄, 桂枝, 杏仁, 甘草                                     │
│ Precision = 1.00, Recall = 1.00, F1 = 1.00                      │
├─────────────────────────────────────────────────────────────────┤
│ 场景2：多开药材                                                  │
│ 预测：麻黄, 桂枝, 杏仁, 甘草, 黄芩, 黄连                         │
│ 实际：麻黄, 桂枝, 杏仁, 甘草                                     │
│ TP=4, FP=2, FN=0                                                │
│ Precision = 4/6 = 0.67, Recall = 4/4 = 1.00, F1 = 0.80          │
├─────────────────────────────────────────────────────────────────┤
│ 场景3：漏开药材                                                  │
│ 预测：麻黄, 桂枝                                                 │
│ 实际：麻黄, 桂枝, 杏仁, 甘草                                     │
│ TP=2, FP=0, FN=2                                                │
│ Precision = 2/2 = 1.00, Recall = 2/4 = 0.50, F1 = 0.67          │
├─────────────────────────────────────────────────────────────────┤
│ 场景4：既多开又漏开                                              │
│ 预测：麻黄, 桂枝, 黄芩                                           │
│ 实际：麻黄, 桂枝, 杏仁, 甘草                                     │
│ TP=2, FP=1, FN=2                                                │
│ Precision = 2/3 = 0.67, Recall = 2/4 = 0.50, F1 = 0.57          │
└─────────────────────────────────────────────────────────────────┘
```

### 4.7 中医场景的特殊考虑

#### 4.7.1 多开 vs 漏开的严重性

```
在中医方剂推荐中：
┌─────────────────────────────────────────────────────┐
│ 漏开关键药材（FN）：                                 │
│ - 君药漏开 → 方剂失去主要治疗作用                    │
│ - 臣药漏开 → 疗效大打折扣                            │
│ - 后果：治疗效果不佳，延误病情                       │
│                                                      │
│ 多开辅助药材（FP）：                                 │
│ - 多开调和药（甘草、大枣）→ 影响较小                 │
│ - 多开功效相近药材 → 可能增强疗效                    │
│ - 后果：增加成本，可能影响口感                        │
└─────────────────────────────────────────────────────┘

结论：漏开比多开更严重，Recall应该比Precision更重要
```

#### 4.7.2 加权F1

```python
def weighted_f1(precision, recall, beta=2):
    """
    加权F1（F-beta score）
    
    beta > 1: 更重视Recall
    beta < 1: 更重视Precision
    beta = 1: 标准F1
    
    在中医场景中，建议beta=2，更重视不漏开药材
    """
    return (1 + beta**2) * precision * recall / (beta**2 * precision + recall + 1e-7)

# 示例
precision = 0.80
recall = 0.90

f1 = 2 * precision * recall / (precision + recall)  # 0.847
f2 = weighted_f1(precision, recall, beta=2)  # 0.878，更重视Recall
```

---

## 5. 深度学习原理与特征提取

### 5.1 神经网络基础

#### 5.1.1 什么是神经网络？

神经网络是一种模拟人脑神经元连接的数学模型，由多个"层"组成：

```
神经网络结构：
┌─────────────────────────────────────────────────────┐
│ 输入层          隐藏层           输出层              │
│                                                      │
│  [x₁] ─┐                                      [y₁] │
│        ├────→ [h₁] ─┐                          │
│  [x₂] ─┤            ├────→ [h₃] ────→         [y₂] │
│        ├────→ [h₂] ─┘                          │
│  [x₃] ─┘                                      [y₃] │
│                                                      │
│  症状向量        特征提取         药材概率           │
│  (120维)         (512维)          (89维)            │
└─────────────────────────────────────────────────────┘

每个连接都有一个权重（weight），训练就是学习这些权重的过程
```

#### 5.1.2 神经元的工作原理

```python
class Neuron:
    """
    单个神经元的计算
    
    输出 = 激活函数(权重 × 输入 + 偏置)
    """
    def __init__(self, input_size):
        self.weights = np.random.randn(input_size) * 0.01
        self.bias = 0.0
    
    def forward(self, x):
        # 线性变换
        z = np.dot(self.weights, x) + self.bias
        # 非线性激活
        output = self.activation(z)
        return output
    
    def activation(self, z):
        """ReLU激活函数"""
        return max(0, z)

# 示例
neuron = Neuron(input_size=120)  # 接收120维症状向量
output = neuron.forward(symptom_vector)
```

#### 5.1.3 为什么需要非线性？

```
没有非线性激活函数：
┌─────────────────────────────────────────────────────┐
│ 多层线性变换 = 单层线性变换                          │
│                                                      │
│ y = W₂(W₁x + b₁) + b₂                              │
│   = W₂W₁x + W₂b₁ + b₂                              │
│   = W'x + b'                                        │
│                                                      │
│ 无法学习复杂的非线性关系！                           │
└─────────────────────────────────────────────────────┘

加入非线性激活函数：
┌─────────────────────────────────────────────────────┐
│ y = W₂·ReLU(W₁x + b₁) + b₂                         │
│                                                      │
│ 可以拟合任意复杂的函数（通用近似定理）               │
└─────────────────────────────────────────────────────┘
```

### 5.2 常用激活函数

#### 5.2.1 ReLU

```python
def relu(x):
    """
    ReLU (Rectified Linear Unit)
    
    f(x) = max(0, x)
    
    优点：
    - 计算简单
    - 缓解梯度消失
    - 稀疏激活（部分神经元输出为0）
    
    缺点：
    - 负值区域梯度为0（神经元死亡）
    """
    return np.maximum(0, x)
```

#### 5.2.2 GELU

```python
def gelu(x):
    """
    GELU (Gaussian Error Linear Unit)
    
    f(x) = x * Φ(x)，其中Φ是标准正态分布的CDF
    
    优点：
    - 比ReLU更平滑
    - 在Transformer中表现更好
    - 负值区域有非零梯度
    
    本项目使用GELU作为主要激活函数
    """
    return x * 0.5 * (1 + np.tanh(np.sqrt(2/np.pi) * (x + 0.044715 * x**3)))
```

#### 5.2.3 Sigmoid

```python
def sigmoid(x):
    """
    Sigmoid函数
    
    f(x) = 1 / (1 + e^(-x))
    
    输出范围：(0, 1)
    
    用途：
    - 二分类输出层
    - 多标签分类的每个标签独立预测
    
    本项目输出层使用Sigmoid
    """
    return 1 / (1 + np.exp(-x))
```

### 5.3 特征提取详解

#### 5.3.1 什么是特征提取？

```
特征提取：将原始数据转换为更有意义的表示

原始输入 ──────→ 特征提取 ──────→ 特征表示
(症状向量)                        (隐藏层输出)

示例：
原始输入：[1,0,0,1,0,1,...]  # 120维multi-hot向量
         恶寒  无汗  头痛

特征提取后：[0.2, 0.8, 0.1, 0.9, ...]  # 512维特征向量
            这些特征捕捉了症状之间的复杂关系
```

#### 5.3.2 Multi-hot编码

```python
def multi_hot_encoding(symptoms, symptom_vocab):
    """
    Multi-hot编码
    
    将症状列表转换为向量表示
    
    参数：
        symptoms: 症状列表，如 ["恶寒", "发热", "无汗"]
        symptom_vocab: 症状词表，如 {"恶寒": 0, "发热": 1, ...}
    
    返回：
        向量，如 [1, 1, 1, 0, 0, ..., 0]  # 120维
    
    与One-hot的区别：
    - One-hot：只有一个位置为1（单标签）
    - Multi-hot：多个位置可以为1（多标签）
    """
    vector = np.zeros(len(symptom_vocab))
    for symptom in symptoms:
        if symptom in symptom_vocab:
            vector[symptom_vocab[symptom]] = 1.0
    return vector

# 示例
symptom_vocab = {"恶寒": 0, "发热": 1, "无汗": 2, "头痛": 3, ...}
symptoms = ["恶寒", "发热", "无汗"]
vector = multi_hot_encoding(symptoms, symptom_vocab)
# 结果：[1, 1, 1, 0, 0, ..., 0]
```

#### 5.3.3 嵌入层

```python
class EmbeddingLayer(nn.Module):
    """
    嵌入层：将稀疏的multi-hot向量转换为稠密的嵌入向量
    
    为什么需要嵌入层？
    1. Multi-hot向量是稀疏的（大部分为0）
    2. 嵌入向量是稠密的（所有维度都有值）
    3. 嵌入向量可以学习症状之间的语义关系
    """
    def __init__(self, input_dim, embed_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, embed_dim)
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.activation = nn.GELU()
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        """
        输入：[batch_size, input_dim]  # 如 [64, 120]
        输出：[batch_size, embed_dim]  # 如 [64, 256]
        """
        # 线性变换
        x = self.linear(x)  # [64, 256]
        
        # 层归一化（稳定训练）
        x = self.layer_norm(x)
        
        # 非线性激活
        x = self.activation(x)
        
        # Dropout（防止过拟合）
        x = self.dropout(x)
        
        return x
```

#### 5.3.4 特征编码器

```python
class Encoder(nn.Module):
    """
    特征编码器：进一步提取高级特征
    
    结构：
    - 两层全连接网络
    - 残差连接
    - 层归一化
    """
    def __init__(self, embed_dim, hidden_dim):
        super().__init__()
        
        # 第一层
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.norm1 = nn.LayerNorm(hidden_dim)
        
        # 第二层
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.norm2 = nn.LayerNorm(hidden_dim)
        
        self.activation = nn.GELU()
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        """
        输入：[batch_size, embed_dim]  # 如 [64, 256]
        输出：[batch_size, hidden_dim]  # 如 [64, 512]
        """
        # 第一层 + 残差（需要投影维度）
        residual = self.fc1(x)  # 投影到hidden_dim
        x = self.norm1(residual)
        x = self.activation(x)
        x = self.dropout(x)
        
        # 第二层 + 残差
        residual = x
        x = self.fc2(x)
        x = self.norm2(x + residual)  # 残差连接
        x = self.activation(x)
        
        return x
```

### 5.4 层归一化（Layer Normalization）

#### 5.4.1 为什么需要归一化？

```
问题：内部协变量偏移（Internal Covariate Shift）
┌─────────────────────────────────────────────────────┐
│ 随着训练进行，每层输入的分布会发生变化                │
│ 这会导致：                                           │
│ 1. 训练不稳定                                        │
│ 2. 需要更小的学习率                                  │
│ 3. 收敛速度慢                                        │
└─────────────────────────────────────────────────────┘

解决：归一化每层的输入，使其分布稳定
```

#### 5.4.2 Layer Normalization vs Batch Normalization

```python
# Batch Normalization：对每个特征在batch维度上归一化
# Layer Normalization：对每个样本在特征维度上归一化

def layer_norm(x, eps=1e-5):
    """
    Layer Normalization
    
    对于输入 x [batch_size, features]
    对每个样本独立归一化
    
    优点：
    1. 不依赖batch size
    2. 适合序列数据和变长输入
    3. 在Transformer中广泛使用
    """
    mean = x.mean(dim=-1, keepdim=True)
    std = x.std(dim=-1, keepdim=True)
    return (x - mean) / (std + eps)

# 示例
x = torch.randn(64, 512)  # [batch_size, hidden_dim]
normalized = layer_norm(x)
# 每个样本的512维特征被归一化到均值0、方差1
```

### 5.5 Dropout正则化

#### 5.5.1 为什么需要Dropout？

```
过拟合问题：
┌─────────────────────────────────────────────────────┐
│ 模型在训练集上表现很好，但在测试集上表现差            │
│                                                      │
│ 原因：模型过度依赖某些神经元，形成"共适应"           │
└─────────────────────────────────────────────────────┘

Dropout解决：
┌─────────────────────────────────────────────────────┐
│ 训练时随机"关闭"一部分神经元                         │
│ 强制网络学习更鲁棒的特征                             │
│                                                      │
│ 测试时使用所有神经元，但输出乘以保留概率             │
└─────────────────────────────────────────────────────┘
```

#### 5.5.2 Dropout实现

```python
class Dropout:
    """
    Dropout实现
    
    训练时：以概率p随机将神经元输出置为0
    测试时：所有神经元都工作，输出乘以(1-p)
    """
    def __init__(self, p=0.5):
        self.p = p  # 丢弃概率
    
    def forward(self, x, training=True):
        if not training:
            return x  # 测试时不dropout
        
        # 生成mask
        mask = (np.random.rand(*x.shape) > self.p).astype(float)
        
        # 应用mask并缩放（inverted dropout）
        return x * mask / (1 - self.p)

# PyTorch实现
dropout = nn.Dropout(p=0.3)
x = torch.randn(64, 512)
output = dropout(x)  # 训练时30%的神经元被置为0
```

---

## 6. 注意力机制详解

### 6.1 什么是注意力机制？

#### 6.1.1 直觉理解

```
人类视觉注意力：
┌─────────────────────────────────────────────────────┐
│ 当你看一张图片时，你不会同时关注所有区域             │
│ 而是根据任务，将注意力集中在相关区域                 │
│                                                      │
│ 例如：看人脸时，注意力集中在眼睛、鼻子、嘴巴         │
│      看风景时，注意力集中在主要景物                  │
└─────────────────────────────────────────────────────┘

神经网络中的注意力：
┌─────────────────────────────────────────────────────┐
│ 让模型学会"关注"输入的不同部分                       │
│                                                      │
│ 在方剂推荐中：                                       │
│ - 麻黄应该关注：恶寒、无汗、喘                       │
│ - 甘草应该关注：乏力、气短、需要调和诸药             │
│ - 黄连应该关注：口苦、心烦、舌红                     │
└─────────────────────────────────────────────────────┘
```

#### 6.1.2 数学表达

```
注意力机制的核心：
┌─────────────────────────────────────────────────────┐
│ Attention(Q, K, V) = softmax(QK^T / √d_k) V        │
│                                                      │
│ Q (Query)：查询向量 - "我在找什么"                   │
│ K (Key)：键向量 - "我是什么"                         │
│ V (Value)：值向量 - "我的内容是什么"                 │
│ d_k：缩放因子，防止点积过大                          │
└─────────────────────────────────────────────────────┘

计算过程：
1. 计算Query和Key的相似度
2. 用softmax归一化得到注意力权重
3. 用权重对Value加权求和
```

### 6.2 标签特定注意力（Label-Specific Attention）

#### 6.2.1 为什么需要标签特定注意力？

```
传统方法的问题：
┌─────────────────────────────────────────────────────┐
│ 所有药材共享同一套特征                               │
│                                                      │
│ 症状编码器 ──→ 共享特征 ──→ 所有药材预测             │
│                                                      │
│ 问题：                                               │
│ - 麻黄和甘草关注的症状不同                           │
│ - 共享特征无法捕捉这种差异                           │
└─────────────────────────────────────────────────────┘

标签特定注意力的解决：
┌─────────────────────────────────────────────────────┐
│ 每个药材学习自己的特征表示                           │
│                                                      │
│ 症状编码器 ──→ 麻黄专用特征 ──→ 麻黄预测             │
│            ──→ 甘草专用特征 ──→ 甘草预测             │
│            ──→ 黄连专用特征 ──→ 黄连预测             │
│                                                      │
│ 每个药材"看到"不同的症状组合                         │
└─────────────────────────────────────────────────────┘
```

#### 6.2.2 实现详解

```python
class LabelSpecificAttention(nn.Module):
    """
    标签特定注意力机制
    
    核心思想：每个标签（药材）学习自己的注意力权重
    
    直觉：
    - 麻黄的Query：关注"恶寒、无汗、喘"
    - 甘草的Query：关注"乏力、气短、需要调和"
    - 黄连的Query：关注"口苦、心烦、舌红"
    """
    def __init__(self, hidden_dim, label_dim):
        super().__init__()
        
        # 注意力计算网络
        # 输入：症状编码 + 标签嵌入
        # 输出：注意力权重
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim + label_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1),
        )
    
    def forward(self, x, label_embed):
        """
        参数：
            x: 症状编码 [batch_size, hidden_dim]
            label_embed: 标签嵌入 [batch_size, num_labels, label_dim]
        
        返回：
            label_specific_features: [batch_size, num_labels, hidden_dim]
        
        计算过程：
        1. 将症状编码扩展到每个标签
        2. 拼接症状编码和标签嵌入
        3. 计算每个标签的注意力权重
        4. 用权重对症状编码加权
        """
        batch_size, num_labels, label_dim = label_embed.shape
        
        # 步骤1：扩展症状编码
        # x: [batch, hidden] -> [batch, num_labels, hidden]
        x_expanded = x.unsqueeze(1).expand(-1, num_labels, -1)
        
        # 步骤2：拼接症状编码和标签嵌入
        # [batch, num_labels, hidden + label_dim]
        combined = torch.cat([x_expanded, label_embed], dim=-1)
        
        # 步骤3：计算注意力权重
        # [batch, num_labels, 1] -> [batch, num_labels]
        attention_scores = self.attention(combined).squeeze(-1)
        attention_weights = F.softmax(attention_scores, dim=-1)
        
        # 步骤4：加权求和
        # [batch, num_labels, hidden]
        label_specific = torch.einsum('bl,bld->bld', attention_weights, x_expanded)
        
        return label_specific
```

#### 6.2.3 注意力权重可视化

```python
def visualize_attention(model, symptoms, symptom_vocab, herb_vocab, top_k=5):
    """
    可视化注意力权重
    
    展示每个药材最关注的症状
    """
    # 准备输入
    symptom_vec = torch.zeros(len(symptom_vocab))
    for s in symptoms:
        if s in symptom_vocab:
            symptom_vec[symptom_vocab[s]] = 1.0
    
    # 获取注意力权重
    with torch.no_grad():
        # ... 前向传播获取attention_weights
    
    # 打印结果
    idx_to_symptom = {v: k for k, v in symptom_vocab.items()}
    idx_to_herb = {v: k for k, v in herb_vocab.items()}
    
    for herb_idx in range(len(herb_vocab)):
        herb_name = idx_to_herb[herb_idx]
        weights = attention_weights[0, herb_idx]
        
        # 获取top-k症状
        top_indices = torch.topk(weights, min(top_k, len(symptoms))).indices
        top_symptoms = [(idx_to_symptom[idx.item()], weights[idx].item()) 
                        for idx in top_indices if idx.item() < len(symptom_vocab)]
        
        print(f"\n{herb_name} 关注的症状：")
        for symptom, weight in top_symptoms:
            print(f"  {symptom}: {weight:.4f}")

# 示例输出
"""
麻黄 关注的症状：
  恶寒: 0.3521
  无汗: 0.2847
  喘: 0.2156
  身痛: 0.0876
  头痛: 0.0600

甘草 关注的症状：
  乏力: 0.3012
  气短: 0.2543
  恶寒: 0.1521
  头痛: 0.1456
  发热: 0.1468
"""
```

### 6.3 多头注意力（Multi-Head Attention）

#### 6.3.1 为什么需要多头？

```
单头注意力的局限：
┌─────────────────────────────────────────────────────┐
│ 只能学习一种注意力模式                               │
│                                                      │
│ 例如：只能学习"症状-药材"的直接关系                  │
│ 无法同时学习：                                       │
│ - 君臣佐使的配伍关系                                 │
│ - 寒热虚实的辨证关系                                 │
│ - 脏腑经络的归经关系                                 │
└─────────────────────────────────────────────────────┘

多头注意力的解决：
┌─────────────────────────────────────────────────────┐
│ 多个"头"并行学习不同的注意力模式                     │
│                                                      │
│ 头1：学习君臣配伍关系                                │
│ 头2：学习寒热辨证关系                                │
│ 头3：学习脏腑归经关系                                │
│ ...                                                  │
│                                                      │
│ 最后将所有头的结果拼接融合                           │
└─────────────────────────────────────────────────────┘
```

#### 6.3.2 实现详解

```python
class MultiHeadAttention(nn.Module):
    """
    多头注意力机制
    
    核心思想：并行运行多个注意力头，每个头学习不同的模式
    """
    def __init__(self, hidden_dim, num_heads=8, dropout=0.1):
        super().__init__()
        assert hidden_dim % num_heads == 0, "hidden_dim必须能被num_heads整除"
        
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        # Q, K, V的线性投影
        self.q_proj = nn.Linear(hidden_dim, hidden_dim)
        self.k_proj = nn.Linear(hidden_dim, hidden_dim)
        self.v_proj = nn.Linear(hidden_dim, hidden_dim)
        
        # 输出投影
        self.out_proj = nn.Linear(hidden_dim, hidden_dim)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = self.head_dim ** -0.5
    
    def forward(self, query, key, value):
        """
        参数：
            query: [batch_size, seq_len, hidden_dim]
            key: [batch_size, seq_len, hidden_dim]
            value: [batch_size, seq_len, hidden_dim]
        
        返回：
            output: [batch_size, seq_len, hidden_dim]
            attention_weights: [batch_size, num_heads, seq_len, seq_len]
        """
        batch_size, seq_len, _ = query.shape
        
        # 线性投影
        Q = self.q_proj(query)  # [batch, seq, hidden]
        K = self.k_proj(key)
        V = self.v_proj(value)
        
        # 重塑为多头形式
        # [batch, seq, hidden] -> [batch, num_heads, seq, head_dim]
        Q = Q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # 计算注意力分数
        # [batch, num_heads, seq, seq]
        attention_scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale
        
        # Softmax归一化
        attention_weights = F.softmax(attention_scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # 加权求和
        # [batch, num_heads, seq, head_dim]
        output = torch.matmul(attention_weights, V)
        
        # 重塑回原始形状
        # [batch, num_heads, seq, head_dim] -> [batch, seq, hidden]
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, -1)
        
        # 输出投影
        output = self.out_proj(output)
        
        return output, attention_weights
```

### 6.4 标签相关性建模

#### 6.4.1 为什么需要建模标签相关性？

```
药材之间的配伍关系：
┌─────────────────────────────────────────────────────┐
│ 麻黄汤中：                                           │
│ - 麻黄 + 桂枝：相须配伍，增强发汗                    │
│ - 麻黄 + 杏仁：宣降相因，止咳平喘                    │
│ - 四药合用：协同增效                                 │
│                                                      │
│ 如果模型预测了"麻黄"，那么"桂枝"出现的概率应该增加   │
│ 这种相关性需要被建模                                 │
└─────────────────────────────────────────────────────┘
```

#### 6.4.2 实现详解

```python
class LabelCorrelation(nn.Module):
    """
    标签相关性建模
    
    使用自注意力机制建模药材之间的相关性
    """
    def __init__(self, hidden_dim, num_heads=8, dropout=0.3):
        super().__init__()
        
        # 自注意力：药材之间互相"看"
        self.self_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True
        )
        
        # 层归一化
        self.norm = nn.LayerNorm(hidden_dim)
    
    def forward(self, label_features):
        """
        参数：
            label_features: [batch_size, num_labels, hidden_dim]
                           每个药材的特征表示
        
        返回：
            correlated_features: [batch_size, num_labels, hidden_dim]
                                融合了相关性的特征
        
        计算过程：
        1. 每个药材的特征作为Query、Key、Value
        2. 通过自注意力，每个药材"看到"其他药材
        3. 学习药材之间的相关性
        """
        # 自注意力
        # Q=K=V=label_features
        attn_output, _ = self.self_attention(
            query=label_features,
            key=label_features,
            value=label_features
        )
        
        # 残差连接 + 层归一化
        output = self.norm(label_features + attn_output)
        
        return output
```

---

## 7. 模型架构设计

### 7.1 LSAN架构总览

```
LSAN (Label-Specific Attention Network) 架构：
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  输入：症状向量 [batch, 120]                                     │
│         ↓                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 嵌入层                                                   │    │
│  │ Linear(120, 256) → LayerNorm → GELU → Dropout           │    │
│  └─────────────────────────────────────────────────────────┘    │
│         ↓                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 编码器                                                   │    │
│  │ Linear(256, 512) → LayerNorm → GELU → Dropout           │    │
│  │ Linear(512, 512) → LayerNorm → GELU                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│         ↓                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 标签嵌入（可学习参数）                                    │    │
│  │ [89, 128] - 每个药材一个嵌入向量                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│         ↓                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 标签特定注意力                                           │    │
│  │ 每个药材学习自己的特征权重                               │    │
│  │ 输出：[batch, 89, 512]                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│         ↓                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 标签相关性建模（自注意力）                                │    │
│  │ 建模药材之间的配伍关系                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│         ↓                                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 输出层                                                   │    │
│  │ 标签特定输出 + 全局输出 → 药材概率 [batch, 89]          │    │
│  └─────────────────────────────────────────────────────────┘    │
│         ↓                                                        │
│  输出：药材概率 [batch, 89]                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 完整模型代码

```python
class LSANPlus(nn.Module):
    """
    LSAN+ 模型
    
    Label-Specific Attention Network with Label Correlation
    
    创新点：
    1. 标签特定注意力：每个药材学习自己的特征表示
    2. 标签相关性：建模药材之间的配伍关系
    3. 双路输出：结合标签特定输出和全局输出
    """
    def __init__(self, num_symptoms, num_herbs, embed_dim=256, hidden_dim=512, 
                 label_dim=128, dropout=0.3):
        super().__init__()
        
        self.num_herbs = num_herbs
        
        # 1. 症状嵌入层
        self.symptom_embed = nn.Sequential(
            nn.Linear(num_symptoms, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        
        # 2. 编码器
        self.encoder = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
        )
        
        # 3. 标签嵌入（可学习参数）
        # 每个药材有一个128维的嵌入向量
        self.label_embed = nn.Parameter(
            torch.randn(num_herbs, label_dim) * 0.02
        )
        
        # 4. 标签特定注意力
        self.label_attention = LabelSpecificAttention(hidden_dim, label_dim)
        
        # 5. 标签相关性建模
        self.label_correlation = nn.MultiheadAttention(
            hidden_dim, num_heads=8, batch_first=True, dropout=dropout
        )
        self.norm = nn.LayerNorm(hidden_dim)
        
        # 6. 标签特定输出头
        self.label_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
        )
        
        # 7. 全局输出头
        self.global_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_herbs),
        )
        
        # 8. 药材数量预测头（辅助任务）
        self.count_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, 20),  # 最多预测20味药材
        )
    
    def forward(self, symptoms):
        """
        前向传播
        
        参数：
            symptoms: 症状向量 [batch_size, num_symptoms]
        
        返回：
            herb_logits: 药材预测logits [batch_size, num_herbs]
            count_logits: 药材数量预测 [batch_size, 20]
        """
        batch_size = symptoms.size(0)
        
        # 1. 症状嵌入
        symptom_embed = self.symptom_embed(symptoms)  # [batch, 256]
        
        # 2. 编码
        encoded = self.encoder(symptom_embed)  # [batch, 512]
        
        # 3. 标签嵌入扩展
        label_embed = self.label_embed.unsqueeze(0).expand(batch_size, -1, -1)
        # [batch, num_herbs, label_dim]
        
        # 4. 标签特定特征
        label_features = self.label_attention(encoded, label_embed)
        # [batch, num_herbs, hidden_dim]
        
        # 5. 标签相关性
        corr_features, _ = self.label_correlation(
            label_features, label_features, label_features
        )
        label_features = self.norm(label_features + corr_features)
        # [batch, num_herbs, hidden_dim]
        
        # 6. 标签特定输出
        label_logits = self.label_head(label_features).squeeze(-1)
        # [batch, num_herbs]
        
        # 7. 全局输出
        global_logits = self.global_head(encoded)
        # [batch, num_herbs]
        
        # 8. 融合输出
        herb_logits = label_logits + global_logits
        
        # 9. 药材数量预测
        count_logits = self.count_head(encoded)
        
        return herb_logits, count_logits
    
    def predict(self, symptoms, threshold=0.5, min_herbs=3, max_herbs=12):
        """
        预测接口
        
        参数：
            symptoms: 症状向量 [num_symptoms]
            threshold: 预测阈值
            min_herbs: 最少药材数
            max_herbs: 最多药材数
        
        返回：
            dict: 包含预测结果
        """
        self.eval()
        with torch.no_grad():
            symptoms = symptoms.unsqueeze(0)  # [1, num_symptoms]
            herb_logits, count_logits = self.forward(symptoms)
            
            # 药材概率
            herb_probs = torch.sigmoid(herb_logits[0])
            
            # 预测药材数量
            predicted_count = torch.argmax(count_logits[0]).item() + 1
            predicted_count = max(min_herbs, min(max_herbs, predicted_count))
            
            # 选择top-k药材
            top_k_indices = torch.topk(herb_probs, predicted_count).indices
            
            return {
                'herb_probs': herb_probs,
                'predicted_herbs': top_k_indices.tolist(),
                'predicted_count': predicted_count,
            }
```

---

## 8. 损失函数设计详解

### 8.1 二元交叉熵损失（BCE）

#### 8.1.1 基本形式

$$L_{BCE} = -\frac{1}{N}\sum_{i=1}^{N}\sum_{j=1}^{M}[y_{ij}\log(\hat{y}_{ij}) + (1-y_{ij})\log(1-\hat{y}_{ij})]$$

其中：
- $N$：样本数量
- $M$：标签数量（药材数）
- $y_{ij}$：第$i$个样本第$j$个标签的真实值（0或1）
- $\hat{y}_{ij}$：预测概率

#### 8.1.2 直觉理解

```python
def bce_loss(pred, target):
    """
    二元交叉熵损失
    
    对于每个药材：
    - 如果实际有该药材（y=1）：惩罚预测概率低的情况
    - 如果实际无该药材（y=0）：惩罚预测概率高的情况
    """
    loss = 0
    
    for i in range(len(target)):
        if target[i] == 1:
            # 实际有，预测概率越低，损失越大
            loss += -np.log(pred[i] + 1e-7)
        else:
            # 实际无，预测概率越高，损失越大
            loss += -np.log(1 - pred[i] + 1e-7)
    
    return loss / len(target)

# 示例
pred = [0.9, 0.3, 0.8, 0.1]  # 预测概率
target = [1, 0, 1, 0]         # 真实标签

# 计算：
# 药材1：实际有，预测0.9 → loss = -log(0.9) = 0.105
# 药材2：实际无，预测0.3 → loss = -log(0.7) = 0.357
# 药材3：实际有，预测0.8 → loss = -log(0.8) = 0.223
# 药材4：实际无，预测0.1 → loss = -log(0.9) = 0.105
# 平均loss = (0.105 + 0.357 + 0.223 + 0.105) / 4 = 0.197
```

### 8.2 非对称损失

#### 8.2.1 为什么需要非对称惩罚？

```
医疗场景的特殊性：
┌─────────────────────────────────────────────────────┐
│ 漏开药材（False Negative）：                         │
│ - 漏开君药 → 方剂失去主要治疗作用                    │
│ - 漏开臣药 → 疗效大打折扣                            │
│ - 后果严重：治疗无效，延误病情                       │
│                                                      │
│ 多开药材（False Positive）：                         │
│ - 多开调和药（甘草）→ 影响较小                       │
│ - 多开功效相近药材 → 可能增强疗效                    │
│ - 后果较轻：增加成本，可能影响口感                    │
└─────────────────────────────────────────────────────┘

结论：漏开比多开更严重，应该给予更大的惩罚
```

#### 8.2.2 非对称损失设计

```python
class AsymmetricLoss(nn.Module):
    """
    非对称损失函数
    
    对漏开（FN）和多开（FP）给予不同的惩罚权重
    
    参数：
        alpha_fn: 漏开惩罚权重（建议0.85）
        alpha_fp: 多开惩罚权重（建议0.15）
    """
    def __init__(self, alpha_fn=0.85, alpha_fp=0.15):
        super().__init__()
        self.alpha_fn = alpha_fn
        self.alpha_fp = alpha_fp
    
    def forward(self, logits, targets):
        """
        参数：
            logits: 模型输出 [batch, num_herbs]
            targets: 真实标签 [batch, num_herbs]
        
        计算：
            L = -α_fn * y * log(σ(z)) - α_fp * (1-y) * log(1-σ(z))
        
        其中：
            - y=1时（实际有）：惩罚漏开，权重α_fn
            - y=0时（实际无）：惩罚多开，权重α_fp
        """
        probs = torch.sigmoid(logits)
        
        # 漏开损失（y=1时）
        fn_loss = -self.alpha_fn * targets * torch.log(probs + 1e-7)
        
        # 多开损失（y=0时）
        fp_loss = -self.alpha_fp * (1 - targets) * torch.log(1 - probs + 1e-7)
        
        return (fn_loss + fp_loss).mean()

# 示例对比
loss_fn = AsymmetricLoss(alpha_fn=0.85, alpha_fp=0.15)

# 场景1：漏开关键药材
pred = torch.tensor([0.3])   # 预测概率低
target = torch.tensor([1.0])  # 实际有
loss1 = loss_fn(pred, target)  # 损失大

# 场景2：多开辅助药材
pred = torch.tensor([0.7])   # 预测概率高
target = torch.tensor([0.0])  # 实际无
loss2 = loss_fn(pred, target)  # 损失小

print(f"漏开损失: {loss1:.4f}")  # 约0.85 * 1.2 = 1.02
print(f"多开损失: {loss2:.4f}")  # 约0.15 * 1.2 = 0.18
```

### 8.3 组合损失

```python
class CombinedLoss(nn.Module):
    """
    组合损失函数
    
    结合多种损失：
    1. 非对称BCE损失
    2. 药材数量预测损失（辅助任务）
    3. 标签平滑（可选）
    """
    def __init__(self, alpha_fn=0.85, alpha_fp=0.15, count_weight=0.1, label_smoothing=0.0):
        super().__init__()
        self.alpha_fn = alpha_fn
        self.alpha_fp = alpha_fp
        self.count_weight = count_weight
        self.label_smoothing = label_smoothing
    
    def forward(self, herb_logits, count_logits, herb_targets, count_targets):
        """
        参数：
            herb_logits: 药材预测 [batch, num_herbs]
            count_logits: 数量预测 [batch, max_herbs]
            herb_targets: 药材标签 [batch, num_herbs]
            count_targets: 数量标签 [batch]
        """
        # 标签平滑
        if self.label_smoothing > 0:
            herb_targets = herb_targets * (1 - self.label_smoothing) + 0.5 * self.label_smoothing
        
        # 药材预测损失
        probs = torch.sigmoid(herb_logits)
        fn_loss = -self.alpha_fn * herb_targets * torch.log(probs + 1e-7)
        fp_loss = -self.alpha_fp * (1 - herb_targets) * torch.log(1 - probs + 1e-7)
        herb_loss = (fn_loss + fp_loss).mean()
        
        # 数量预测损失
        count_loss = F.cross_entropy(count_logits, count_targets)
        
        # 组合
        total_loss = herb_loss + self.count_weight * count_loss
        
        return total_loss, {'herb_loss': herb_loss.item(), 'count_loss': count_loss.item()}
```

---

## 9. 训练流程详解

### 9.1 优化器选择

#### 9.1.1 AdamW vs Adam

```
Adam优化器：
┌─────────────────────────────────────────────────────┐
│ m_t = β₁ * m_{t-1} + (1-β₁) * g_t       # 一阶矩   │
│ v_t = β₂ * v_{t-1} + (1-β₂) * g_t²      # 二阶矩   │
│ θ_t = θ_{t-1} - lr * m_t / (√v_t + ε)              │
│                                                      │
│ 问题：权重衰减（L2正则化）实现不正确                 │
└─────────────────────────────────────────────────────┘

AdamW优化器：
┌─────────────────────────────────────────────────────┐
│ 正确实现权重衰减：                                   │
│ θ_t = θ_{t-1} - lr * (m_t / (√v_t + ε) + wd * θ)   │
│                                                      │
│ 优点：                                               │
│ 1. 权重衰减与梯度更新解耦                           │
│ 2. 更好的泛化性能                                    │
│ 3. 在Transformer类模型中表现更好                    │
└─────────────────────────────────────────────────────┘
```

```python
from torch.optim import AdamW

optimizer = AdamW(
    model.parameters(),
    lr=0.001,           # 学习率
    betas=(0.9, 0.999), # 一阶、二阶矩衰减率
    eps=1e-8,           # 数值稳定性
    weight_decay=0.05   # 权重衰减（L2正则化）
)
```

### 9.2 学习率调度

#### 9.2.1 余弦退火

```python
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts

scheduler = CosineAnnealingWarmRestarts(
    optimizer,
    T_0=30,      # 初始周期长度（epochs）
    T_mult=2,    # 每次重启后周期倍增因子
    eta_min=1e-6 # 最小学习率
)

# 学习率变化示例：
# Epoch 1-30:   lr从0.001降到1e-6
# Epoch 31-90:  lr从0.001降到1e-6（周期翻倍）
# Epoch 91-210: lr从0.001降到1e-6（周期再翻倍）
```

#### 9.2.2 为什么用余弦退火？

```
学习率调度的作用：
┌─────────────────────────────────────────────────────┐
│ 训练初期：                                           │
│ - 较大学习率快速探索参数空间                         │
│ - 跳出局部最优                                       │
│                                                      │
│ 训练后期：                                           │
│ - 较小学习率精细调整                                 │
│ - 在最优解附近收敛                                   │
│                                                      │
│ 余弦退火特点：                                       │
│ - 平滑下降，不会突变                                 │
│ - 周期性重启，有机会跳出局部最优                     │
│ - 在深度学习中广泛使用                               │
└─────────────────────────────────────────────────────┘
```

### 9.3 早停策略

```python
class EarlyStopping:
    """
    早停策略
    
    当验证集性能连续patience轮不提升时，停止训练
    """
    def __init__(self, patience=100, min_delta=0.0001, mode='max'):
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.counter = 0
        self.best_score = None
        self.early_stop = False
    
    def __call__(self, score):
        if self.best_score is None:
            self.best_score = score
            return False
        
        if self.mode == 'max':
            if score > self.best_score + self.min_delta:
                self.best_score = score
                self.counter = 0
            else:
                self.counter += 1
        else:
            if score < self.best_score - self.min_delta:
                self.best_score = score
                self.counter = 0
            else:
                self.counter += 1
        
        if self.counter >= self.patience:
            self.early_stop = True
            return True
        
        return False
```

### 9.4 混合精度训练

```python
def train_with_amp(model, loader, criterion, optimizer, device):
    """
    混合精度训练（Automatic Mixed Precision）
    
    优点：
    1. 减少显存占用（约50%）
    2. 加速训练（约2倍）
    3. 保持精度不变
    """
    model.train()
    scaler = torch.amp.GradScaler('cuda')
    
    for symptoms, herbs in loader:
        symptoms = symptoms.to(device)
        herbs = herbs.to(device)
        
        optimizer.zero_grad()
        
        # 使用混合精度
        with torch.amp.autocast('cuda'):
            logits, count_logits = model(symptoms)
            loss = criterion(logits, herbs)
        
        # 梯度缩放
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
```

---

## 10. 模型评估与分析

### 10.1 测试集评估

```python
def evaluate_on_test_set(model, test_loader, device):
    """
    在测试集上评估模型
    """
    model.eval()
    
    total_tp, total_fp, total_fn = 0, 0, 0
    
    with torch.no_grad():
        for symptoms, herbs in test_loader:
            symptoms = symptoms.to(device)
            herbs = herbs.to(device)
            
            # 预测
            logits, _ = model(symptoms)
            probs = torch.sigmoid(logits)
            preds = (probs > 0.5).float()
            
            # 统计
            total_tp += (preds * herbs).sum().item()
            total_fp += (preds * (1 - herbs)).sum().item()
            total_fn += ((1 - preds) * herbs).sum().item()
    
    # 计算指标
    precision = total_tp / (total_tp + total_fp + 1e-7)
    recall = total_tp / (total_tp + total_fn + 1e-7)
    f1 = 2 * precision * recall / (precision + recall + 1e-7)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': total_tp,
        'fp': total_fp,
        'fn': total_fn,
    }
```

### 10.2 最终测试结果

```
======================================================================
  整体测试结果
======================================================================

  Precision: 0.9703
  Recall: 0.9702
  F1 Score: 0.9703
  
  平均预测药材数: 6.48
  平均目标药材数: 6.48
  
  TP (正确预测): 10,856
  FP (多开): 332
  FN (漏开): 332

======================================================================
```

### 10.3 典型案例分析

**成功案例：麻黄汤**
```
症状: 恶寒, 发热, 无汗, 头痛, 身痛, 喘
目标药材: 杏仁, 桂枝, 甘草, 麻黄
预测药材: 杏仁, 桂枝, 甘草, 麻黄
正确: 4, 多开: 0, 漏开: 0
F1=1.00 ✓

分析：症状完整，模型准确识别了麻黄汤的配伍
```

**失败案例：清营汤**
```
症状: 高热, 烦躁, 口渴
目标药材: 丹参, 水牛角, 玄参, 生地黄, 竹叶, 连翘, 金银花, 麦冬, 黄连
预测药材: 栀子, 黄柏, 黄芩, 黄连
正确: 1, 多开: 3, 漏开: 8
F1=0.15 ✗

分析：
1. 输入症状太少（仅3个），信息不足
2. "高热, 烦躁, 口渴"与黄连解毒汤症状重叠
3. 模型混淆了清营汤和黄连解毒汤

改进方向：
1. 增加症状描述的完整性
2. 引入更多区分性症状（如斑疹、舌绛）
```

---

## 11. 工程实践要点

### 11.1 项目结构

```
Chinese-medicine/
├── training/
│   ├── data_external/          # 数据目录
│   │   ├── train_data.json     # 训练集 (5,160样本)
│   │   ├── val_data.json       # 验证集 (1,720样本)
│   │   ├── test_data.json      # 测试集 (1,720样本)
│   │   ├── symptom_vocab.json  # 症状词表 (120个)
│   │   ├── herb_vocab.json     # 药材词表 (89个)
│   │   └── meta.json           # 元数据
│   ├── checkpoints_v18/        # 模型检查点
│   │   └── best_model.pt
│   └── scripts/
│       ├── download_datasets.py # 数据准备脚本
│       ├── run_v16_lsan_plus.py # 训练脚本
│       └── test_model.py        # 测试脚本
└── tutorials/
    └── deep_learning_tutorial.md
```

### 11.2 关键配置

```python
# 数据配置
DATA_CONFIG = {
    'train_ratio': 0.6,
    'val_ratio': 0.2,
    'test_ratio': 0.2,
    'augment_factor': 5,
    'random_seed': 42,
}

# 模型配置
MODEL_CONFIG = {
    'embed_dim': 256,
    'hidden_dim': 512,
    'label_dim': 128,
    'num_heads': 8,
    'dropout': 0.3,
}

# 训练配置
TRAIN_CONFIG = {
    'batch_size': 64,
    'learning_rate': 0.001,
    'weight_decay': 0.05,
    'epochs': 500,
    'patience': 100,
    'alpha_fn': 0.85,  # 漏开惩罚权重
    'alpha_fp': 0.15,  # 多开惩罚权重
}
```

---

## 12. 常见问题与解决方案

### 12.1 过拟合

**现象**：训练集F1很高，测试集F1很低

**解决方案**：
1. 增加Dropout
2. 增加权重衰减
3. 数据增强
4. 早停

### 12.2 欠拟合

**现象**：训练集和测试集F1都很低

**解决方案**：
1. 增加模型容量
2. 减少正则化
3. 增加训练时间
4. 调整学习率

### 12.3 类别不平衡

**现象**：某些药材出现频率很低

**解决方案**：
1. 损失函数加权
2. 过采样少数类
3. 阈值调整

---

## 总结

本教程从工程视角详细介绍了深度学习项目流程：

1. **项目背景**：理解中医方剂学的挑战和深度学习的优势
2. **问题定义**：明确多标签分类问题和标签相关性
3. **数据工程**：数据清洗、增强、划分的完整流程
4. **评价指标**：Precision、Recall、F1的详细计算和意义
5. **特征提取**：神经网络如何自动学习特征
6. **注意力机制**：标签特定注意力和多头注意力的原理
7. **模型设计**：LSAN架构的完整实现
8. **损失函数**：非对称损失的设计动机和实现
9. **训练流程**：优化器、学习率调度、早停策略
10. **模型评估**：测试集评估和案例分析

**关键经验**：
- 数据质量比数据量更重要
- 选择合适的模型架构事半功倍
- 损失函数设计要考虑业务场景
- 验证集是调参的指南针
- 测试集是最终裁判

---

## 参考资料

1. LSAN论文: "Label-Specific Document Representation for Multi-Label Text Classification" (EMNLP 2019)
2. Attention Is All You Need: Transformer论文 (NeurIPS 2017)
3. PyTorch官方文档: https://pytorch.org/docs/
4. 《方剂学》教材: 全国中医药行业高等教育规划教材

---

*本教程基于中医方剂推荐项目实践编写，代码已在项目中验证。*
