'use client';

import { useApp } from '@/context/AppContext';

export default function WenZhen() {
    const { currentPatient, updateDiagnosis } = useApp();
    const { wenZhen } = currentPatient.diagnosis;

    const options = {
        voiceType: ['正常', '声音低微', '声音嘶哑', '语声重浊'],
        breathType: ['正常', '气短', '气促', '呼吸深长'],
        coughType: ['无咳嗽', '干咳少痰', '咳嗽痰多色白', '咳嗽痰黄稠', '咳声重浊'],
        bodySmell: ['正常', '口臭', '体味重'],
    };

    const handleChange = (field, value) => {
        updateDiagnosis('wenZhen', { [field]: value });
    };

    return (
        <div className="card">
            <div className="card-header">
                <div className="card-icon">👂</div>
                <div>
                    <div className="card-title">闻诊</div>
                    <div className="card-subtitle">听声音、嗅气味，了解患者身体状况</div>
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">声音观察</div>
                <div style={{ display: 'grid', gap: 'var(--space-lg)' }}>
                    <div>
                        <label className="form-label">声音特点</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {options.voiceType.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wenZhen.voiceType === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('voiceType', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="form-label">呼吸特点</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {options.breathType.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wenZhen.breathType === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('breathType', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">咳嗽情况</div>
                <div className="option-grid">
                    {options.coughType.map(opt => (
                        <div
                            key={opt}
                            className={`option-card ${wenZhen.coughType === opt ? 'selected' : ''}`}
                            onClick={() => handleChange('coughType', opt)}
                        >
                            <div className="option-card-label">{opt}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">气味观察</div>
                <div className="option-grid">
                    {options.bodySmell.map(opt => (
                        <div
                            key={opt}
                            className={`option-card ${wenZhen.bodySmell === opt ? 'selected' : ''}`}
                            onClick={() => handleChange('bodySmell', opt)}
                        >
                            <div className="option-card-label">{opt}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
