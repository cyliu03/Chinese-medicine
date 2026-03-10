"""
数据集下载与转换脚本 — 从开源数据集构建训练数据

数据来源:
  PTM (Prescription Topic Model) — TKDE 2018
  GitHub: https://github.com/yao8839836/PTM
  原始数据: 98,334 个中医处方 (症状→药材+剂量)
  版权: CKCEST (中国工程科学知识中心), 仅限研究用途

用法:
    python scripts/download_dataset.py [--output_dir data/raw] [--existing_data ../src/data]
"""

import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.error
from collections import defaultdict


# PTM GitHub raw URLs
PTM_BASE_URL = "https://raw.githubusercontent.com/yao8839836/PTM/master/data"
PTM_FILES = {
    "prescriptions": "prescriptions.txt",
    "herbs_list": "herbs_contains.txt",
    "symptoms_list": "symptom_contains.txt",
    "pre_herbs": "pre_herbs.txt",
    "pre_symptoms": "pre_symptoms.txt",
    "pre_herbs_train": "pre_herbs_train.txt",
    "pre_symptoms_train": "pre_symptoms_train.txt",
    "pre_herbs_test": "pre_herbs_test.txt",
    "pre_symptoms_test": "pre_symptoms_test.txt",
    "symptom_herb_mesh": "symptom_herb_tcm_mesh.txt",
}

# 中文数字→阿拉伯数字映射
CN_NUM_MAP = {
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
    '十': 10, '百': 100, '千': 1000, '半': 0.5,
    '两': 2,  # "二两"的"两"
}

# 古代计量单位→克 换算 (取近似值)
UNIT_TO_GRAM = {
    '两': 30.0,    # 1两 ≈ 30g (现代)
    '钱': 3.0,     # 1钱 ≈ 3g
    '分': 0.3,     # 1分 ≈ 0.3g
    '厘': 0.03,    # 1厘 ≈ 0.03g
    '克': 1.0,
    'g': 1.0,
    '斤': 500.0,
    '升': 200.0,   # 液体近似
    '合': 20.0,
    '枚': 3.0,     # 枚/个 (如大枣，近似)
    '个': 3.0,
    '片': 3.0,
    '条': 5.0,
    '根': 5.0,
    '只': 10.0,
    '具': 10.0,
}


def cn_num_to_float(s):
    """将中文数字转换为浮点数，如 '三钱五分' → 3.5 (钱) + 0.5 (分)"""
    if not s:
        return None

    # 先尝试直接解析阿拉伯数字
    m = re.search(r'(\d+\.?\d*)', s)
    if m:
        return float(m.group(1))

    # 中文数字解析 (简单版)
    result = 0
    current = 0
    for ch in s:
        if ch in CN_NUM_MAP:
            val = CN_NUM_MAP[ch]
            if val >= 10:
                if current == 0:
                    current = 1
                current *= val
                result += current
                current = 0
            else:
                current = val
        elif ch == '半':
            result += 0.5
    result += current
    return result if result > 0 else None


def parse_herb_dosage(text):
    """
    从药材剂量文本中提取药材名和剂量

    示例输入:
      "甘草一两"          → ("甘草", 30.0)
      "黄芪18g"           → ("黄芪", 18.0)
      "大枣3枚"           → ("大枣", 9.0)
      "穿山甲五钱"         → ("穿山甲", 15.0)
    """
    text = text.strip()
    if not text:
        return None, None

    # 去掉括号中的炮制说明
    clean = re.sub(r'[（(][^）)]*[）)]', '', text).strip()
    if not clean:
        clean = text

    # 匹配模式: 药材名 + 数字/中文数字 + 单位
    # 阿拉伯数字模式
    m = re.match(r'^(.+?)\s*(\d+\.?\d*)\s*(两|钱|分|厘|克|g|斤|升|合|枚|个|片|条|根|只|具)?$', clean)
    if m:
        herb = m.group(1).strip()
        amount = float(m.group(2))
        unit = m.group(3) or '克'
        gram = amount * UNIT_TO_GRAM.get(unit, 1.0)
        return herb, gram

    # 中文数字模式
    m = re.match(r'^(.+?)\s*([零一二三四五六七八九十百千半两]+)\s*(两|钱|分|厘|克|斤|升|合|枚|个|片|条|根|只|具)(.*)$', clean)
    if m:
        herb = m.group(1).strip()
        cn_num = m.group(2)
        unit = m.group(3)
        amount = cn_num_to_float(cn_num)
        if amount is not None:
            gram = amount * UNIT_TO_GRAM.get(unit, 1.0)
            return herb, gram

    # 无法解析剂量，尝试提取药材名
    # 去掉末尾的数字和单位
    herb = re.sub(r'\s*[\d零一二三四五六七八九十百千半两]+\s*[两钱分厘克g斤升合枚个片条根只具].*$', '', clean)
    herb = herb.strip()
    if herb:
        return herb, 9.0  # 默认9g

    return text, 9.0


