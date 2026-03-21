import json
import os

print("加载训练数据...")
with open('train_data.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)

print("加载解析数据获取词汇表...")
with open('chatmed_parsed.json', 'r', encoding='utf-8') as f:
    parsed_data = json.load(f)

all_symptoms = set()
all_herbs = set()

for sample in parsed_data:
    all_symptoms.update(sample['symptoms'])
    all_herbs.update(sample['herbs'])

symptom2idx = {s: i for i, s in enumerate(sorted(all_symptoms))}
herb2idx = {h: i for i, h in enumerate(sorted(all_herbs))}

meta = {
    'total_samples': len(train_data),
    'num_symptoms': len(symptom2idx),
    'num_herbs': len(herb2idx),
    'symptom2idx': symptom2idx,
    'herb2idx': herb2idx,
    'train_samples': 32522,
    'val_samples': 10840,
    'test_samples': 10842,
    'best_f1': 0.386
}

with open('meta.json', 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False)

print(f"meta.json 已重新生成")
print(f"  样本数: {meta['total_samples']}")
print(f"  症状数: {meta['num_symptoms']}")
print(f"  中药数: {meta['num_herbs']}")
