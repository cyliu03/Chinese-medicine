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


def main():
    parser = argparse.ArgumentParser(description='准备中医方剂训练数据')
    parser.add_argument('--data_dir', type=str, default='../src/data',
                        help='原始数据目录 (包含 herbs.json, formulas.json, symptoms.json)')
    parser.add_argument('--output_dir', type=str, default='data',
                        help='输出数据目录')
    parser.add_argument('--num_augmented', type=int, default=20,
                        help='每个方剂的增强样本数')
    parser.add_argument('--val_ratio', type=float, default=0.15,
                        help='验证集比例')
    parser.add_argument('--seed', type=int, default=42, help='随机种子')
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    print('=' * 60)
    print('  中医方剂推荐 — 数据预处理')
    print('=' * 60)

    # 加载原始数据
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
    print(f'   · 方剂:     {len(formula_vocab)} 个')

    # 保存词表
    with open(os.path.join(args.output_dir, 'symptom_vocab.json'), 'w', encoding='utf-8') as f:
        json.dump(symptom_vocab, f, ensure_ascii=False, indent=2)

    with open(os.path.join(args.output_dir, 'herb_vocab.json'), 'w', encoding='utf-8') as f:
        json.dump(herb_vocab, f, ensure_ascii=False, indent=2)

    with open(os.path.join(args.output_dir, 'formula_vocab.json'), 'w', encoding='utf-8') as f:
        json.dump(formula_vocab, f, ensure_ascii=False, indent=2)

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
        'num_formulas': len(formula_vocab),
        'total_samples': len(all_samples),
        'train_samples': len(train_samples),
        'val_samples': len(val_samples),
        'num_augmented_per_formula': args.num_augmented,
    }
    with open(os.path.join(args.output_dir, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f'\n✅ 数据预处理完成! 输出目录: {args.output_dir}/')
    print('=' * 60)


if __name__ == '__main__':
    main()
