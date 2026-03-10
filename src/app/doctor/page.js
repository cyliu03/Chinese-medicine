'use client';

import { useState } from 'react';
import Header from '@/components/shared/Header';
import { useDiagnosis } from '@/context/DiagnosisContext';
import Link from 'next/link';

export default function DoctorPage() {
    const { patientSubmissions, setPatientSubmissions } = useDiagnosis();
    const [selectedId, setSelectedId] = useState(null);

    const selected = patientSubmissions.find(s => s.id === selectedId);

    const updateStatus = (id, status, note) => {
        setPatientSubmissions(prev => prev.map(s =>
            s.id === id ? { ...s, status, doctorNote: note || s.doctorNote } : s
        ));
    };

    if (patientSubmissions.length === 0) {
        return (
            <>
                <Header />
                <main className="main-content">
                    <div className="page-enter" style={{ textAlign: 'center' }}>
                        <h1 style={{ fontSize: '1.8rem', letterSpacing: '3px', marginBottom: '16px' }}>👨‍⚕️ 医生工作台</h1>
                        <div className="empty-state">
                            <div className="empty-state-icon">📋</div>
                            <h2>暂无待审处方</h2>
                            <p style={{ marginBottom: '16px' }}>目前没有患者提交的处方需要审核</p>
                            <Link href="/patient" className="btn btn-primary">模拟患者问诊</Link>
                        </div>
                    </div>
                </main>
            </>
        );
    }

    return (
        <>
            <Header />
            <main className="main-content">
                <div className="page-enter">
                    <h1 style={{ fontSize: '1.8rem', letterSpacing: '3px', marginBottom: 'var(--space-lg)', textAlign: 'center' }}>
                        👨‍⚕️ 医生工作台
                    </h1>

                    {!selected ? (
                        /* 待审列表 */
                        <div className="card">
                            <div className="card-header">
                                <div className="card-icon">📋</div>
                                <div>
                                    <div className="card-title">待审处方列表</div>
                                    <div className="card-subtitle">共 {patientSubmissions.length} 条记录</div>
                                </div>
                            </div>

                            {patientSubmissions.map((sub) => (
                                <div
                                    key={sub.id}
                                    className="patient-queue-item"
                                    onClick={() => setSelectedId(sub.id)}
                                    style={{ marginBottom: '8px' }}
                                >
                                    <div className="patient-avatar">
                                        {sub.patientName?.slice(-1) || '?'}
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: 600 }}>{sub.patientName}</div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--ink-gray)' }}>
                                            {new Date(sub.timestamp).toLocaleString('zh-CN')}
                                            {sub.aiResults?.recommendations?.[0] && ` · AI推荐: ${sub.aiResults.recommendations[0].name}`}
                                        </div>
                                    </div>
                                    <span className={`status-badge ${sub.status}`}>
                                        {sub.status === 'pending' ? '待审核' : sub.status === 'approved' ? '已批准' : '已驳回'}
                                    </span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        /* 审核详情 */
                        <ReviewDetail
                            submission={selected}
                            onBack={() => setSelectedId(null)}
                            onApprove={(note) => { updateStatus(selected.id, 'approved', note); setSelectedId(null); }}
                            onReject={(note) => { updateStatus(selected.id, 'rejected', note); setSelectedId(null); }}
                        />
                    )}
                </div>
            </main>
        </>
    );
}

