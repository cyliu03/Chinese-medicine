'use client';

import { useRef } from 'react';
import { useDiagnosis } from '@/context/DiagnosisContext';
import symptomsData from '@/data/symptoms.json';

export default function WangZhen() {
    const { diagnosis, updateWangZhen } = useDiagnosis();
    const { wangZhen } = diagnosis;
    const faceFileRef = useRef(null);
    const tongueFileRef = useRef(null);

    const data = symptomsData.wangZhen;

    const handleSelect = (field, value) => {
        updateWangZhen({ [field]: wangZhen[field] === value ? '' : value });
    };

    const handlePhoto = (field, e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (ev) => updateWangZhen({ [field]: ev.target.result });
            reader.readAsDataURL(file);
        }
    };

    return (
        <div className="card page-enter">
            <div className="card-header">
                <div className="card-icon">👁️</div>
                <div>
                    <div className="card-title">望诊</div>
                    <div className="card-subtitle">观察面色、舌象、体态、精神状态</div>
                </div>
            </div>

            {/* 面色 */}
            <div className="form-section">
                <div className="form-section-title">🎨 面色观察</div>
                <div className="option-grid">
                    {data.faceColor.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wangZhen.faceColor === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('faceColor', item.label)}
                        >
                            <div className="option-card-icon">{item.icon}</div>
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 拍照识图 — 面部 */}
            <div className="form-section">
                <div className="form-section-title">📸 面部拍照（可选）</div>
                <div
                    className={`photo-upload-area ${wangZhen.facePhoto ? 'has-image' : ''}`}
                    onClick={() => faceFileRef.current?.click()}
                >
                    {wangZhen.facePhoto ? (
                        <img src={wangZhen.facePhoto} alt="面部照片" className="photo-preview" />
                    ) : (
                        <>
                            <div className="photo-upload-icon">📷</div>
                            <div className="photo-upload-text">点击上传面部照片，辅助望诊判断</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--light-ink)', marginTop: '4px' }}>
                                支持 JPG / PNG 格式
                            </div>
                        </>
                    )}
                </div>
                <input ref={faceFileRef} type="file" accept="image/*" hidden onChange={(e) => handlePhoto('facePhoto', e)} />
            </div>

            {/* 舌色 */}
            <div className="form-section">
                <div className="form-section-title">👅 舌色</div>
                <div className="option-grid wide">
                    {data.tongueColor.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wangZhen.tongueColor === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('tongueColor', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                            <div className="option-card-desc">{item.desc}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 舌苔 */}
            <div className="form-section">
                <div className="form-section-title">🫧 舌苔</div>
                <div className="option-grid wide">
                    {data.tongueCoating.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wangZhen.tongueCoating === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('tongueCoating', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                            <div className="option-card-desc">{item.desc}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 舌形 */}
            <div className="form-section">
                <div className="form-section-title">📐 舌形</div>
                <div className="option-grid wide">
                    {data.tongueShape.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wangZhen.tongueShape === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('tongueShape', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                            <div className="option-card-desc">{item.desc}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 拍照识图 — 舌头 */}
            <div className="form-section">
                <div className="form-section-title">📸 舌象拍照（可选）</div>
                <div
                    className={`photo-upload-area ${wangZhen.tonguePhoto ? 'has-image' : ''}`}
                    onClick={() => tongueFileRef.current?.click()}
                >
                    {wangZhen.tonguePhoto ? (
                        <img src={wangZhen.tonguePhoto} alt="舌象照片" className="photo-preview" />
                    ) : (
                        <>
                            <div className="photo-upload-icon">📷</div>
                            <div className="photo-upload-text">点击上传舌头照片，辅助舌象分析</div>
                        </>
                    )}
                </div>
                <input ref={tongueFileRef} type="file" accept="image/*" hidden onChange={(e) => handlePhoto('tonguePhoto', e)} />
            </div>

            {/* 体态 */}
            <div className="form-section">
                <div className="form-section-title">🧍 体态</div>
                <div className="option-grid">
                    {data.bodyType.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wangZhen.bodyType === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('bodyType', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 精神 */}
            <div className="form-section">
                <div className="form-section-title">💡 精神状态</div>
                <div className="option-grid">
                    {data.spirit.map(item => (
                        <div
                            key={item.id}
                            className={`option-card ${wangZhen.spirit === item.label ? 'selected' : ''}`}
                            onClick={() => handleSelect('spirit', item.label)}
                        >
                            <div className="option-card-label">{item.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
