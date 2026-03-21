'use client';

import { useApp } from '@/context/AppContext';

export default function QieZhen() {
    const { currentPatient, updateDiagnosis } = useApp();
    const { qieZhen } = currentPatient.diagnosis;

    const pulseTypeOptions = [
        '浮脉', '沉脉', '迟脉', '数脉', '滑脉', '涩脉', 
        '弦脉', '紧脉', '细脉', '洪脉', '虚脉', '实脉',
        '弱脉', '结脉', '缓脉', '浮缓脉',
    ];

    const pulseStrengthOptions = ['中等(正常)', '有力', '无力'];
    const pulseRhythmOptions = ['规则(正常)', '不规则', '间歇'];
    const abdomenPainOptions = ['无异常', '喜按', '压痛', '拒按', '反跳痛'];

    const handlePulseTypeToggle = (pulse) => {
        const current = qieZhen.pulseType || [];
        const updated = current.includes(pulse)
            ? current.filter(p => p !== pulse)
            : [...current, pulse];
        updateDiagnosis('qieZhen', { pulseType: updated });
    };

    const handleChange = (field, value) => {
        updateDiagnosis('qieZhen', { [field]: value });
    };

    return (
        <div className="card">
            <div className="card-header">
                <div className="card-icon">✋</div>
                <div>
                    <div className="card-title">切诊</div>
                    <div className="card-subtitle">脉诊、按诊，了解患者体内情况</div>
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">脉象</div>
                <p style={{ fontSize: '0.85rem', color: 'var(--ink-gray)', marginBottom: 'var(--space-sm)' }}>
                    请选择脉象特征（可多选）
                </p>
                <div className="symptom-grid">
                    {pulseTypeOptions.map(pulse => (
                        <div
                            key={pulse}
                            className={`symptom-tag ${(qieZhen.pulseType || []).includes(pulse) ? 'selected' : ''}`}
                            onClick={() => handlePulseTypeToggle(pulse)}
                        >
                            {pulse}
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">脉力</div>
                <div className="option-grid">
                    {pulseStrengthOptions.map(opt => (
                        <div
                            key={opt}
                            className={`option-card ${qieZhen.pulseStrength === opt ? 'selected' : ''}`}
                            onClick={() => handleChange('pulseStrength', opt)}
                        >
                            <div className="option-card-label">{opt}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">脉律</div>
                <div className="option-grid">
                    {pulseRhythmOptions.map(opt => (
                        <div
                            key={opt}
                            className={`option-card ${qieZhen.pulseRhythm === opt ? 'selected' : ''}`}
                            onClick={() => handleChange('pulseRhythm', opt)}
                        >
                            <div className="option-card-label">{opt}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">腹部按诊</div>
                <p style={{ fontSize: '0.85rem', color: 'var(--ink-gray)', marginBottom: 'var(--space-sm)' }}>
                    请选择腹部触诊发现（可多选）
                </p>
                <div className="symptom-grid">
                    {abdomenPainOptions.map(opt => (
                        <div
                            key={opt}
                            className={`symptom-tag ${(qieZhen.abdomenPain || []).includes(opt) ? 'selected' : ''}`}
                            onClick={() => {
                                const current = qieZhen.abdomenPain || [];
                                const updated = current.includes(opt)
                                    ? current.filter(p => p !== opt)
                                    : [...current, opt];
                                updateDiagnosis('qieZhen', { abdomenPain: updated });
                            }}
                        >
                            {opt}
                        </div>
                    ))}
                </div>
            </div>

            <div style={{ 
                marginTop: 'var(--space-lg)', 
                padding: 'var(--space-md)', 
                background: 'rgba(201,169,110,0.1)', 
                borderRadius: 'var(--radius-md)',
                fontSize: '0.85rem',
                color: 'var(--ink-gray)'
            }}>
                <p style={{ marginBottom: 'var(--space-sm)' }}>📌 <strong>脉象参考：</strong></p>
                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    <li><strong>浮脉</strong>：轻取即得，主表证</li>
                    <li><strong>沉脉</strong>：重按始得，主里证</li>
                    <li><strong>迟脉</strong>：一息不足四至，主寒证</li>
                    <li><strong>数脉</strong>：一息五至以上，主热证</li>
                    <li><strong>弦脉</strong>：端直而长，主肝郁</li>
                    <li><strong>滑脉</strong>：往来流利，主痰湿</li>
                </ul>
            </div>
        </div>
    );
}
