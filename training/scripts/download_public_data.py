"""
下载公开中医方剂数据集
"""

import os
import json
import requests
import pandas as pd
import random


DATASET_DIR = "raw_data"
OUTPUT_DIR = "data"


def download_file(url, filename):
    """下载文件"""
    print(f"下载 {filename}...")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            filepath = os.path.join(DATASET_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"  成功: {len(response.content)} bytes")
            return True
        else:
            print(f"  失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  错误: {e}")
        return False


def create_sample_data():
    """
    创建示例数据（基于经典方剂）
    当无法下载公开数据集时使用
    """
    print("\n创建示例数据...")
    
    CLASSIC_FORMULAS = [
        {"formula": "麻黄汤", "symptoms": ["恶寒", "发热", "无汗", "头痛", "身痛", "喘"], "herbs": ["麻黄", "桂枝", "杏仁", "甘草"]},
        {"formula": "桂枝汤", "symptoms": ["发热", "恶风", "汗出", "头痛", "鼻鸣", "干呕"], "herbs": ["桂枝", "白芍", "生姜", "大枣", "甘草"]},
        {"formula": "小柴胡汤", "symptoms": ["寒热往来", "胸胁苦满", "口苦", "咽干", "目眩", "心烦"], "herbs": ["柴胡", "黄芩", "人参", "半夏", "生姜", "大枣", "甘草"]},
        {"formula": "四君子汤", "symptoms": ["气短", "乏力", "面色萎黄", "食欲不振", "语声低微", "大便溏薄"], "herbs": ["人参", "白术", "茯苓", "甘草"]},
        {"formula": "四物汤", "symptoms": ["头晕", "心悸", "失眠", "面色苍白", "月经不调", "腹痛"], "herbs": ["当归", "川芎", "白芍", "熟地黄"]},
        {"formula": "逍遥散", "symptoms": ["胁痛", "口苦", "食欲不振", "月经不调", "乳房胀痛", "情绪抑郁"], "herbs": ["柴胡", "当归", "白芍", "白术", "茯苓", "薄荷", "生姜", "甘草"]},
        {"formula": "补中益气汤", "symptoms": ["气短", "乏力", "头晕", "自汗", "脱肛", "子宫下垂"], "herbs": ["黄芪", "人参", "白术", "当归", "陈皮", "升麻", "柴胡", "甘草"]},
        {"formula": "肾气丸", "symptoms": ["腰痛", "畏寒", "乏力", "小便不利", "水肿", "阳痿"], "herbs": ["熟地黄", "山药", "山茱萸", "茯苓", "泽泻", "牡丹皮", "桂枝", "附子"]},
        {"formula": "六味地黄丸", "symptoms": ["腰膝酸软", "头晕", "耳鸣", "盗汗", "遗精", "手足心热"], "herbs": ["熟地黄", "山药", "山茱萸", "茯苓", "泽泻", "牡丹皮"]},
        {"formula": "归脾汤", "symptoms": ["心悸", "失眠", "健忘", "面色萎黄", "食欲不振", "月经量多"], "herbs": ["人参", "黄芪", "白术", "茯苓", "龙眼肉", "酸枣仁", "木香", "当归", "远志", "甘草"]},
        {"formula": "大承气汤", "symptoms": ["腹痛", "便秘", "发热", "谵语", "腹部胀满", "拒按"], "herbs": ["大黄", "芒硝", "枳实", "厚朴"]},
        {"formula": "白虎汤", "symptoms": ["高热", "口渴", "汗出", "脉洪大", "烦躁", "面赤"], "herbs": ["石膏", "知母", "甘草", "粳米"]},
        {"formula": "黄连解毒汤", "symptoms": ["高热", "烦躁", "口渴", "舌红", "苔黄", "脉数"], "herbs": ["黄连", "黄芩", "黄柏", "栀子"]},
        {"formula": "清营汤", "symptoms": ["高热", "烦躁", "口渴", "斑疹", "舌绛", "脉数"], "herbs": ["水牛角", "生地黄", "玄参", "竹叶", "麦冬", "丹参", "黄连", "金银花", "连翘"]},
        {"formula": "犀角地黄汤", "symptoms": ["高热", "斑疹", "出血", "舌绛", "烦躁", "神昏"], "herbs": ["水牛角", "生地黄", "芍药", "牡丹皮"]},
        {"formula": "银翘散", "symptoms": ["发热", "微恶寒", "头痛", "咳嗽", "咽痛", "口渴"], "herbs": ["金银花", "连翘", "薄荷", "牛蒡子", "桔梗", "竹叶", "荆芥", "淡豆豉", "甘草"]},
        {"formula": "桑菊饮", "symptoms": ["咳嗽", "发热", "口渴", "咽痛", "头痛", "脉浮数"], "herbs": ["桑叶", "菊花", "杏仁", "连翘", "薄荷", "桔梗", "芦根", "甘草"]},
        {"formula": "败毒散", "symptoms": ["恶寒", "发热", "头痛", "肢体酸痛", "咳嗽", "鼻塞"], "herbs": ["柴胡", "前胡", "川芎", "枳壳", "羌活", "独活", "茯苓", "桔梗", "人参", "甘草"]},
        {"formula": "参苓白术散", "symptoms": ["食欲不振", "腹泻", "乏力", "面色萎黄", "咳嗽", "痰多"], "herbs": ["人参", "白术", "茯苓", "山药", "莲子", "薏苡仁", "砂仁", "桔梗", "白扁豆", "甘草"]},
        {"formula": "生脉散", "symptoms": ["气短", "乏力", "汗出", "口渴", "脉虚", "心悸"], "herbs": ["人参", "麦冬", "五味子"]},
        {"formula": "玉屏风散", "symptoms": ["自汗", "恶风", "乏力", "易感冒", "面色苍白", "舌淡"], "herbs": ["黄芪", "白术", "防风"]},
        {"formula": "四逆汤", "symptoms": ["四肢厥冷", "神疲", "畏寒", "下利清谷", "脉微欲绝", "面色苍白"], "herbs": ["附子", "干姜", "甘草"]},
        {"formula": "当归补血汤", "symptoms": ["乏力", "头晕", "面色萎黄", "心悸", "气短", "脉虚"], "herbs": ["黄芪", "当归"]},
        {"formula": "酸枣仁汤", "symptoms": ["失眠", "心悸", "盗汗", "头晕", "咽干", "脉细数"], "herbs": ["酸枣仁", "茯苓", "知母", "川芎", "甘草"]},
        {"formula": "天王补心丹", "symptoms": ["失眠", "心悸", "健忘", "盗汗", "口舌生疮", "大便干燥"], "herbs": ["人参", "玄参", "丹参", "茯苓", "远志", "桔梗", "当归", "五味子", "麦冬", "天冬", "柏子仁", "酸枣仁", "生地黄"]},
        {"formula": "朱砂安神丸", "symptoms": ["失眠", "心悸", "烦躁", "多梦", "舌红", "脉数"], "herbs": ["朱砂", "黄连", "当归", "生地黄", "甘草"]},
        {"formula": "安宫牛黄丸", "symptoms": ["高热", "神昏", "谵语", "烦躁", "舌绛", "脉数"], "herbs": ["牛黄", "麝香", "犀角", "黄连", "黄芩", "栀子", "郁金", "朱砂", "雄黄", "冰片", "珍珠"]},
        {"formula": "苏合香丸", "symptoms": ["神昏", "牙关紧闭", "痰壅气闭", "突然昏倒", "苔白", "脉迟"], "herbs": ["苏合香", "麝香", "冰片", "安息香", "青木香", "香附", "白檀香", "丁香", "沉香", "荜茇", "乳香", "白术", "诃子", "朱砂", "水牛角"]},
        {"formula": "越鞠丸", "symptoms": ["胸膈痞闷", "脘腹胀痛", "嗳腐吞酸", "食欲不振", "情绪抑郁", "苔腻"], "herbs": ["香附", "川芎", "苍术", "栀子", "神曲"]},
        {"formula": "半夏厚朴汤", "symptoms": ["咽中如有物阻", "咳之不出", "吞之不下", "胸胁满闷", "情绪抑郁", "苔白腻"], "herbs": ["半夏", "厚朴", "茯苓", "生姜", "苏叶"]},
        {"formula": "苏子降气汤", "symptoms": ["咳嗽", "气喘", "痰多", "胸膈满闷", "呼多吸少", "腰痛"], "herbs": ["苏子", "半夏", "前胡", "厚朴", "肉桂", "当归", "生姜", "苏叶", "甘草"]},
        {"formula": "定喘汤", "symptoms": ["哮喘", "咳嗽", "痰多", "胸闷", "发热", "恶寒"], "herbs": ["白果", "麻黄", "苏子", "甘草", "款冬花", "杏仁", "桑白皮", "黄芩", "半夏"]},
        {"formula": "旋覆代赭汤", "symptoms": ["嗳气", "呃逆", "呕吐", "胃脘痞硬", "苔白", "脉滑"], "herbs": ["旋覆花", "代赭石", "人参", "生姜", "甘草", "半夏", "大枣"]},
        {"formula": "血府逐瘀汤", "symptoms": ["头痛", "胸痛", "失眠", "心悸", "烦躁", "舌紫暗"], "herbs": ["桃仁", "红花", "当归", "生地黄", "川芎", "赤芍", "牛膝", "桔梗", "柴胡", "枳壳", "甘草"]},
        {"formula": "补阳还五汤", "symptoms": ["半身不遂", "口眼歪斜", "语言謇涩", "乏力", "小便频数", "舌暗"], "herbs": ["黄芪", "当归", "赤芍", "地龙", "川芎", "桃仁", "红花"]},
        {"formula": "川芎茶调散", "symptoms": ["头痛", "恶寒", "发热", "鼻塞", "苔薄白", "脉浮"], "herbs": ["川芎", "荆芥", "薄荷", "防风", "细辛", "白芷", "羌活", "甘草"]},
        {"formula": "独活寄生汤", "symptoms": ["腰膝疼痛", "关节屈伸不利", "畏寒", "乏力", "麻木", "舌淡"], "herbs": ["独活", "桑寄生", "杜仲", "牛膝", "细辛", "秦艽", "茯苓", "肉桂", "防风", "川芎", "人参", "甘草", "当归", "芍药", "熟地黄"]},
        {"formula": "平胃散", "symptoms": ["脘腹胀满", "食欲不振", "恶心呕吐", "肢体困重", "舌苔白腻", "脉缓"], "herbs": ["苍术", "厚朴", "陈皮", "甘草"]},
        {"formula": "藿香正气散", "symptoms": ["恶寒", "发热", "头痛", "胸膈满闷", "恶心呕吐", "腹泻"], "herbs": ["藿香", "紫苏", "白芷", "大腹皮", "茯苓", "白术", "陈皮", "半夏", "厚朴", "桔梗", "甘草"]},
    ]
    
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
    
    samples = []
    
    for formula in CLASSIC_FORMULAS:
        base_sample = {
            "symptoms": formula["symptoms"],
            "herbs": [{"name": h, "dosage": 9} for h in formula["herbs"]],
            "formula_name": formula["formula"],
            "source": f"classic_{formula['formula']}",
            "is_classic": True,
        }
        samples.append(base_sample)
        
        for _ in range(5):
            new_symptoms = []
            for s in formula["symptoms"]:
                if s in SYMPTOM_VARIATIONS and random.random() < 0.3:
                    new_symptoms.append(random.choice(SYMPTOM_VARIATIONS[s]))
                else:
                    new_symptoms.append(s)
            
            if len(new_symptoms) > 3:
                k = random.randint(3, len(new_symptoms))
                new_symptoms = random.sample(new_symptoms, k)
            
            random.shuffle(new_symptoms)
            
            samples.append({
                "symptoms": new_symptoms,
                "herbs": [{"name": h, "dosage": 9} for h in formula["herbs"]],
                "formula_name": formula["formula"],
                "source": f"classic_{formula['formula']}_aug",
                "is_classic": False,
            })
    
    random.shuffle(samples)
    return samples