def parse_prescription_line(line):
    """
    解析 PTM prescriptions.txt 的一行

    格式: 症状描述[\t]药材1(炮制)剂量  药材2(炮制)剂量 ...

    Returns:
        dict with 'symptoms_text', 'symptoms', 'herbs'
    """
    line = line.strip()
    if not line:
        return None

    parts = line.split('\t')
    if len(parts) != 2:
        return None

    symptom_text = parts[0].strip()
    herb_text = parts[1].strip()

    if not symptom_text or not herb_text:
        return None

    # 提取症状关键词
    symptoms = extract_symptom_tags(symptom_text)

    # 解析药材列表
    # 药材之间用两个或以上空格分隔
    herb_entries = re.split(r'\s{2,}', herb_text)
    herbs = []
    seen_herbs = set()

    for entry in herb_entries:
        entry = entry.strip()
        if not entry:
            continue

        # 处理 "各X两" 的情况: "川乌  草乌各三两" → 分别解析
        if '各' in entry:
            # 提取 "各" 后面的剂量
            m_ge = re.search(r'各\s*(.+)$', entry)
            if m_ge:
                dosage_text = m_ge.group(1)
                herb_names_part = entry[:entry.index('各')].strip()
                # 可能有多个药材名在前面，已在前面的 herb_entries 中处理
                # 这里直接把整个作为一味药处理
                herb_name, dosage = parse_herb_dosage(entry.replace('各', ''))
                if herb_name and herb_name not in seen_herbs:
                    herbs.append({'name': herb_name, 'dosage': round(dosage, 1)})
                    seen_herbs.add(herb_name)
                continue

        herb_name, dosage = parse_herb_dosage(entry)
        if herb_name and herb_name not in seen_herbs:
            # 过滤太短或明显非药材的
            if len(herb_name) >= 1:
                herbs.append({'name': herb_name, 'dosage': round(dosage, 1)})
                seen_herbs.add(herb_name)

    if not herbs or not symptoms:
        return None

    return {
        'symptoms_text': symptom_text,
        'symptoms': symptoms,
        'herbs': herbs,
    }