function ReviewDetail({ submission, onBack, onApprove, onReject }) {
    const [doctorNote, setDoctorNote] = useState('');
    const { diagnosis, aiResults } = submission;
    const rec = aiResults?.recommendations?.[0];

    return (
        <div>
            <button className="btn btn-ghost" onClick={onBack} style={{ marginBottom: 'var(--space-lg)' }}>
                ← 返回列表
            </button>

            <div className="review-layout">
                {/* 左侧 — 患者信息 */}
                <div className="card review-panel">
                    <div className="card-header">
                        <div className="card-icon">🩺</div>
                        <div>
                            <div className="card-title">{submission.patientName} 四诊信息</div>
                            <div className="card-subtitle">{new Date(submission.timestamp).toLocaleString('zh-CN')}</div>
                        </div>
                    </div>

                    <div className="diagnosis-category" style={{ marginBottom: '12px' }}>
                        <h4>👁️ 望诊</h4>
                        {diagnosis.wangZhen.faceColor && <div className="diagnosis-item">面色：{diagnosis.wangZhen.faceColor}</div>}
                        {diagnosis.wangZhen.tongueColor && <div className="diagnosis-item">舌色：{diagnosis.wangZhen.tongueColor}</div>}
                        {diagnosis.wangZhen.tongueCoating && <div className="diagnosis-item">舌苔：{diagnosis.wangZhen.tongueCoating}</div>}
                        {diagnosis.wangZhen.tongueShape && <div className="diagnosis-item">舌形：{diagnosis.wangZhen.tongueShape}</div>}
                        {diagnosis.wangZhen.bodyType && <div className="diagnosis-item">体态：{diagnosis.wangZhen.bodyType}</div>}
                        {diagnosis.wangZhen.spirit && <div className="diagnosis-item">精神：{diagnosis.wangZhen.spirit}</div>}
                    </div>

                    <div className="diagnosis-category" style={{ marginBottom: '12px' }}>
                        <h4>👂 闻诊</h4>
                        {diagnosis.wenZhen.voiceType && <div className="diagnosis-item">声音：{diagnosis.wenZhen.voiceType}</div>}
                        {diagnosis.wenZhen.breathType && <div className="diagnosis-item">呼吸：{diagnosis.wenZhen.breathType}</div>}
                        {diagnosis.wenZhen.coughType && <div className="diagnosis-item">咳嗽：{diagnosis.wenZhen.coughType}</div>}
                    </div>

                    <div className="diagnosis-category" style={{ marginBottom: '12px' }}>
                        <h4>💬 问诊</h4>
                        {diagnosis.wenZhenAsk.mainComplaint && <div className="diagnosis-item">主诉：{diagnosis.wenZhenAsk.mainComplaint}</div>}
                        {diagnosis.wenZhenAsk.symptoms?.length > 0 && (
                            <div className="diagnosis-item" style={{ flexWrap: 'wrap' }}>
                                症状：{diagnosis.wenZhenAsk.symptoms.map((s, i) => <span key={i} className="diagnosis-tag">{s}</span>)}
                            </div>
                        )}
                        {diagnosis.wenZhenAsk.duration && <div className="diagnosis-item">病程：{diagnosis.wenZhenAsk.duration}</div>}
                        {diagnosis.wenZhenAsk.sweating && <div className="diagnosis-item">汗出：{diagnosis.wenZhenAsk.sweating}</div>}
                        {diagnosis.wenZhenAsk.thirst && <div className="diagnosis-item">口渴：{diagnosis.wenZhenAsk.thirst}</div>}
                        {diagnosis.wenZhenAsk.sleepQuality && <div className="diagnosis-item">睡眠：{diagnosis.wenZhenAsk.sleepQuality}</div>}
                    </div>

                    <div className="diagnosis-category">
                        <h4>✋ 切诊</h4>
                        {diagnosis.qieZhen.pulseType?.length > 0 && (
                            <div className="diagnosis-item" style={{ flexWrap: 'wrap' }}>
                                脉象：{diagnosis.qieZhen.pulseType.map((p, i) => <span key={i} className="diagnosis-tag">{p}</span>)}
                            </div>
                        )}
                        {diagnosis.qieZhen.pulseStrength && <div className="diagnosis-item">脉力：{diagnosis.qieZhen.pulseStrength}</div>}
                    </div>
                </div>

                {/* 右侧 — AI推荐 */}
                <div className="card review-panel">
                    <div className="card-header">
                        <div className="card-icon">🤖</div>
                        <div>
                            <div className="card-title">AI推荐处方</div>
                            <div className="card-subtitle">请审核以下推荐方剂</div>
                        </div>
                    </div>

                    {rec ? (
                        <>
                            <div style={{ marginBottom: '16px' }}>
                                <div className="formula-name" style={{ fontSize: '1.5rem', marginBottom: '4px' }}>{rec.name}</div>
                                <div className="formula-source">📚 来源：{rec.source} · {rec.author}</div>
                                <div className={`match-score ${rec.matchScore >= 60 ? 'high' : 'medium'}`} style={{ marginTop: '8px' }}>
                                    匹配度 {rec.matchScore}%
                                </div>
                            </div>

                            <div className="form-section">
                                <div className="form-section-title">💊 方剂组成</div>
                                <div className="herb-list">
                                    {rec.composition.map((c, i) => (
                                        <span key={i} className="herb-tag">{c.herb} <span className="herb-amount">{c.amount}</span></span>
                                    ))}
                                </div>
                            </div>

                            <div className="source-note">
                                <strong>📖 学习来源：</strong>基于 <strong>{rec.author}</strong> {rec.source} 中的「{rec.name}」方，
                                原方主治「{rec.syndrome}」。
                            </div>

                            {rec.suggestedModifications?.length > 0 && (
                                <div className="modification-note">
                                    <strong>🔧 AI加减建议：</strong>
                                    <ul style={{ margin: '8px 0 0 16px', fontSize: '0.85rem' }}>
                                        {rec.suggestedModifications.map((mod, i) => (
                                            <li key={i}>{mod.type === 'add' ? '➕ 加' : '➖ 减'} <strong>{mod.herb} {mod.amount}</strong> — {mod.reason}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* 其他推荐 */}
                            {aiResults?.recommendations?.length > 1 && (
                                <div style={{ marginTop: '16px' }}>
                                    <div className="form-section-title">📋 其他推荐</div>
                                    {aiResults.recommendations.slice(1).map((r, i) => (
                                        <div key={i} style={{ padding: '8px', background: 'rgba(245,240,232,0.5)', borderRadius: '8px', marginBottom: '6px', fontSize: '0.85rem' }}>
                                            <strong>{r.name}</strong> · {r.source} · 匹配度 {r.matchScore}%
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="empty-state"><p>无AI推荐结果</p></div>
                    )}

                    {/* 医生批注 & 操作 */}
                    <div className="review-actions" style={{ flexDirection: 'column', gap: '12px' }}>
                        <div className="form-group" style={{ margin: 0 }}>
                            <label className="form-label">📝 医生批注</label>
                            <textarea
                                className="form-textarea"
                                placeholder="请输入审核意见、修改建议或批注..."
                                value={doctorNote}
                                onChange={(e) => setDoctorNote(e.target.value)}
                                rows={3}
                            />
                        </div>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <button className="btn btn-approve" style={{ flex: 1 }} onClick={() => onApprove(doctorNote)}>
                                ✅ 批准处方
                            </button>
                            <button className="btn btn-modify" style={{ flex: 1 }} onClick={() => onApprove(doctorNote || '需修改后使用')}>
                                ✏️ 修改后批准
                            </button>
                            <button className="btn btn-reject" onClick={() => onReject(doctorNote || '处方不适用')}>
                                ❌ 驳回
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
