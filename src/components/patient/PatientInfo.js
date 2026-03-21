'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';

export default function PatientInfo() {
    const { currentPatient, loginAsPatient, setCurrentStep } = useApp();
    const [formData, setFormData] = useState({
        name: currentPatient.name || '',
        age: currentPatient.age || '',
        gender: currentPatient.gender || '',
        phone: currentPatient.phone || '',
    });

    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = () => {
        loginAsPatient(formData);
        setCurrentStep(1);
    };

    const isValid = formData.name && formData.age && formData.gender;

    return (
        <div className="card">
            <div className="card-header">
                <div className="card-icon">👤</div>
                <div>
                    <div className="card-title">患者基本信息</div>
                    <div className="card-subtitle">请填写您的基本信息，便于医生了解您的情况</div>
                </div>
            </div>

            <div className="form-section">
                <div className="form-group">
                    <label className="form-label">姓名 *</label>
                    <input
                        type="text"
                        className="form-input"
                        placeholder="请输入您的姓名"
                        value={formData.name}
                        onChange={(e) => handleChange('name', e.target.value)}
                    />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
                    <div className="form-group">
                        <label className="form-label">年龄 *</label>
                        <input
                            type="number"
                            className="form-input"
                            placeholder="请输入年龄"
                            value={formData.age}
                            onChange={(e) => handleChange('age', e.target.value)}
                        />
                    </div>
                    <div className="form-group">
                        <label className="form-label">性别 *</label>
                        <div className="option-grid" style={{ marginTop: 'var(--space-sm)' }}>
                            {['男', '女'].map(g => (
                                <div
                                    key={g}
                                    className={`option-card ${formData.gender === g ? 'selected' : ''}`}
                                    onClick={() => handleChange('gender', g)}
                                >
                                    <div className="option-card-icon">{g === '男' ? '👨' : '👩'}</div>
                                    <div className="option-card-label">{g}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="form-group">
                    <label className="form-label">联系电话</label>
                    <input
                        type="tel"
                        className="form-input"
                        placeholder="请输入联系电话（选填）"
                        value={formData.phone}
                        onChange={(e) => handleChange('phone', e.target.value)}
                    />
                </div>
            </div>

            <div style={{ marginTop: 'var(--space-lg)', textAlign: 'center' }}>
                <button
                    className="btn btn-primary btn-lg"
                    disabled={!isValid}
                    onClick={handleSubmit}
                >
                    确认信息，开始问诊 →
                </button>
            </div>

            <div style={{ marginTop: 'var(--space-lg)', padding: 'var(--space-md)', background: 'rgba(201,169,110,0.1)', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', color: 'var(--ink-gray)' }}>
                <p style={{ marginBottom: 'var(--space-sm)' }}>📌 <strong>温馨提示：</strong></p>
                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    <li>本系统仅供辅助参考，不替代专业医疗诊断</li>
                    <li>如有紧急情况，请立即就医</li>
                    <li>您的信息将被安全保存，仅用于诊断参考</li>
                </ul>
            </div>
        </div>
    );
}