def extract_symptom_tags(text):
    """
    从症状描述文本中提取症状标签

    使用常见中医症状关键词进行匹配
    """
    # 常见中医症状关键词表
    symptom_keywords = [
        # 全身症状
        '发热', '恶寒', '恶风', '畏寒', '壮热', '潮热', '低热', '寒热往来',
        '自汗', '盗汗', '无汗', '大汗', '汗出',
        '乏力', '倦怠', '神疲', '气短', '少气', '懒言',
        '消瘦', '肥胖', '水肿', '浮肿',

        # 头面部
        '头痛', '头晕', '头眩', '目眩', '眩晕',
        '面赤', '面色萎黄', '面色苍白', '面色无华', '面色萎白',
        '目赤', '目痛', '目涩', '视物模糊', '目昏', '翳膜',
        '耳鸣', '耳聋', '耳痛',
        '鼻塞', '流涕', '鼻衄',
        '口苦', '口干', '口渴', '口臭', '口疮',
        '咽痛', '咽干', '咽喉肿痛',
        '牙痛', '齿痛', '齿龈肿',

        # 胸腹部
        '胸闷', '胸痛', '胁痛', '两胁胀痛', '胸胁苦满',
        '心悸', '怔忡', '心烦', '失眠', '多梦', '健忘', '易惊',
        '腹痛', '腹胀', '脘腹疼痛', '胃痛', '胃脘痛',
        '恶心', '呕吐', '嗳气', '泛酸', '呃逆',

        # 饮食
        '食少', '纳差', '厌食', '食欲不振', '不欲饮食', '饮食减少',
        '多食', '善饥', '消谷善饥',
        '烦渴', '渴饮',

        # 二便
        '便秘', '便溏', '泄泻', '下利', '腹泻', '大便干结',
        '小便黄', '小便不利', '尿频', '尿急', '尿痛', '遗尿', '淋证',
        '便血', '尿血',

        # 呼吸
        '咳嗽', '咳痰', '喘', '气喘', '哮喘', '痰多', '痰黄', '痰白',

        # 四肢经络
        '腰痛', '腰膝酸软', '腰酸', '背痛',
        '肢体疼痛', '身痛', '关节痛', '肢冷', '四肢厥冷', '手足心热',
        '麻木', '痿软', '拘挛', '抽搐', '痉挛',
        '肿痛', '红肿',

        # 妇科
        '月经不调', '痛经', '闭经', '崩漏', '带下', '经期延长',

        # 皮肤
        '疮疡', '痈疽', '疥疮', '湿疹', '瘙痒', '疹', '斑疹',
        '瘰疬', '痘疮',

        # 脉象
        '脉浮', '脉沉', '脉迟', '脉数', '脉弦', '脉细', '脉洪大',
        '脉浮紧', '脉浮缓', '脉弦数', '脉弦滑', '脉沉迟',
        '脉细数', '脉细弱', '脉微细', '脉虚', '脉虚弱',

        # 舌象
        '舌红', '舌淡', '舌紫', '舌尖红',
        '苔白', '苔黄', '苔白腻', '苔黄腻', '舌红苔黄腻',

        # 其他
        '遗精', '阳痿', '眩晕', '中风', '癫痫', '黄疸',
        '痰饮', '血瘀', '气滞', '食积',
        '跌打损伤', '烫伤', '烧伤',
        '唇甲淡白',
    ]

    # 按长度降序排列 (先匹配长的)
    symptom_keywords.sort(key=len, reverse=True)

    found = []
    remaining = text
    for kw in symptom_keywords:
        if kw in remaining:
            found.append(kw)
            # 不从remaining中移除,允许重叠匹配

    # 如果没有匹配到任何症状关键词，尝试用标点分割
    if not found:
        # 按逗号、句号等分割
        segments = re.split(r'[，。、；,;.]+', text)
        for seg in segments:
            seg = seg.strip()
            if seg and len(seg) >= 2 and len(seg) <= 10:
                found.append(seg)

    return found[:20]  # 最多取20个标签


def download_file(url, save_path, max_retries=3):
    """下载文件"""
    for attempt in range(max_retries):
        try:
            print(f'   下载: {os.path.basename(save_path)}...', end='', flush=True)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
            with open(save_path, 'wb') as f:
                f.write(data)
            size_kb = len(data) / 1024
            print(f' OK ({size_kb:.0f} KB)')
            return True
        except Exception as e:
            print(f' 失败 (尝试 {attempt+1}/{max_retries}): {e}')
            if attempt == max_retries - 1:
                return False
    return False


