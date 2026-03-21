"""
TCM Formula Dataset Preparation

Data sources:
1. Classic formulas from TCM textbooks
2. Symptom variations for data augmentation
"""

import os
import json
import random
from typing import List, Dict, Any


DATASET_DIR = "data"


CLASSIC_FORMULAS = [
    {"formula": "麻黄汤", "symptoms": ["恶寒", "发热", "无汗", "头痛", "身痛", "喘"], "herbs": ["麻黄", "桂枝", "杏仁", "甘草"]},
    {"formula": "桂枝汤", "symptoms": ["发热", "恶风", "汗出", "头痛"], "herbs": ["桂枝", "白芍", "生姜", "大枣", "甘草"]},
    {"formula": "小柴胡汤", "symptoms": ["寒热往来", "胸胁苦满", "口苦", "咽干", "目眩", "心烦", "喜呕"], "herbs": ["柴胡", "黄芩", "人参", "半夏", "生姜", "大枣", "甘草"]},
    {"formula": "大柴胡汤", "symptoms": ["寒热往来", "胸胁苦满", "呕不止", "郁郁微烦", "心下痞硬", "大便不解"], "herbs": ["柴胡", "黄芩", "芍药", "半夏", "生姜", "枳实", "大枣", "大黄"]},
    {"formula": "四君子汤", "symptoms": ["气短", "乏力", "面色萎黄", "食欲不振", "语声低微"], "herbs": ["人参", "白术", "茯苓", "甘草"]},
    {"formula": "四物汤", "symptoms": ["头晕", "心悸", "失眠", "面色苍白", "月经不调"], "herbs": ["当归", "熟地黄", "白芍", "川芎"]},
    {"formula": "六君子汤", "symptoms": ["气短", "乏力", "食欲不振", "腹胀", "咳嗽", "痰多", "恶心"], "herbs": ["人参", "白术", "茯苓", "甘草", "陈皮", "半夏"]},
    {"formula": "归脾汤", "symptoms": ["心悸", "失眠", "健忘", "乏力", "食欲不振", "面色萎黄"], "herbs": ["人参", "白术", "茯苓", "当归", "龙眼肉", "酸枣仁", "远志", "木香", "甘草"]},
    {"formula": "逍遥散", "symptoms": ["胁痛", "口苦", "食欲不振", "月经不调", "乳房胀痛"], "herbs": ["柴胡", "当归", "白芍", "白术", "茯苓", "薄荷", "甘草"]},
    {"formula": "补中益气汤", "symptoms": ["气短", "乏力", "头晕", "自汗", "食欲不振", "脱肛"], "herbs": ["黄芪", "人参", "白术", "当归", "陈皮", "升麻", "柴胡", "甘草"]},
    {"formula": "肾气丸", "symptoms": ["腰痛", "畏寒", "乏力", "头晕", "耳鸣", "小便不利"], "herbs": ["熟地黄", "山药", "山茱萸", "茯苓", "泽泻", "牡丹皮", "附子", "肉桂"]},
    {"formula": "理中丸", "symptoms": ["腹痛", "腹泻", "恶心", "呕吐", "食欲不振", "畏寒"], "herbs": ["人参", "白术", "干姜", "甘草"]},
    {"formula": "二陈汤", "symptoms": ["咳嗽", "痰多", "恶心", "呕吐", "胸闷", "头晕"], "herbs": ["半夏", "陈皮", "茯苓", "甘草"]},
    {"formula": "平胃散", "symptoms": ["腹胀", "食欲不振", "恶心", "呕吐", "乏力"], "herbs": ["苍术", "厚朴", "陈皮", "甘草"]},
    {"formula": "银翘散", "symptoms": ["发热", "咳嗽", "咽干", "头痛", "口干", "咽喉肿痛"], "herbs": ["金银花", "连翘", "桔梗", "薄荷", "牛蒡子", "荆芥", "甘草"]},
    {"formula": "桑菊饮", "symptoms": ["咳嗽", "发热", "口干", "头痛", "咽痛"], "herbs": ["桑叶", "菊花", "杏仁", "连翘", "薄荷", "桔梗", "芦根", "甘草"]},
    {"formula": "玉屏风散", "symptoms": ["自汗", "畏寒", "乏力", "气短", "易感冒"], "herbs": ["黄芪", "白术", "防风"]},
    {"formula": "酸枣仁汤", "symptoms": ["失眠", "心悸", "头晕", "盗汗", "咽干"], "herbs": ["酸枣仁", "茯苓", "知母", "川芎", "甘草"]},
    {"formula": "血府逐瘀汤", "symptoms": ["头痛", "胸痛", "失眠", "心悸", "情绪不畅"], "herbs": ["桃仁", "红花", "当归", "生地黄", "川芎", "赤芍", "牛膝", "桔梗", "柴胡", "枳壳", "甘草"]},
    {"formula": "半夏泻心汤", "symptoms": ["腹胀", "恶心", "呕吐", "腹泻", "心下痞满"], "herbs": ["半夏", "黄芩", "干姜", "人参", "黄连", "大枣", "甘草"]},
    {"formula": "清营汤", "symptoms": ["高热", "烦躁", "口渴", "斑疹", "舌绛"], "herbs": ["水牛角", "生地黄", "玄参", "竹叶", "麦冬", "丹参", "黄连", "金银花", "连翘"]},
    {"formula": "龙胆泻肝汤", "symptoms": ["头痛", "目赤", "口苦", "胁痛", "耳鸣", "小便黄"], "herbs": ["龙胆草", "黄芩", "栀子", "泽泻", "木通", "车前子", "当归", "生地黄", "柴胡", "甘草"]},
    {"formula": "左金丸", "symptoms": ["胁痛", "口苦", "呕吐", "吞酸"], "herbs": ["黄连", "吴茱萸"]},
    {"formula": "一贯煎", "symptoms": ["胁痛", "口干", "咽干", "吞酸", "舌红少苔"], "herbs": ["北沙参", "麦冬", "当归", "生地黄", "枸杞子", "川楝子"]},
    {"formula": "四逆散", "symptoms": ["胁痛", "腹痛", "四肢不温", "脉弦"], "herbs": ["柴胡", "枳实", "芍药", "甘草"]},
    {"formula": "痛泻要方", "symptoms": ["腹痛", "腹泻", "泻后痛减", "脉弦"], "herbs": ["白术", "白芍", "陈皮", "防风"]},
    {"formula": "参苓白术散", "symptoms": ["腹泻", "乏力", "食欲不振", "腹胀", "面色萎黄"], "herbs": ["人参", "白术", "茯苓", "甘草", "山药", "莲子", "薏苡仁", "砂仁", "桔梗", "白扁豆"]},
    {"formula": "生脉散", "symptoms": ["气短", "乏力", "汗出", "口干"], "herbs": ["人参", "麦冬", "五味子"]},
    {"formula": "当归补血汤", "symptoms": ["乏力", "头晕", "面色苍白", "脉虚大"], "herbs": ["黄芪", "当归"]},
    {"formula": "炙甘草汤", "symptoms": ["心悸", "气短", "失眠", "盗汗"], "herbs": ["炙甘草", "生姜", "人参", "生地黄", "桂枝", "阿胶", "麦冬", "麻仁", "大枣"]},
    {"formula": "百合固金汤", "symptoms": ["咳嗽", "咳血", "咽喉干燥", "舌红少苔"], "herbs": ["百合", "熟地黄", "生地黄", "玄参", "贝母", "桔梗", "甘草", "芍药", "当归", "麦冬"]},
    {"formula": "麦门冬汤", "symptoms": ["咳嗽", "咽喉干燥", "咳痰不爽", "舌红少苔"], "herbs": ["麦冬", "半夏", "人参", "甘草", "粳米", "大枣"]},
    {"formula": "养阴清肺汤", "symptoms": ["咳嗽", "咽喉干燥", "声音嘶哑", "舌红少苔"], "herbs": ["生地黄", "玄参", "麦冬", "芍药", "牡丹皮", "贝母", "薄荷", "甘草"]},
    {"formula": "清燥救肺汤", "symptoms": ["咳嗽", "气短", "咽喉干燥", "心烦", "舌红少苔"], "herbs": ["桑叶", "石膏", "人参", "甘草", "胡麻仁", "阿胶", "麦冬", "杏仁", "枇杷叶"]},
    {"formula": "杏苏散", "symptoms": ["咳嗽", "恶寒", "头痛", "鼻塞", "咽干", "舌苔薄白"], "herbs": ["苏叶", "半夏", "茯苓", "前胡", "桔梗", "枳壳", "甘草", "生姜", "大枣", "杏仁", "陈皮"]},
    {"formula": "桑杏汤", "symptoms": ["咳嗽", "发热", "口干", "咽干", "舌苔薄黄"], "herbs": ["桑叶", "杏仁", "沙参", "贝母", "豆豉", "栀子", "梨皮"]},
    {"formula": "白虎汤", "symptoms": ["高热", "口渴", "汗出", "脉洪大"], "herbs": ["石膏", "知母", "甘草", "粳米"]},
    {"formula": "黄连解毒汤", "symptoms": ["高热", "烦躁", "口渴", "舌红苔黄"], "herbs": ["黄连", "黄芩", "黄柏", "栀子"]},
    {"formula": "犀角地黄汤", "symptoms": ["高热", "斑疹", "出血", "舌绛"], "herbs": ["水牛角", "生地黄", "芍药", "牡丹皮"]},
    {"formula": "普济消毒饮", "symptoms": ["发热", "咽喉肿痛", "头面红肿", "舌红苔黄"], "herbs": ["黄芩", "黄连", "陈皮", "甘草", "玄参", "柴胡", "桔梗", "连翘", "板蓝根", "马勃", "牛蒡子", "薄荷", "僵蚕", "升麻"]},
]


