"""
下载ShenNong TCM数据集（11万+中医药指令数据）

数据来源: https://huggingface.co/datasets/michaelwzhu/ShenNong_TCM_Dataset
"""

import os
import json
import requests
import random
from typing import List, Dict, Any


DATASET_DIR = "raw_data"
OUTPUT_DIR = "data"


def download_shenong_dataset():
    """
    下载ShenNong TCM数据集
    """
    print("=" * 70)
    print("  下载ShenNong TCM数据集")
    print("=" * 70)
    
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    # HuggingFace数据集URL
    base_url = "https://huggingface.co/datasets/michaelwzhu/ShenNong_TCM_Dataset/resolve/main"
    
    files_to_download = [
        "ShenNong_TCM_Dataset_v0.2/train_0.jsonl",
        "ShenNong_TCM_Dataset_v0.2/train_1.jsonl",
        "ShenNong_TCM_Dataset_v0.2/train_2.jsonl",
        "ShenNong_TCM_Dataset_v0.2/train_3.jsonl",
        "ShenNong_TCM_Dataset_v0.2/train_4.jsonl",
        "ShenNong_TCM_Dataset_v0.2/train_5.jsonl",
        "ShenNong_TCM_Dataset_v0.2/train_6.jsonl",
        "ShenNong_TCM_Dataset_v0.2/train_7.jsonl",
        "ShenNong_TCM_Dataset_v0.2/train_8.jsonl",
        "ShenNong_TCM_Dataset_v0.2/train_9.jsonl",
    ]
    
    downloaded_files = []
    
    for file_path in files_to_download:
        url = f"{base_url}/{file_path}"
        local_path = os.path.join(DATASET_DIR, os.path.basename(file_path))
        
        if os.path.exists(local_path):
            print(f"  已存在: {os.path.basename(file_path)}")
            downloaded_files.append(local_path)
            continue
        
        print(f"  下载: {os.path.basename(file_path)}...")
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                downloaded_files.append(local_path)
                print(f"    成功: {len(response.content)} bytes")
            else:
                print(f"    失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"    错误: {e}")
    
    return downloaded_files


def parse_shenong_data(file_paths: List[str]) -> List[Dict]:
    """
    解析ShenNong数据集格式
    
    原始格式（指令微调格式）:
    {
        "instruction": "请根据以下症状推荐中药方剂...",
        "input": "症状: 恶寒, 发热, 无汗...",
        "output": "推荐方剂: 麻黄汤..."
    }
    
    目标格式:
    {
        "symptoms": ["恶寒", "发热", "无汗"],
        "herbs": [{"name": "麻黄", "dosage": 9}, ...]
    }
    """
    print("\n解析ShenNong数据集...")
    
    all_samples = []
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    
                    # 提取症状和药材
                    symptoms = extract_symptoms(data)
                    herbs = extract_herbs(data)
                    
                    if symptoms and herbs:
                        all_samples.append({
                            "symptoms": symptoms,
                            "herbs": herbs,
                            "source": "ShenNong_TCM",
                            "original_instruction": data.get("instruction", ""),
                            "original_output": data.get("output", "")[:200],  # 截断
                        })
                except Exception as e:
                    continue
    
    print(f"  解析出 {len(all_samples)} 条有效样本")
    return all_samples


def extract_symptoms(data: Dict) -> List[str]:
    """
    从指令数据中提取症状
    """
    symptoms = []
    
    # 从input字段提取
    input_text = data.get("input", "")
    
    # 常见症状关键词
    symptom_keywords = [
        "恶寒", "发热", "无汗", "头痛", "身痛", "喘", "咳嗽", "痰",
        "气短", "乏力", "面色萎黄", "食欲不振", "失眠", "心悸",
        "腹痛", "腹泻", "便秘", "恶心", "呕吐", "口苦", "口干",
        "腰痛", "腿痛", "关节痛", "水肿", "盗汗", "自汗",
        "头晕", "耳鸣", "目眩", "咽干", "咽痛", "鼻塞", "流涕",
        "胸闷", "胸痛", "胁痛", "黄疸", "消渴", "遗精", "阳痿",
        "月经不调", "痛经", "带下", "崩漏", "不孕", "小儿疳积",
    ]
    
    for keyword in symptom_keywords:
        if keyword in input_text:
            symptoms.append(keyword)
    
    # 去重
    symptoms = list(set(symptoms))
    
    return symptoms


def extract_herbs(data: Dict) -> List[Dict]:
    """
    从输出中提取药材
    """
    herbs = []
    
    output_text = data.get("output", "")
    
    # 常见药材
    herb_keywords = [
        "麻黄", "桂枝", "杏仁", "甘草", "石膏", "知母", "粳米",
        "人参", "白术", "茯苓", "当归", "川芎", "白芍", "熟地黄",
        "柴胡", "黄芩", "半夏", "生姜", "大枣", "黄芪", "升麻",
        "陈皮", "枳实", "厚朴", "大黄", "芒硝", "黄连", "黄柏",
        "栀子", "连翘", "金银花", "薄荷", "牛蒡子", "桔梗", "竹叶",
        "荆芥", "防风", "羌活", "独活", "秦艽", "威灵仙", "木瓜",
        "桑寄生", "杜仲", "牛膝", "续断", "骨碎补", "补骨脂",
        "益智仁", "菟丝子", "沙苑子", "锁阳", "肉苁蓉", "巴戟天",
        "淫羊藿", "仙茅", "鹿茸", "蛤蚧", "冬虫夏草", "紫河车",
        "何首乌", "阿胶", "龙眼肉", "百合", "玉竹", "黄精",
        "石斛", "麦冬", "天冬", "北沙参", "南沙参", "玄参",
        "牡丹皮", "赤芍", "紫草", "水牛角", "生地黄", "青蒿",
        "地骨皮", "银柴胡", "胡黄连", "白薇", "青黛", "大青叶",
        "板蓝根", "射干", "山豆根", "马勃", "蒲公英", "紫花地丁",
        "野菊花", "穿心莲", "鱼腥草", "败酱草", "白头翁", "马齿苋",
        "鸦胆子", "土茯苓", "白花蛇舌草", "半枝莲", "半边莲",
    ]
    
    for herb in herb_keywords:
        if herb in output_text:
            herbs.append({"name": herb, "dosage": 9})
    
    # 去重
    seen = set()
    unique_herbs = []
    for h in herbs:
        if h["name"] not in seen:
            seen.add(h["name"])
            unique_herbs.append(h)
    
    return unique_herbs


def create_classic_formula_data():
    """
    创建经典方剂数据（作为补充）
    """
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
        {"formula": "银翘散", "symptoms": ["发热", "微恶寒", "头痛", "咳嗽", "咽痛", "口渴"], "herbs": ["金银花", "连翘", "薄荷", "牛蒡子", "桔梗", "竹叶", "荆芥", "淡豆豉", "甘草"]},
        {"formula": "桑菊饮", "symptoms": ["咳嗽", "发热", "口渴", "咽痛", "头痛", "脉浮数"], "herbs": ["桑叶", "菊花", "杏仁", "连翘", "薄荷", "桔梗", "芦根", "甘草"]},
        {"formula": "败毒散", "symptoms": ["恶寒", "发热", "头痛", "肢体酸痛", "咳嗽", "鼻塞"], "herbs": ["柴胡", "前胡", "川芎", "枳壳", "羌活", "独活", "茯苓", "桔梗", "人参", "甘草"]},
        {"formula": "参苓白术散", "symptoms": ["食欲不振", "腹泻", "乏力", "面色萎黄", "咳嗽", "痰多"], "herbs": ["人参", "白术", "茯苓", "山药", "莲子", "薏苡仁", "砂仁", "桔梗", "白扁豆", "甘草"]},
        {"formula": "生脉散", "symptoms": ["气短", "乏力", "汗出", "口渴", "脉虚", "心悸"], "herbs": ["人参", "麦冬", "五味子"]},
        {"formula": "玉屏风散", "symptoms": ["自汗", "恶风", "乏力", "易感冒", "面色苍白", "舌淡"], "herbs": ["黄芪", "白术", "防风"]},
        {"formula": "四逆汤", "symptoms": ["四肢厥冷", "神疲", "畏寒", "下利清谷", "脉微欲绝", "面色苍白"], "herbs": ["附子", "干姜", "甘草"]},
        {"formula": "当归补血汤", "symptoms": ["乏力", "头晕", "面色萎黄", "心悸", "气短", "脉虚"], "herbs": ["黄芪", "当归"]},
        {"formula": "酸枣仁汤", "symptoms": ["失眠", "心悸", "盗汗", "头晕", "咽干", "脉细数"], "herbs": ["酸枣仁", "茯苓", "知母", "川芎", "甘草"]},
        {"formula": "血府逐瘀汤", "symptoms": ["头痛", "胸痛", "失眠", "心悸", "烦躁", "舌紫暗"], "herbs": ["桃仁", "红花", "当归", "生地黄", "川芎", "赤芍", "牛膝", "桔梗", "柴胡", "枳壳", "甘草"]},
        {"formula": "补阳还五汤", "symptoms": ["半身不遂", "口眼歪斜", "语言謇涩", "乏力", "小便频数", "舌暗"], "herbs": ["黄芪", "当归", "赤芍", "地龙", "川芎", "桃仁", "红花"]},
        {"formula": "川芎茶调散", "symptoms": ["头痛", "恶寒", "发热", "鼻塞", "苔薄白", "脉浮"], "herbs": ["川芎", "荆芥", "薄荷", "防风", "细辛", "白芷", "羌活", "甘草"]},
        {"formula": "独活寄生汤", "symptoms": ["腰膝疼痛", "关节屈伸不利", "畏寒", "乏力", "麻木", "舌淡"], "herbs": ["独活", "桑寄生", "杜仲", "牛膝", "细辛", "秦艽", "茯苓", "肉桂", "防风", "川芎", "人参", "甘草", "当归", "芍药", "熟地黄"]},
        {"formula": "平胃散", "symptoms": ["脘腹胀满", "食欲不振", "恶心呕吐", "肢体困重", "舌苔白腻", "脉缓"], "herbs": ["苍术", "厚朴", "陈皮", "甘草"]},
        {"formula": "藿香正气散", "symptoms": ["恶寒", "发热", "头痛", "胸膈满闷", "恶心呕吐", "腹泻"], "herbs": ["藿香", "紫苏", "白芷", "大腹皮", "茯苓", "白术", "陈皮", "半夏", "厚朴", "桔梗", "甘草"]},
        {"formula": "半夏厚朴汤", "symptoms": ["咽中如有物阻", "咳之不出", "吞之不下", "胸胁满闷", "情绪抑郁", "苔白腻"], "herbs": ["半夏", "厚朴", "茯苓", "生姜", "苏叶"]},
        {"formula": "苏子降气汤", "symptoms": ["咳嗽", "气喘", "痰多", "胸膈满闷", "呼多吸少", "腰痛"], "herbs": ["苏子", "半夏", "前胡", "厚朴", "肉桂", "当归", "生姜", "苏叶", "甘草"]},
        {"formula": "定喘汤", "symptoms": ["哮喘", "咳嗽", "痰多", "胸闷", "发热", "恶寒"], "herbs": ["白果", "麻黄", "苏子", "甘草", "款冬花", "杏仁", "桑白皮", "黄芩", "半夏"]},
        {"formula": "旋覆代赭汤", "symptoms": ["嗳气", "呃逆", "呕吐", "胃脘痞硬", "苔白", "脉滑"], "herbs": ["旋覆花", "代赭石", "人参", "生姜", "甘草", "半夏", "大枣"]},
        {"formula": "越鞠丸", "symptoms": ["胸膈痞闷", "脘腹胀痛", "嗳腐吞酸", "食欲不振", "情绪抑郁", "苔腻"], "herbs": ["香附", "川芎", "苍术", "栀子", "神曲"]},
        {"formula": "天王补心丹", "symptoms": ["失眠", "心悸", "健忘", "盗汗", "口舌生疮", "大便干燥"], "herbs": ["人参", "玄参", "丹参", "茯苓", "远志", "桔梗", "当归", "五味子", "麦冬", "天冬", "柏子仁", "酸枣仁", "生地黄"]},
        {"formula": "安宫牛黄丸", "symptoms": ["高热", "神昏", "谵语", "烦躁", "舌绛", "脉数"], "herbs": ["牛黄", "麝香", "犀角", "黄连", "黄芩", "栀子", "郁金", "朱砂", "雄黄", "冰片", "珍珠"]},
        {"formula": "苏合香丸", "symptoms": ["神昏", "牙关紧闭", "痰壅气闭", "突然昏倒", "苔白", "脉迟"], "herbs": ["苏合香", "麝香", "冰片", "安息香", "青木香", "香附", "白檀香", "丁香", "沉香", "荜茇", "乳香", "白术", "诃子", "朱砂", "水牛角"]},
        {"formula": "朱砂安神丸", "symptoms": ["失眠", "心悸", "烦躁", "多梦", "舌红", "脉数"], "herbs": ["朱砂", "黄连", "当归", "生地黄", "甘草"]},
        {"formula": "犀角地黄汤", "symptoms": ["高热", "斑疹", "出血", "舌绛", "烦躁", "神昏"], "herbs": ["水牛角", "生地黄", "芍药", "牡丹皮"]},
    ]
    
    samples = []
    
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
    
    for formula in CLASSIC_FORMULAS:
        base_sample = {
            "symptoms": formula["symptoms"],
            "herbs": [{"name": h, "dosage": 9} for h in formula["herbs"]],
            "formula_name": formula["formula"],
            "source": f"classic_{formula['formula']}",
            "is_classic": True,
        }
        samples.append(base_sample)
        
        for _ in range(10):
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
    
    return samples