def main():
    parser = argparse.ArgumentParser(description='下载并转换中医方剂数据集')
    parser.add_argument('--output_dir', type=str, default='data/raw',
                        help='输出目录')
    parser.add_argument('--existing_data', type=str, default='../src/data',
                        help='现有知识库目录 (包含 formulas.json, herbs.json)')
    parser.add_argument('--skip_download', action='store_true',
                        help='跳过下载 (使用已下载的文件)')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    download_dir = os.path.join(args.output_dir, 'ptm_raw')
    os.makedirs(download_dir, exist_ok=True)

    print('=' * 60)
    print('  中医方剂数据集 — 下载与转换')
    print('=' * 60)

    # ========== 1. 下载 PTM 数据 ==========
    if not args.skip_download:
        print('\n📥 下载 PTM 数据集 (TKDE 2018, 98K处方)...')
        print('   来源: github.com/yao8839836/PTM')
        print('   许可: CKCEST, 仅限研究用途\n')

        for key, filename in PTM_FILES.items():
            url = f'{PTM_BASE_URL}/{filename}'
            save_path = os.path.join(download_dir, filename)
            if os.path.exists(save_path):
                print(f'   跳过: {filename} (已存在)')
                continue
            if not download_file(url, save_path):
                print(f'   ⚠ 警告: {filename} 下载失败，继续...')
    else:
        print('\n📂 使用已下载的数据...')

    # ========== 2. 加载 PTM 原始处方 ==========
    prescriptions_path = os.path.join(download_dir, 'prescriptions.txt')
    if not os.path.exists(prescriptions_path):
        print(f'\n❌ 错误: {prescriptions_path} 不存在')
        print('   请先运行不带 --skip_download 的命令')
        sys.exit(1)

    print('\n📝 解析 PTM 处方数据...')
    ptm_prescriptions = []
    parse_errors = 0

    with open(prescriptions_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            result = parse_prescription_line(line)
            if result:
                result['id'] = f'PTM_{i+1:06d}'
                result['source'] = 'PTM/CKCEST'
                ptm_prescriptions.append(result)
            else:
                parse_errors += 1

    print(f'   ✅ 成功解析: {len(ptm_prescriptions)} 个处方')
    print(f'   ⚠ 解析失败: {parse_errors} 行')

    # 统计
    all_herbs_ptm = set()
    all_symptoms_ptm = set()
    for p in ptm_prescriptions:
        for h in p['herbs']:
            all_herbs_ptm.add(h['name'])
        for s in p['symptoms']:
            all_symptoms_ptm.add(s)
    print(f'   · 药材种类: {len(all_herbs_ptm)}')
    print(f'   · 症状标签: {len(all_symptoms_ptm)}')
    print(f'   · 平均每方药材数: {sum(len(p["herbs"]) for p in ptm_prescriptions)/len(ptm_prescriptions):.1f}')
    print(f'   · 平均每方症状数: {sum(len(p["symptoms"]) for p in ptm_prescriptions)/len(ptm_prescriptions):.1f}')

    # ========== 3. 加载现有知识库 ==========
    print('\n📂 加载现有知识库...')
    existing_formulas = []
    existing_herbs = []

    formulas_path = os.path.join(args.existing_data, 'formulas.json')
    herbs_path = os.path.join(args.existing_data, 'herbs.json')

    if os.path.exists(formulas_path):
        with open(formulas_path, 'r', encoding='utf-8') as f:
            existing_formulas = json.load(f)
        print(f'   ✅ 经典方剂: {len(existing_formulas)} 个')
    else:
        print(f'   ⚠ {formulas_path} 不存在')

    if os.path.exists(herbs_path):
        with open(herbs_path, 'r', encoding='utf-8') as f:
            existing_herbs = json.load(f)
        print(f'   ✅ 药材信息: {len(existing_herbs)} 味')
    else:
        print(f'   ⚠ {herbs_path} 不存在')

    # ========== 4. 合并数据 ==========
    print('\n🔧 合并数据...')

    # 将现有方剂也转为训练格式
    classic_prescriptions = []
    for formula in existing_formulas:
        herbs = []
        for comp in formula.get('composition', []):
            dosage_str = comp.get('amount', '9g')
            dosage_match = re.search(r'(\d+\.?\d*)', str(dosage_str))
            dosage = float(dosage_match.group(1)) if dosage_match else 9.0
            herbs.append({
                'name': comp['herb'],
                'dosage': dosage,
            })
        symptoms = formula.get('symptomTags', [])
        if herbs and symptoms:
            classic_prescriptions.append({
                'id': formula.get('id', f'CLASSIC_{formula["name"]}'),
                'source': formula.get('source', '经典方剂'),
                'formula_name': formula.get('name', ''),
                'symptoms_text': '；'.join(formula.get('indications', [])),
                'symptoms': symptoms,
                'herbs': herbs,
                'syndrome': formula.get('syndrome', ''),
                'is_classic': True,
            })

    print(f'   · 经典方剂 (训练格式): {len(classic_prescriptions)} 个')
    print(f'   · PTM 处方: {len(ptm_prescriptions)} 个')
    print(f'   · 合计: {len(classic_prescriptions) + len(ptm_prescriptions)} 个')

    # ========== 5. 构建完整词表 ==========
    all_herbs = set()
    all_symptoms = set()

    for p in ptm_prescriptions + classic_prescriptions:
        for h in p['herbs']:
            all_herbs.add(h['name'])
        for s in p['symptoms']:
            all_symptoms.add(s)

    # 从 existing_herbs 补充
    for herb in existing_herbs:
        all_herbs.add(herb['name'])

    print(f'\n📊 最终统计:')
    print(f'   · 总处方数: {len(ptm_prescriptions) + len(classic_prescriptions)}')
    print(f'   · 药材种类: {len(all_herbs)}')
    print(f'   · 症状标签: {len(all_symptoms)}')

    # ========== 6. 保存 ==========
    print(f'\n💾 保存数据到 {args.output_dir}/')

    # PTM 处方
    ptm_path = os.path.join(args.output_dir, 'ptm_prescriptions.json')
    with open(ptm_path, 'w', encoding='utf-8') as f:
        json.dump(ptm_prescriptions, f, ensure_ascii=False, indent=2)
    print(f'   ✅ ptm_prescriptions.json ({len(ptm_prescriptions)} 条)')

    # 经典方剂
    classic_path = os.path.join(args.output_dir, 'classic_prescriptions.json')
    with open(classic_path, 'w', encoding='utf-8') as f:
        json.dump(classic_prescriptions, f, ensure_ascii=False, indent=2)
    print(f'   ✅ classic_prescriptions.json ({len(classic_prescriptions)} 条)')

    # 合并
    merged = classic_prescriptions + ptm_prescriptions
    merged_path = os.path.join(args.output_dir, 'merged_prescriptions.json')
    with open(merged_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f'   ✅ merged_prescriptions.json ({len(merged)} 条)')

    # 药材列表
    herbs_list = sorted(list(all_herbs))
    herbs_path_out = os.path.join(args.output_dir, 'all_herbs.json')
    with open(herbs_path_out, 'w', encoding='utf-8') as f:
        json.dump(herbs_list, f, ensure_ascii=False, indent=2)
    print(f'   ✅ all_herbs.json ({len(herbs_list)} 味)')

    # 症状列表
    symptoms_list = sorted(list(all_symptoms))
    symptoms_path_out = os.path.join(args.output_dir, 'all_symptoms.json')
    with open(symptoms_path_out, 'w', encoding='utf-8') as f:
        json.dump(symptoms_list, f, ensure_ascii=False, indent=2)
    print(f'   ✅ all_symptoms.json ({len(symptoms_list)} 个)')

    # 元数据
    meta = {
        'ptm_count': len(ptm_prescriptions),
        'classic_count': len(classic_prescriptions),
        'total_count': len(merged),
        'num_herbs': len(all_herbs),
        'num_symptoms': len(all_symptoms),
        'ptm_source': 'github.com/yao8839836/PTM (TKDE 2018)',
        'ptm_license': 'CKCEST, research use only',
    }
    meta_path = os.path.join(args.output_dir, 'dataset_meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'   ✅ dataset_meta.json')

    print(f'\n✅ 数据集构建完成!')
    print('=' * 60)
    print(f'  下一步: python scripts/prepare_data.py --use_raw')
    print('=' * 60)


if __name__ == '__main__':
    main()
