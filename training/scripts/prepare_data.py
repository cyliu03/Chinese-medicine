"""
数据预处理脚本 — 将中药知识库 JSON 转换为训练数据

用法:
    python scripts/prepare_data.py [--data_dir ../src/data] [--output_dir data]
"""

import json
import os
import argparse
import re
import random
from collections import defaultdict


def parse_dosage(amount_str):
    """从剂量字符串中提取数值 (克)"""
    if not amount_str:
        return 9.0
    match = re.search(r'(\d+\.?\d*)', str(amount_str))
    if match:
        return float(match.group(1))
    return 9.0


def build_vocabs(herbs_data, formulas_data, symptoms_data):
    """构建词表"""
    # 症状词表：从symptoms.json和formulas的symptomTags中提取
    symptom_set = set()

    # 从 symptoms.json 提取所有tag
    def extract_tags(obj):
        if isinstance(obj, dict):
            for key, val in obj.items():
                if key == 'tags' and isinstance(val, list):
                    for t in val:
                        if t:
                            symptom_set.add(t)
                else:
                    extract_tags(val)
        elif isinstance(obj, list):
            for item in obj:
                extract_tags(item)

    extract_tags(symptoms_data)

    # 从 formulas 的 symptomTags
    for formula in formulas_data:
        for tag in formula.get('symptomTags', []):
            symptom_set.add(tag)

    # 药材词表
    herb_set = set()
    for herb in herbs_data:
        herb_set.add(herb['name'])
    # 也从方剂组成中添加
    for formula in formulas_data:
        for comp in formula.get('composition', []):
            herb_set.add(comp['herb'])

    # 方剂词表
    formula_set = set()
    for formula in formulas_data:
        formula_set.add(formula['name'])

    symptom_vocab = {s: i for i, s in enumerate(sorted(symptom_set))}
    herb_vocab = {h: i for i, h in enumerate(sorted(herb_set))}
    formula_vocab = {f: i for i, f in enumerate(sorted(formula_set))}

    return symptom_vocab, herb_vocab, formula_vocab


