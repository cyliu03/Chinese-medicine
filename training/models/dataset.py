"""
TCM Dataset — 中医方剂训练数据集

将症状-方剂映射转换为 PyTorch Dataset
"""

import json
import torch
from torch.utils.data import Dataset
import numpy as np
import random


class TCMDataset(Dataset):
    """
    中医方剂训练数据集

    每个样本:
        input:  症状 multi-hot 向量
        target: (方剂索引, 药材 multi-hot, 剂量向量)
    """

    def __init__(self, data_path, symptom_vocab, herb_vocab, formula_vocab, augment=True):
        """
        Args:
            data_path: 训练数据 JSON 路径
            symptom_vocab: {symptom_name: index} 词表
            herb_vocab: {herb_name: index} 词表
            formula_vocab: {formula_name: index} 词表
            augment: 是否做数据增强
        """
        with open(data_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

        self.symptom_vocab = symptom_vocab
        self.herb_vocab = herb_vocab
        self.formula_vocab = formula_vocab
        self.num_symptoms = len(symptom_vocab)
        self.num_herbs = len(herb_vocab)
        self.num_formulas = len(formula_vocab)
        self.augment = augment

    def __len__(self):
        return len(self.raw_data)

    def __getitem__(self, idx):
        sample = self.raw_data[idx]

        # 构建症状 multi-hot 向量
        symptom_vec = torch.zeros(self.num_symptoms)
        symptoms = sample['symptoms']

        if self.augment:
            # 数据增强：随机丢弃 10-30% 的症状模拟不完整问诊
            dropout_rate = random.uniform(0.0, 0.3)
            symptoms = [s for s in symptoms if random.random() > dropout_rate]
            # 至少保留1个症状
            if len(symptoms) == 0 and len(sample['symptoms']) > 0:
                symptoms = [random.choice(sample['symptoms'])]

        for symptom in symptoms:
            if symptom in self.symptom_vocab:
                symptom_vec[self.symptom_vocab[symptom]] = 1.0

        # 方剂目标 (分类索引)
        formula_idx = self.formula_vocab.get(sample['formula_name'], 0)

        # 药材 multi-hot 向量
        herb_vec = torch.zeros(self.num_herbs)
        dosage_vec = torch.zeros(self.num_herbs)
        for herb_info in sample['herbs']:
            herb_name = herb_info['name']
            dosage = herb_info.get('dosage', 9.0)  # 默认9g
            if herb_name in self.herb_vocab:
                h_idx = self.herb_vocab[herb_name]
                herb_vec[h_idx] = 1.0
                dosage_vec[h_idx] = dosage

        return {
            'symptoms': symptom_vec,
            'formula_target': torch.tensor(formula_idx, dtype=torch.long),
            'herb_target': herb_vec,
            'dosage_target': dosage_vec,
        }


class TCMInferenceDataset(Dataset):
    """推理用数据集 — 只需要症状输入"""

    def __init__(self, symptom_list, symptom_vocab):
        """
        Args:
            symptom_list: list of list of symptom strings
            symptom_vocab: {symptom_name: index}
        """
        self.symptom_list = symptom_list
        self.symptom_vocab = symptom_vocab
        self.num_symptoms = len(symptom_vocab)

    def __len__(self):
        return len(self.symptom_list)

    def __getitem__(self, idx):
        symptoms = self.symptom_list[idx]
        symptom_vec = torch.zeros(self.num_symptoms)
        for s in symptoms:
            if s in self.symptom_vocab:
                symptom_vec[self.symptom_vocab[s]] = 1.0
        return symptom_vec
