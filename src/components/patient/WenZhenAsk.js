'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';

export default function WenZhenAsk() {
    const { currentPatient, updateDiagnosis } = useApp();
    const { wenZhenAsk } = currentPatient.diagnosis;

    const symptomOptions = [
        '头痛', '发热', '恶寒', '失眠', '腹痛', '腹胀', '恶心呕吐', '腹泻', '便秘',
        '心悸', '胸闷', '头晕', '耳鸣', '目赤', '咽痛', '口干口渴', '腰膝酸软',
        '关节疼痛', '四肢冰冷', '多汗', '盗汗', '水肿', '月经不调', '食欲不振', '乏力',
    ];

    const durationOptions = ['1天内', '1-3天', '3-7天', '1-2周', '2周以上', '慢性反复'];
    const sweatingOptions = ['正常无汗', '汗出恶风', '自汗(白天出汗)', '盗汗(夜间出汗)', '大汗'];
    const thirstOptions = ['正常', '口渴多饮', '口干不欲饮', '渴喜热饮'];
    const sleepOptions = ['正常', '入睡困难', '多梦易醒', '嗜睡'];
    const emotionOptions = ['正常', '烦躁易怒', '情绪低落', '焦虑紧张'];

    const handleSymptomToggle = (symptom) => {
        const current = wenZhenAsk.symptoms || [];
        const updated = current.includes(symptom)
            ? current.filter(s => s !== symptom)
            : [...current, symptom];
        updateDiagnosis('wenZhenAsk', { symptoms: updated });
    };

    const handleChange = (field, value) => {
        updateDiagnosis('wenZhenAsk', { [field]: value });
    };

    return (
        <div className="card">
            <div className="card-header">
                <div className="card-icon">💬</div>
                <div>
                    <div className="card-title">问诊</div>
                    <div className="card-subtitle">详细询问患者的症状、病史等信息</div>
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">主诉</div>
                <div className="form-group">
                    <textarea
                        className="form-textarea"
                        placeholder="请描述您最主要的不适症状..."
                        value={wenZhenAsk.mainComplaint || ''}
                        onChange={(e) => handleChange('mainComplaint', e.target.value)}
                        rows={2}
                    />
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">症状选择</div>
                <p style={{ fontSize: '0.85rem', color: 'var(--ink-gray)', marginBottom: 'var(--space-sm)' }}>
                    请选择您目前存在的症状（可多选）
                </p>
                <div className="symptom-grid">
                    {symptomOptions.map(symptom => (
                        <div
                            key={symptom}
                            className={`symptom-tag ${(wenZhenAsk.symptoms || []).includes(symptom) ? 'selected' : ''}`}
                            onClick={() => handleSymptomToggle(symptom)}
                        >
                            {symptom}
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">病程</div>
                <div className="option-grid">
                    {durationOptions.map(opt => (
                        <div
                            key={opt}
                            className={`option-card ${wenZhenAsk.duration === opt ? 'selected' : ''}`}
                            onClick={() => handleChange('duration', opt)}
                        >
                            <div className="option-card-label">{opt}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">其他症状</div>
                <div style={{ display: 'grid', gap: 'var(--space-lg)' }}>
                    <div>
                        <label className="form-label">汗出情况</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {sweatingOptions.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wenZhenAsk.sweating === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('sweating', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="form-label">口渴情况</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {thirstOptions.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wenZhenAsk.thirst === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('thirst', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="form-label">睡眠情况</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {sleepOptions.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wenZhenAsk.sleepQuality === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('sleepQuality', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="form-label">情绪状态</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {emotionOptions.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wenZhenAsk.emotionState === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('emotionState', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">病史</div>
                <div className="form-group">
                    <textarea
                        className="form-textarea"
                        placeholder="请描述您的既往病史、过敏史等..."
                        value={wenZhenAsk.medicalHistory || ''}
                        onChange={(e) => handleChange('medicalHistory', e.target.value)}
                        rows={2}
                    />
                </div>
            </div>
        </div>
    );
}
