'use client';

import { useApp } from '@/context/AppContext';

export default function WangZhen() {
    const { currentPatient, updateDiagnosis } = useApp();
    const { wangZhen } = currentPatient.diagnosis;

    const options = {
        faceColor: ['正常', '面色苍白', '面色萎黄', '面色红赤', '面色青紫', '面色晦暗'],
        tongueColor: ['正常', '淡白舌', '红舌', '绛舌', '紫舌', '青舌'],
        tongueCoating: ['薄白苔(正常)', '白厚苔', '白滑苔', '黄苔', '黄腻苔', '无苔/少苔'],
        tongueShape: ['正常', '齿痕舌', '胖大舌', '瘦薄舌', '裂纹舌'],
        bodyType: ['正常', '体瘦', '体胖', '浮肿'],
        spirit: ['正常', '精神疲惫', '烦躁不安', '神志恍惚'],
    };

    const handleChange = (field, value) => {
        updateDiagnosis('wangZhen', { [field]: value });
    };

    return (
        <div className="card">
            <div className="card-header">
                <div className="card-icon">👁️</div>
                <div>
                    <div className="card-title">望诊</div>
                    <div className="card-subtitle">观察患者的面色、舌象、体态等外在表现</div>
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">面色观察</div>
                <div className="option-grid">
                    {options.faceColor.map(opt => (
                        <div
                            key={opt}
                            className={`option-card ${wangZhen.faceColor === opt ? 'selected' : ''}`}
                            onClick={() => handleChange('faceColor', opt)}
                        >
                            <div className="option-card-label">{opt}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">舌象观察</div>
                <div style={{ display: 'grid', gap: 'var(--space-md)' }}>
                    <div>
                        <label className="form-label">舌色</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {options.tongueColor.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wangZhen.tongueColor === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('tongueColor', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="form-label">舌苔</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {options.tongueCoating.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wangZhen.tongueCoating === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('tongueCoating', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="form-label">舌形</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {options.tongueShape.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wangZhen.tongueShape === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('tongueShape', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">体态与精神</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
                    <div>
                        <label className="form-label">体态</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {options.bodyType.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wangZhen.bodyType === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('bodyType', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="form-label">精神状态</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {options.spirit.map(opt => (
                                <div
                                    key={opt}
                                    className={`option-card ${wangZhen.spirit === opt ? 'selected' : ''}`}
                                    onClick={() => handleChange('spirit', opt)}
                                >
                                    <div className="option-card-label">{opt}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
