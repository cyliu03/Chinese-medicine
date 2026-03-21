import json
import re
import os
from collections import defaultdict

def extract_symptoms(query):
    symptoms = []
    
    symptom_patterns = [
        r'症状[是为：:]\s*([^\。\，\n]+)',
        r'出现([^\。\，\n]+)症状',
        r'患有([^\。\，\n]+)',
        r'感觉([^\。\，\n]+)',
        r'我([^\。\，\n]+)',
    ]
    
    for pattern in symptom_patterns:
        matches = re.findall(pattern, query)
        for match in matches:
            symptom_text = match.strip()
            symptom_list = re.split(r'[、，,和与及]', symptom_text)
            for s in symptom_list:
                s = s.strip()
                if len(s) >= 2 and len(s) <= 10:
                    if not any(x in s for x in ['推荐', '中药', '方剂', '治疗', '没有', '其他']):
                        symptoms.append(s)
    
    common_symptoms = [
        '头痛', '发热', '咳嗽', '腹痛', '腹泻', '便秘', '恶心', '呕吐',
        '失眠', '心悸', '胸闷', '气喘', '乏力', '浮肿', '眩晕', '腰痛',
        '盗汗', '自汗', '口干', '口苦', '咽痛', '鼻塞', '流涕', '喷嚏',
        '恶寒', '发热', '潮热', '烦躁', '抑郁', '健忘', '耳鸣', '耳聋',
        '目赤', '目痛', '齿痛', '牙龈肿痛', '口舌生疮', '咽喉肿痛',
        '颈项强痛', '肩背痛', '腰膝酸软', '关节痛', '四肢麻木',
        '小便不利', '小便频数', '小便涩痛', '遗尿', '尿血',
        '带下', '月经不调', '痛经', '闭经', '崩漏',
        '食欲不振', '腹胀', '肠鸣', '里急后重', '便血',
        '黄疸', '水肿', '腹水', '消瘦', '肥胖',
        '半身不遂', '抽搐', '痉厥', '昏迷', '谵语',
        '出血', '瘀血', '肿块', '疮疡', '湿疹', '瘙痒'
    ]
    
    for symptom in common_symptoms:
        if symptom in query:
            symptoms.append(symptom)
    
    return list(set(symptoms))