HERB_DOSAGES = {
    "麻黄": 9, "桂枝": 9, "杏仁": 9, "甘草": 6, "白芍": 9, "生姜": 9, "大枣": 6,
    "柴胡": 12, "黄芩": 9, "人参": 9, "半夏": 9, "枳实": 9, "大黄": 6,
    "白术": 12, "茯苓": 12, "当归": 9, "熟地黄": 12, "川芎": 6, "陈皮": 6,
    "龙眼肉": 9, "酸枣仁": 12, "远志": 6, "木香": 6, "黄芪": 15, "升麻": 6,
    "山药": 12, "山茱萸": 9, "泽泻": 9, "牡丹皮": 9, "附子": 6, "肉桂": 3,
    "干姜": 6, "苍术": 9, "厚朴": 9, "金银花": 15, "连翘": 12, "桔梗": 9,
    "薄荷": 6, "牛蒡子": 9, "荆芥": 9, "桑叶": 9, "菊花": 9, "芦根": 15,
    "防风": 9, "知母": 9, "川芎": 6, "桃仁": 9, "红花": 6, "生地黄": 12,
    "赤芍": 9, "牛膝": 9, "黄连": 6, "水牛角": 30, "玄参": 12, "丹参": 15,
    "竹叶": 6, "麦冬": 12, "龙胆草": 6, "栀子": 9, "木通": 6, "车前子": 9,
    "吴茱萸": 3, "北沙参": 12, "枸杞子": 12, "川楝子": 6, "芍药": 9,
    "莲子": 9, "薏苡仁": 15, "砂仁": 6, "白扁豆": 9, "五味子": 6,
    "阿胶": 9, "麻仁": 9, "贝母": 9, "百合": 12, "枇杷叶": 9, "苏叶": 9,
    "前胡": 9, "沙参": 12, "梨皮": 9, "粳米": 15, "胡麻仁": 9, "石膏": 30,
    "黄柏": 9, "板蓝根": 15, "马勃": 6, "僵蚕": 9, "牡丹皮": 9,
}


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


