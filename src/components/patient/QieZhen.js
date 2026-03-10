'use client';

import { useDiagnosis } from '@/context/DiagnosisContext';
import symptomsData from '@/data/symptoms.json';

export default function QieZhen() {
    const { diagnosis, updateQieZhen } = useDiagnosis();
    const { qieZhen } = diagnosis;
    const data = symptomsData.qieZhen;

    const togglePulse = (label) => {
        const current = qieZhen.pulseType || [];
        const updated = current.includes(label)
            ? current.filter(p => p !== label)
            : [...current, label];
        updateQieZhen({ pulseType: updated });
    };

    const handleSelect = (field, value) => {
        updateQieZhen({ [field]: qieZhen[field] === value ? '' : value });
    };

    return (
        <div className="card page-enter">
            <div className="card-header">
                <div className="card-icon">✋</div>
                <div>
                    <div className="card-title">切诊</div>
                    <div className="card-subtitle">脉象诊察</div>
                </div>
            </div>

            {/* 脉象类型 */}
            <div className="form-section">
                <div className="form-section-title">🫀 脉象类型（可多选）</div>
                <div className="option-grid wide">
                    {data.pulseType.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${(qieZhen.pulseType || []).includes(item.label) ? 'selected' : ''}`}
                            onClick={() => togglePulse(item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                            <div className="option-card-desc">{item.desc}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 脉力 */}
            <div className="form-section">
                <div className="form-section-title">💪 脉力</div>
                <div className="option-grid">
                    {data.pulseStrength.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${qieZhen.pulseStrength === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('pulseStrength', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