def extract_herbs_and_formulas(response):
    herbs = []
    formulas = []
    
    formula_patterns = [
        r'([^\s、，,。]+汤)',
        r'([^\s、，,。]+丸)',
        r'([^\s、，,。]+散)',
        r'([^\s、，,。]+丹)',
        r'([^\s、，,。]+膏)',
        r'([^\s、，,。]+饮)',
        r'([^\s、，,。]+片)',
        r'([^\s、，,。]+胶囊)',
        r'([^\s、，,。]+颗粒)',
    ]
    
    for pattern in formula_patterns:
        matches = re.findall(pattern, response)
        for match in matches:
            formula = match.strip()
            if len(formula) >= 3 and len(formula) <= 15:
                if not any(x in formula for x in ['可以', '具有', '能够', '建议', '适用']):
                    formulas.append(formula)
    
    common_herbs = [
        '人参', '黄芪', '白术', '茯苓', '甘草', '当归', '川芎', '白芍', '熟地', '生地',
        '桂枝', '麻黄', '杏仁', '石膏', '黄芩', '黄连', '黄柏', '栀子', '连翘', '金银花',
        '柴胡', '半夏', '陈皮', '枳实', '厚朴', '苍术', '泽泻', '车前子', '木通', '滑石',
        '附子', '干姜', '肉桂', '吴茱萸', '细辛', '丁香', '小茴香', '花椒', '胡椒',
        '大黄', '芒硝', '番泻叶', '火麻仁', '郁李仁', '牵牛子', '甘遂', '大戟', '芫花',
        '桃仁', '红花', '丹参', '益母草', '牛膝', '鸡血藤', '王不留行', '穿山甲',
        '延胡索', '郁金', '姜黄', '乳香', '没药', '五灵脂', '三七', '白及', '仙鹤草',
        '天麻', '钩藤', '石决明', '珍珠母', '龙骨', '牡蛎', '代赭石', '刺蒺藜',
        '酸枣仁', '柏子仁', '远志', '合欢皮', '夜交藤', '朱砂', '磁石', '琥珀',
        '麝香', '冰片', '苏合香', '石菖蒲', '安息香', '蟾酥', '樟脑',
        '党参', '太子参', '西洋参', '山药', '白扁豆', '大枣', '饴糖', '蜂蜜',
        '鹿茸', '巴戟天', '淫羊藿', '仙茅', '补骨脂', '益智仁', '肉苁蓉', '锁阳',
        '杜仲', '续断', '菟丝子', '沙苑子', '核桃仁', '韭菜子', '阳起石',
        '枸杞子', '桑葚', '女贞子', '墨旱莲', '龟甲', '鳖甲', '黑芝麻', '百合',
        '麦冬', '天冬', '石斛', '玉竹', '黄精', '北沙参', '南沙参', '明党参',
        '五味子', '乌梅', '五倍子', '诃子', '肉豆蔻', '赤石脂', '禹余粮', '罂粟壳',
        '浮小麦', '麻黄根', '糯稻根', '椿皮', '石榴皮', '莲子', '芡实', '金樱子',
        '桑螵蛸', '海螵蛸', '覆盆子', '山茱萸', '龙眼肉',
        '防风', '荆芥', '羌活', '独活', '白芷', '藁本', '苍耳子', '辛夷', '薄荷', '蝉蜕',
        '牛蒡子', '桑叶', '菊花', '蔓荆子', '葛根', '升麻', '淡豆豉', '浮萍',
        '知母', '芦根', '天花粉', '淡竹叶', '鸭跖草', '青葙子', '密蒙花', '谷精草',
        '青蒿', '地骨皮', '白薇', '银柴胡', '胡黄连', '秦艽', '功劳叶', '鳖甲',
        '藿香', '佩兰', '砂仁', '白豆蔻', '草豆蔻', '草果', '厚朴花', '扁豆花',
        '茵陈', '金钱草', '虎杖', '垂盆草', '地耳草', '鸡骨草', '珍珠草',
        '木香', '香附', '乌药', '沉香', '檀香', '川楝子', '荔枝核', '青木香',
        '佛手', '香橼', '玫瑰花', '绿萼梅', '娑罗子', '薤白', '大腹皮', '柿蒂',
        '山楂', '神曲', '麦芽', '谷芽', '莱菔子', '鸡内金', '鸡矢藤', '隔山消',
        '使君子', '苦楝皮', '槟榔', '南瓜子', '鹤草芽', '雷丸', '鹤虱', '榧子',
        '小蓟', '大蓟', '地榆', '槐花', '槐角', '白茅根', '苎麻根', '羊蹄',
        '侧柏叶', '棕榈炭', '藕节', '血余炭', '紫珠', '艾叶', '灶心土',
        '川乌', '草乌', '威灵仙', '防己', '秦艽', '络石藤', '海风藤', '青风藤',
        '桑枝', '豨莶草', '臭梧桐', '海桐皮', '丝瓜络', '穿山龙', '老鹳草',
        '蕲蛇', '乌梢蛇', '金钱白花蛇', '蛇蜕', '蜂房', '蝉蜕', '僵蚕', '全蝎',
        '蜈蚣', '地龙', '水蛭', '虻虫', '斑蝥', '穿山甲', '蟾酥', '露蜂房',
        '大蒜', '猫爪草', '毛茛', '皂角刺', '天南星', '白附子', '白芥子', '皂荚',
        '桔梗', '前胡', '瓜蒌', '贝母', '竹茹', '竹沥', '天竺黄', '海藻', '昆布',
        '胖大海', '海蛤壳', '浮海石', '瓦楞子', '礞石', '罗汉果',
        '朱砂根', '百部', '紫菀', '款冬花', '枇杷叶', '桑白皮', '葶苈子', '白果',
        '洋金花', '华山参', '矮地茶', '满山红', '胡颓叶', '龙脷叶',
        '朱砂', '磁石', '龙骨', '琥珀', '酸枣仁', '柏子仁', '灵芝', '首乌藤',
        '合欢皮', '远志', '缬草', '广枣', '娑罗子',
    ]
    
    for herb in common_herbs:
        if herb in response:
            herbs.append(herb)
    
    return list(set(herbs)), list(set(formulas))