def create_dataset():
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    sample_data = []
    
    for formula in CLASSIC_FORMULAS:
        for i in range(15):
            num_symptoms = min(len(formula["symptoms"]), max(3, len(formula["symptoms"]) - 2 + (i % 3)))
            selected_symptoms = formula["symptoms"][:num_symptoms]
            
            herbs_with_dosage = []
            for herb in formula["herbs"]:
                dosage = HERB_DOSAGES.get(herb, 9)
                herbs_with_dosage.append({"name": herb, "dosage": dosage})
            
            sample_data.append({
                "symptoms": selected_symptoms,
                "herbs": herbs_with_dosage,
                "source": f"classic_{formula['formula']}",
                "formula_name": formula["formula"],
                "is_classic": True,
            })
    
    random.seed(42)
    
    for _ in range(8000):
        base_sample = random.choice(sample_data[:len(CLASSIC_FORMULAS) * 15])
        
        new_symptoms = []
        for s in base_sample["symptoms"]:
            if s in SYMPTOM_VARIATIONS and random.random() < 0.3:
                new_symptoms.append(random.choice(SYMPTOM_VARIATIONS[s]))
            else:
                new_symptoms.append(s)
        
        sample_data.append({
            "symptoms": new_symptoms,
            "herbs": list(base_sample["herbs"]),
            "source": base_sample["source"] + "_aug",
            "formula_name": base_sample["formula_name"],
            "is_classic": False,
        })
    
    random.shuffle(sample_data)
    
    train_end = int(len(sample_data) * 0.6)
    val_end = int(len(sample_data) * 0.8)
    
    train_data = sample_data[:train_end]
    val_data = sample_data[train_end:val_end]
    test_data = sample_data[val_end:]
    
    print(f"Generated {len(sample_data)} samples")
    print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
    
    with open(os.path.join(DATASET_DIR, 'train_data.json'), 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(DATASET_DIR, 'val_data.json'), 'w', encoding='utf-8') as f:
        json.dump(val_data, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(DATASET_DIR, 'test_data.json'), 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    symptom_set = set()
    herb_set = set()
    for sample in sample_data:
        for s in sample["symptoms"]:
            symptom_set.add(s)
        for h in sample["herbs"]:
            herb_set.add(h["name"])
    
    symptom_vocab = {s: i for i, s in enumerate(sorted(symptom_set))}
    herb_vocab = {h: i for i, h in enumerate(sorted(herb_set))}
    
    with open(os.path.join(DATASET_DIR, 'symptom_vocab.json'), 'w', encoding='utf-8') as f:
        json.dump(symptom_vocab, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(DATASET_DIR, 'herb_vocab.json'), 'w', encoding='utf-8') as f:
        json.dump(herb_vocab, f, ensure_ascii=False, indent=2)
    
    symptom_counts = [len(s["symptoms"]) for s in sample_data]
    herb_counts = [len(s["herbs"]) for s in sample_data]
    
    meta = {
        "total_samples": len(sample_data),
        "train_samples": len(train_data),
        "val_samples": len(val_data),
        "test_samples": len(test_data),
        "num_symptoms": len(symptom_vocab),
        "num_herbs": len(herb_vocab),
        "avg_symptoms_per_sample": sum(symptom_counts) / len(symptom_counts),
        "avg_herbs_per_sample": sum(herb_counts) / len(herb_counts),
        "min_symptoms": min(symptom_counts),
        "max_symptoms": max(symptom_counts),
        "min_herbs": min(herb_counts),
        "max_herbs": max(herb_counts),
        "source": "classic_formulas_augmented",
        "split_ratio": "6:2:2",
    }
    
    with open(os.path.join(DATASET_DIR, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"\nDataset saved to {DATASET_DIR}")
    print(f"Symptoms: {len(symptom_vocab)}")
    print(f"Herbs: {len(herb_vocab)}")
    print(f"Avg symptoms: {meta['avg_symptoms_per_sample']:.2f}")
    print(f"Avg herbs: {meta['avg_herbs_per_sample']:.2f}")
    
    return sample_data


if __name__ == "__main__":
    create_dataset()