def merge_and_split_data(shenong_samples: List[Dict], classic_samples: List[Dict]):
    """
    合并并划分数据集
    """
    print("\n合并数据集...")
    
    all_samples = shenong_samples + classic_samples
    random.shuffle(all_samples)
    
    print(f"  总样本数: {len(all_samples)}")
    print(f"    ShenNong数据: {len(shenong_samples)}")
    print(f"    经典方剂数据: {len(classic_samples)}")
    
    # 构建词表
    symptom_vocab = set()
    herb_vocab = set()
    
    for sample in all_samples:
        for s in sample.get("symptoms", []):
            symptom_vocab.add(s)
        for h in sample.get("herbs", []):
            herb_vocab.add(h["name"])
    
    symptom_vocab_dict = {s: i for i, s in enumerate(sorted(symptom_vocab))}
    herb_vocab_dict = {h: i for i, h in enumerate(sorted(herb_vocab))}
    
    print(f"  症状词表: {len(symptom_vocab)}")
    print(f"  药材词表: {len(herb_vocab)}")
    
    # 划分数据集
    train_end = int(len(all_samples) * 0.6)
    val_end = int(len(all_samples) * 0.8)
    
    train_data = all_samples[:train_end]
    val_data = all_samples[train_end:val_end]
    test_data = all_samples[val_end:]
    
    print(f"\n数据集划分:")
    print(f"  训练集: {len(train_data)}")
    print(f"  验证集: {len(val_data)}")
    print(f"  测试集: {len(test_data)}")
    
    return train_data, val_data, test_data, symptom_vocab_dict, herb_vocab_dict