def build_training_samples(formulas_data, symptom_vocab, herb_vocab, num_augmented=20):
    """
    从方剂数据生成训练样本

    每个方剂 → 多个训练样本 (通过随机组合症状标签)
    """
    samples = []

    for formula in formulas_data:
        name = formula['name']
        tags = formula.get('symptomTags', [])
        composition = formula.get('composition', [])

        if not tags or not composition:
            continue

        # 基础样本: 使用所有symptomTags
        base_herbs = []
        for comp in composition:
            dosage = parse_dosage(comp.get('amount', '9g'))
            base_herbs.append({
                'name': comp['herb'],
                'dosage': dosage,
            })

        # 原始样本
        samples.append({
            'symptoms': tags,
            'formula_name': name,
            'herbs': base_herbs,
        })

        # 数据增强: 生成子集组合
        for _ in range(num_augmented):
            if len(tags) <= 1:
                augmented_tags = tags[:]
            else:
                # 随机选择 50%-100% 的标签
                k = random.randint(max(1, len(tags) // 2), len(tags))
                augmented_tags = random.sample(tags, k)

            samples.append({
                'symptoms': augmented_tags,
                'formula_name': name,
                'herbs': base_herbs,
            })

    return samples


def load_raw_dataset_filtered(raw_dir, min_count=5):
    """从 download_dataset.py 生成的原始数据加载，并过滤低频词"""
    merged_path = os.path.join(raw_dir, 'merged_prescriptions.json')
    if not os.path.exists(merged_path):
        raise FileNotFoundError(f'{merged_path} 不存在，请先运行 scripts/download_dataset.py')

    with open(merged_path, 'r', encoding='utf-8') as f:
        prescriptions = json.load(f)

    # 统计频率
    from collections import Counter
    symptom_counter = Counter()
    herb_counter = Counter()

    for p in prescriptions:
        for s in set(p.get('symptoms', [])):  # 使用 set 避免同一处方内重复计数
            symptom_counter[s] += 1
        for h in set(h['name'] for h in p.get('herbs', [])):
            herb_counter[h] += 1

    # 过滤低频词
    all_symptoms = {s for s, c in symptom_counter.items() if c >= min_count}
    all_herbs = {h for h, c in herb_counter.items() if c >= min_count}

    return prescriptions, all_symptoms, all_herbs


def build_samples_from_raw(prescriptions, symptom_vocab, herb_vocab, num_augmented=5):
    """从原始处方数据生成训练样本"""
    samples = []

    for p in prescriptions:
        symptoms = p.get('symptoms', [])
        herbs_info = p.get('herbs', [])

        if not symptoms or not herbs_info:
            continue

        # 过滤：只保留在词表中的症状和药材
        valid_symptoms = [s for s in symptoms if s in symptom_vocab]
        valid_herbs = [
            {'name': h['name'], 'dosage': h.get('dosage', 9.0)}
            for h in herbs_info if h['name'] in herb_vocab
        ]

        if not valid_symptoms or not valid_herbs:
            continue

        # 基础样本
        samples.append({
            'symptoms': valid_symptoms,
            'herbs': valid_herbs,
        })

        # 数据增强 (PTM数据量大，减少增强倍数)
        aug_count = num_augmented if p.get('is_classic') else min(num_augmented, 3)
        for _ in range(aug_count):
            if len(valid_symptoms) <= 1:
                aug_symptoms = valid_symptoms[:]
            else:
                k = random.randint(max(1, len(valid_symptoms) // 2), len(valid_symptoms))
                aug_symptoms = random.sample(valid_symptoms, k)
            samples.append({
                'symptoms': aug_symptoms,
                'herbs': valid_herbs,
            })

    return samples


def main():
    parser = argparse.ArgumentParser(description='准备中医方剂训练数据 (中医开方模型)')
    parser.add_argument('--data_dir', type=str, default='../src/data',
                        help='原始数据目录 (包含 herbs.json, formulas.json, symptoms.json)')
    parser.add_argument('--output_dir', type=str, default='data',
                        help='输出数据目录')
    parser.add_argument('--raw_dir', type=str, default='data/raw',
                        help='下载的原始数据目录 (download_dataset.py 输出)')
    parser.add_argument('--use_raw', action='store_true',
                        help='使用下载的大规模原始数据集 (PTM + 经典方剂)')
    parser.add_argument('--num_augmented', type=int, default=20,
                        help='每个方剂的增强样本数')
    parser.add_argument('--val_ratio', type=float, default=0.15,
                        help='验证集比例')
    parser.add_argument('--min_count', type=int, default=5,
                        help='药材和症状的最小出现次数，低于此频率将被过滤')
    parser.add_argument('--seed', type=int, default=42, help='随机种子')
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    print('=' * 60)
    print('  岐黄AI自动开方模型 — 数据预处理')
    print('=' * 60)

    if args.use_raw:
        # ========== 大规模数据集模式 ==========
        print(f'\n📂 使用大规模数据集: {args.raw_dir} (过滤频率 < {args.min_count} 的词)')
        prescriptions, all_symptoms, all_herbs = load_raw_dataset_filtered(args.raw_dir, args.min_count)
        print(f'   ✅ 处方: {len(prescriptions)} 个')
        print(f'   · 药材种类 (频次>={args.min_count}): {len(all_herbs)}')
        print(f'   · 症状标签 (频次>={args.min_count}): {len(all_symptoms)}')

        # 构建词表
        print('\n📝 构建词表...')
        symptom_vocab = {s: i for i, s in enumerate(sorted(all_symptoms))}
        herb_vocab = {h: i for i, h in enumerate(sorted(all_herbs))}

        print(f'   · 症状标签: {len(symptom_vocab)} 个')
        print(f'   · 药材:     {len(herb_vocab)} 味')

        # 保存词表
        for name, vocab in [('symptom_vocab', symptom_vocab), ('herb_vocab', herb_vocab)]:
            with open(os.path.join(args.output_dir, f'{name}.json'), 'w', encoding='utf-8') as f:
                json.dump(vocab, f, ensure_ascii=False, indent=2)
        print('   ✅ 词表已保存')

        # 生成训练样本
        aug = min(args.num_augmented, 3)  # 大数据集减少增强
        print(f'\n🔧 生成训练样本 (增强倍数: {aug}x for PTM, {args.num_augmented}x for 经典方)...')
        all_samples = build_samples_from_raw(prescriptions, symptom_vocab, herb_vocab, args.num_augmented)

    else:
        # ========== 原有小数据集模式 ==========
        print(f'\n📂 加载数据: {args.data_dir}')

        with open(os.path.join(args.data_dir, 'herbs.json'), 'r', encoding='utf-8') as f:
            herbs_data = json.load(f)
        print(f'   ✅ 药材: {len(herbs_data)} 味')

        with open(os.path.join(args.data_dir, 'formulas.json'), 'r', encoding='utf-8') as f:
            formulas_data = json.load(f)
        print(f'   ✅ 方剂: {len(formulas_data)} 个')

        with open(os.path.join(args.data_dir, 'symptoms.json'), 'r', encoding='utf-8') as f:
            symptoms_data = json.load(f)
        print(f'   ✅ 症状数据: 已加载')

        # 构建词表
        print('\n📝 构建词表...')
        symptom_vocab, herb_vocab, formula_vocab = build_vocabs(herbs_data, formulas_data, symptoms_data)
        print(f'   · 症状标签: {len(symptom_vocab)} 个')
        print(f'   · 药材:     {len(herb_vocab)} 味')

        # 保存词表
        for name, vocab in [('symptom_vocab', symptom_vocab), ('herb_vocab', herb_vocab)]:
            with open(os.path.join(args.output_dir, f'{name}.json'), 'w', encoding='utf-8') as f:
                json.dump(vocab, f, ensure_ascii=False, indent=2)
        print('   ✅ 词表已保存')

        # 生成训练样本
        print(f'\n🔧 生成训练样本 (每方 {args.num_augmented} 个增强样本)...')
        all_samples = build_training_samples(formulas_data, symptom_vocab, herb_vocab, args.num_augmented)

    print(f'   · 总样本数: {len(all_samples)}')

    # 划分训练/验证集
    random.shuffle(all_samples)
    val_size = int(len(all_samples) * args.val_ratio)
    val_samples = all_samples[:val_size]
    train_samples = all_samples[val_size:]

    print(f'   · 训练集: {len(train_samples)} 样本')
    print(f'   · 验证集: {len(val_samples)} 样本')

    # 保存
    with open(os.path.join(args.output_dir, 'train_data.json'), 'w', encoding='utf-8') as f:
        json.dump(train_samples, f, ensure_ascii=False, indent=2)

    with open(os.path.join(args.output_dir, 'val_data.json'), 'w', encoding='utf-8') as f:
        json.dump(val_samples, f, ensure_ascii=False, indent=2)

    # 保存元数据
    meta = {
        'num_symptoms': len(symptom_vocab),
        'num_herbs': len(herb_vocab),
        'total_samples': len(all_samples),
        'train_samples': len(train_samples),
        'val_samples': len(val_samples),
        'num_augmented_per_formula': args.num_augmented,
        'use_raw': args.use_raw,
    }
    with open(os.path.join(args.output_dir, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f'\n✅ 数据预处理完成! 输出目录: {args.output_dir}/')
    print('=' * 60)


if __name__ == '__main__':
    main()
