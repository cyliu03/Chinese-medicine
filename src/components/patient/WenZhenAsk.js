'use client';

import { useDiagnosis } from '@/context/DiagnosisContext';
import symptomsData from '@/data/symptoms.json';

export default function WenZhenAsk() {
    const { diagnosis, updateWenZhenAsk } = useDiagnosis();
    const { wenZhenAsk } = diagnosis;
    const data = symptomsData.wenZhenAsk;

    const toggleSymptom = (label) => {
        const current = wenZhenAsk.symptoms || [];
        const updated = current.includes(label)
            ? current.filter(s => s !== label)
            : [...current, label];
        updateWenZhenAsk({ symptoms: updated });
    };

    const handleSelect = (field, value) => {
        updateWenZhenAsk({ [field]: wenZhenAsk[field] === value ? '' : value });
    };

    return (
        <div className="card page-enter">
            <div className="card-header">
                <div className="card-icon">💬</div>
                <div>
                    <div className="card-title">问诊</div>
                    <div className="card-subtitle">详细询问症状、病史、生活习惯</div>
                </div>
            </div>

            {/* 主诉 */}
            <div className="form-section">
                <div className="form-section-title">📝 主诉（主要不适）</div>
                <div className="form-group">
                    <textarea
                        className="form-textarea"
                        placeholder="请描述您目前最主要的不适症状，例如：头痛三天，伴有发热恶寒..."
                        value={wenZhenAsk.mainComplaint || ''}
                        onChange={(e) => updateWenZhenAsk({ mainComplaint: e.target.value })}
                        rows={3}
                    />
                </div>
            </div>

            {/* 症状多选 */}
            <div className="form-section">
                <div className="form-section-title">🩺 伴随症状（可多选）</div>
                <div className="option-grid wide">
                    {data.symptoms.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${(wenZhenAsk.symptoms || []).includes(item.label) ? 'selected' : ''}`}
                            onClick={() => toggleSymptom(item.label)}
                        >
                            <div className="option-card-icon">{item.icon}</div>
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 病程 */}
            <div className="form-section">
                <div className="form-section-title">⏱️ 病程（症状持续时间）</div>
                <div className="option-grid">
                    {data.duration.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhenAsk.duration === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('duration', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 饮食偏好 */}
            <div className="form-section">
                <div className="form-section-title">🍵 饮食偏好</div>
                <div className="option-grid">
                    {data.dietPreference.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhenAsk.dietPreference === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('dietPreference', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 汗出 */}
            <div className="form-section">
                <div className="form-section-title">💦 汗出情况</div>
                <div className="option-grid wide">
                    {data.sweating.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhenAsk.sweating === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('sweating', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 口渴 */}
            <div className="form-section">
                <div className="form-section-title">💧 口渴情况</div>
                <div className="option-grid wide">
                    {data.thirst.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhenAsk.thirst === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('thirst', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 睡眠 */}
            <div className="form-section">
                <div className="form-section-title">😴 睡眠情况</div>
                <div className="option-grid wide">
                    {data.sleepQuality.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhenAsk.sleepQuality === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('sleepQuality', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 情绪 */}
            <div className="form-section">
                <div className="form-section-title">🧠 情绪状态</div>
                <div className="option-grid wide">
                    {data.emotionState.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wenZhenAsk.emotionState === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('emotionState', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 既往病史 */}
            <div className="form-section">
                <div className="form-section-title">📋 既往病史</div>
                <div className="form-group">
                    <textarea
                        className="form-textarea"
                        placeholder="请填写您的既往病史，例如：高血压、糖尿病、过敏史等..."
                        value={wenZhenAsk.medicalHistory || ''}
                        onChange={(e) => updateWenZhenAsk({ medicalHistory: e.target.value })}
                        rows={2}
                    />
                </div>
            </div>
        </div>
    );
}