def main():
    print("=" * 70)
    print("  中医方剂数据集准备")
    print("=" * 70)
    
    os.makedirs(DATASET_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    urls = [
        ("https://raw.githubusercontent.com/hzfu/TCMPR/master/data/prescription.csv", "prescription.csv"),
        ("https://raw.githubusercontent.com/hzfu/TCMPR/master/data/herb.csv", "herb.csv"),
        ("https://raw.githubusercontent.com/hzfu/TCMPR/master/data/symptom.csv", "symptom.csv"),
    ]
    
    downloaded = 0
    for url, filename in urls:
        if download_file(url, filename):
            downloaded += 1
    
    if downloaded > 0:
        print(f"\n成功下载 {downloaded} 个文件")
        
        prescription_path = os.path.join(DATASET_DIR, "prescription.csv")
        if os.path.exists(prescription_path):
            print("\n处理TCMPR数据...")
            df = pd.read_csv(prescription_path)
            print(f"  数据列: {list(df.columns)}")
            print(f"  数据量: {len(df)}")
    else:
        print("\n无法下载公开数据集，使用经典方剂数据")
    
    print("\n生成训练数据...")
    samples = create_sample_data()
    print(f"  总样本数: {len(samples)}")
    
    random.seed(42)
    random.shuffle(samples)
    
    train_end = int(len(samples) * 0.6)
    val_end = int(len(samples) * 0.8)
    
    train_data = samples[:train_end]
    val_data = samples[train_end:val_end]
    test_data = samples[val_end:]
    
    print(f"  训练集: {len(train_data)}")
    print(f"  验证集: {len(val_data)}")
    print(f"  测试集: {len(test_data)}")
    
    symptom_vocab = set()
    herb_vocab = set()
    
    for sample in samples:
        for s in sample["symptoms"]:
            symptom_vocab.add(s)
        for h in sample["herbs"]:
            herb_vocab.add(h["name"])
    
    symptom_vocab = {s: i for i, s in enumerate(sorted(symptom_vocab))}
    herb_vocab = {h: i for i, h in enumerate(sorted(herb_vocab))}
    
    print(f"  症状词表: {len(symptom_vocab)}")
    print(f"  药材词表: {len(herb_vocab)}")
    
    with open(os.path.join(OUTPUT_DIR, 'train_data.json'), 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, 'val_data.json'), 'w', encoding='utf-8') as f:
        json.dump(val_data, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, 'test_data.json'), 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, 'symptom_vocab.json'), 'w', encoding='utf-8') as f:
        json.dump(symptom_vocab, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, 'herb_vocab.json'), 'w', encoding='utf-8') as f:
        json.dump(herb_vocab, f, ensure_ascii=False, indent=2)
    
    symptom_counts = [len(s["symptoms"]) for s in samples]
    herb_counts = [len(s["herbs"]) for s in samples]
    
    meta = {
        "total_samples": len(samples),
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
    
    with open(os.path.join(OUTPUT_DIR, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据集已保存到 {OUTPUT_DIR}/")
    print("=" * 70)


if __name__ == '__main__':
    main()