def parse_chatmed_data(input_file, output_dir):
    print(f"解析ChatMed_TCM数据集: {input_file}")
    
    samples = []
    symptom_counter = defaultdict(int)
    herb_counter = defaultdict(int)
    formula_counter = defaultdict(int)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                query = data.get('query', '')
                response = data.get('response', '')
                
                symptoms = extract_symptoms(query)
                herbs, formulas = extract_herbs_and_formulas(response)
                
                if symptoms and (herbs or formulas):
                    sample = {
                        'symptoms': symptoms,
                        'herbs': herbs,
                        'formulas': formulas,
                        'query': query,
                        'response': response[:200]
                    }
                    samples.append(sample)
                    
                    for s in symptoms:
                        symptom_counter[s] += 1
                    for h in herbs:
                        herb_counter[h] += 1
                    for f in formulas:
                        formula_counter[f] += 1
                        
            except json.JSONDecodeError:
                continue
    
    print(f"\n解析结果:")
    print(f"  总样本数: {len(samples)}")
    print(f"  症状种类: {len(symptom_counter)}")
    print(f"  中药种类: {len(herb_counter)}")
    print(f"  方剂种类: {len(formula_counter)}")
    
    print(f"\n常见症状 Top 20:")
    for symptom, count in sorted(symptom_counter.items(), key=lambda x: -x[1])[:20]:
        print(f"  {symptom}: {count}")
    
    print(f"\n常见中药 Top 20:")
    for herb, count in sorted(herb_counter.items(), key=lambda x: -x[1])[:20]:
        print(f"  {herb}: {count}")
    
    print(f"\n常见方剂 Top 20:")
    for formula, count in sorted(formula_counter.items(), key=lambda x: -x[1])[:20]:
        print(f"  {formula}: {count}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'chatmed_parsed.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print(f"\n解析结果已保存: {output_file}")
    
    return samples

def convert_to_training_format(samples, output_dir):
    print("\n转换为训练格式...")
    
    all_symptoms = set()
    all_herbs = set()
    
    for sample in samples:
        all_symptoms.update(sample['symptoms'])
        all_herbs.update(sample['herbs'])
    
    symptom2idx = {s: i for i, s in enumerate(sorted(all_symptoms))}
    herb2idx = {h: i for i, h in enumerate(sorted(all_herbs))}
    
    train_data = []
    for sample in samples:
        symptom_indices = [symptom2idx[s] for s in sample['symptoms'] if s in symptom2idx]
        herb_indices = [herb2idx[h] for h in sample['herbs'] if h in herb2idx]
        
        if symptom_indices and herb_indices:
            train_data.append({
                'symptom_ids': symptom_indices,
                'herb_ids': herb_indices
            })
    
    meta = {
        'total_samples': len(train_data),
        'num_symptoms': len(symptom2idx),
        'num_herbs': len(herb2idx),
        'symptom2idx': symptom2idx,
        'herb2idx': herb2idx
    }
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, 'train_data.json'), 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False)
    
    with open(os.path.join(output_dir, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"训练数据已保存: {output_dir}")
    print(f"  样本数: {len(train_data)}")
    print(f"  症状数: {len(symptom2idx)}")
    print(f"  中药数: {len(herb2idx)}")
    
    return meta

if __name__ == '__main__':
    input_file = 'raw_data/shenong/ChatMed_TCM-v0.2.json'
    output_dir = '../../data/chatmed'
    
    samples = parse_chatmed_data(input_file, output_dir)
    
    if samples:
        meta = convert_to_training_format(samples, output_dir)
