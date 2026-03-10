'use client';

import { useDiagnosis } from '@/context/DiagnosisContext';
import symptomsData from '@/data/symptoms.json';

export default function WenZhen() {
    const { diagnosis, updateWenZhen } = useDiagnosis();
    const { wenZhen } = diagnosis;
    const data = symptomsData.wenZhen;

    const handleSelect = (field, value) => {
        updateWenZhen({ [field]: wenZhen[field] === value ? '' : value });
    };

    return (
        <div className="card page-enter">
            <div className="card-header">
                <div className="card-icon">👂</div>
                <div>
                    <div className="card-title">闻诊</div>
                    <div className="card-subtitle">听声音、辨气味</div>
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">🗣️ 声音特征</div>
                <div className="option-grid wide">
                    {data.voiceType.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhen.voiceType === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('voiceType', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">🌬️ 呼吸特征</div>
                <div className="option-grid wide">
                    {data.breathType.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhen.breathType === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('breathType', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">😷 咳嗽情况</div>
                <div className="option-grid wide">
                    {data.coughType.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhen.coughType === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('coughType', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <div className="form-section-title">👃 气味</div>
                <div className="option-grid wide">
                    {data.bodySmell.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhen.bodySmell === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('bodySmell', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