def save_dataset(train_data, val_data, test_data, symptom_vocab, herb_vocab):
    """
    保存数据集
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
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
    
    all_data = train_data + val_data + test_data
    symptom_counts = [len(s.get("symptoms", [])) for s in all_data]
    herb_counts = [len(s.get("herbs", [])) for s in all_data]
    
    meta = {
        "total_samples": len(all_data),
        "train_samples": len(train_data),
        "val_samples": len(val_data),
        "test_samples": len(test_data),
        "num_symptoms": len(symptom_vocab),
        "num_herbs": len(herb_vocab),
        "avg_symptoms_per_sample": sum(symptom_counts) / len(symptom_counts) if symptom_counts else 0,
        "avg_herbs_per_sample": sum(herb_counts) / len(herb_counts) if herb_counts else 0,
        "min_symptoms": min(symptom_counts) if symptom_counts else 0,
        "max_symptoms": max(symptom_counts) if symptom_counts else 0,
        "min_herbs": min(herb_counts) if herb_counts else 0,
        "max_herbs": max(herb_counts) if herb_counts else 0,
        "source": "ShenNong_TCM + classic_formulas",
        "split_ratio": "6:2:2",
    }
    
    with open(os.path.join(OUTPUT_DIR, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据集已保存到 {OUTPUT_DIR}/")
    print("=" * 70)


def main():
    print("=" * 70)
    print("  中医方剂数据集准备")
    print("  数据来源: ShenNong TCM Dataset (11万+) + 经典方剂")
    print("=" * 70)
    
    # 尝试下载ShenNong数据集
    downloaded_files = download_shenong_dataset()
    
    # 解析ShenNong数据
    shenong_samples = []
    if downloaded_files:
        shenong_samples = parse_shenong_data(downloaded_files)
    
    # 创建经典方剂数据
    print("\n创建经典方剂数据...")
    classic_samples = create_classic_formula_data()
    print(f"  经典方剂样本: {len(classic_samples)}")
    
    # 合并并划分
    train_data, val_data, test_data, symptom_vocab, herb_vocab = merge_and_split_data(
        shenong_samples, classic_samples
    )
    
    # 保存
    save_dataset(train_data, val_data, test_data, symptom_vocab, herb_vocab)


if __name__ == '__main__':
    main()
