'use client';

import Header from '@/components/shared/Header';
import Link from 'next/link';
import { useApp } from '@/context/AppContext';

export default function HomePage() {
    const { diagnoses } = useApp();
    const pendingCount = diagnoses.filter(d => d.status === 'pending').length;
    
    return (
        <>
            <Header />
            <main className="main-content">
                <section className="hero">
                    <div className="hero-icon">🏥</div>
                    <h1 className="hero-title">岐黄AI · 智能中医诊断系统</h1>
                    <p className="hero-desc">
                        传承千年中医智慧，融合现代人工智能技术<br />
                        推荐系统 + 深度学习模型并行融合，精准推荐方剂<br />
                        医患双端协作，确保诊断安全有效
                    </p>
                    <div className="hero-buttons">
                        <Link href="/patient" className="btn btn-primary btn-lg">
                            <span className="btn-icon">🩺</span> 患者问诊
                        </Link>
                        <Link href="/doctor" className="btn btn-secondary btn-lg">
                            <span className="btn-icon">👨‍⚕️</span> 医生工作台
                            {pendingCount > 0 && (
                                <span className="notification-badge">{pendingCount}</span>
                            )}
                        </Link>
                    </div>
                </section>

                <div className="divider" />

                <section className="system-architecture">
                    <h2 className="section-title">🏗️ 系统架构</h2>
                    <div className="architecture-flow">
                        <div className="arch-node patient-node">
                            <div className="arch-icon">👤</div>
                            <div className="arch-title">患者端</div>
                            <div className="arch-desc">智能问诊 · 症状采集</div>
                        </div>
                        <div className="arch-arrow">→</div>
                        <div className="arch-node ai-node">
                            <div className="arch-icon">🤖</div>
                            <div className="arch-title">AI诊断引擎</div>
                            <div className="arch-desc">推荐系统 + 深度学习</div>
                        </div>
                        <div className="arch-arrow">→</div>
                        <div className="arch-node doctor-node">
                            <div className="arch-icon">👨‍⚕️</div>
                            <div className="arch-title">医生端</div>
                            <div className="arch-desc">审核处方 · 患者管理</div>
                        </div>
                    </div>
                </section>

                <div className="divider" />

                <section className="features-grid">
                    <div className="card feature-card">
                        <div className="card-icon" style={{ background: 'linear-gradient(135deg, rgba(196,30,58,0.15), rgba(196,30,58,0.05))' }}>👁️</div>
                        <h3>四诊合参</h3>
                        <p>望闻问切全面采集，遵循传统中医诊断方法，支持舌象拍照辅助分析。</p>
                    </div>
                    <div className="card feature-card">
                        <div className="card-icon" style={{ background: 'linear-gradient(135deg, rgba(91,140,90,0.15), rgba(91,140,90,0.05))' }}>�</div>
                        <h3>双引擎AI</h3>
                        <p>推荐系统(规则匹配) + 深度学习(LSAN模型)并行融合，推荐更精准。</p>
                    </div>
                    <div className="card feature-card">
                        <div className="card-icon" style={{ background: 'linear-gradient(135deg, rgba(201,169,110,0.2), rgba(201,169,110,0.05))' }}>🛡️</div>
                        <h3>医生审核</h3>
                        <p>AI推荐结果交由执业中医师审核，可调整药材剂量，确保安全有效。</p>
                    </div>
                    <div className="card feature-card">
                        <div className="card-icon" style={{ background: 'linear-gradient(135deg, rgba(44,44,44,0.1), rgba(44,44,44,0.03))' }}>�</div>
                        <h3>数据驱动</h3>
                        <p>基于54,204条真实中医药数据训练，覆盖9,629种症状，273种中药。</p>
                    </div>
                </section>

                <div className="divider" />

                <section className="tech-section">
                    <h2 className="section-title">🔬 技术特点</h2>
                    <div className="tech-grid">
                        <div className="tech-item">
                            <div className="tech-label">深度学习模型</div>
                            <div className="tech-value">LSAN (Label-Specific Attention Network)</div>
                        </div>
                        <div className="tech-item">
                            <div className="tech-label">训练样本</div>
                            <div className="tech-value">54,204 条中医药数据</div>
                        </div>
                        <div className="tech-item">
                            <div className="tech-label">症状覆盖</div>
                            <div className="tech-value">9,629 种症状标签</div>
                        </div>
                        <div className="tech-item">
                            <div className="tech-label">中药覆盖</div>
                            <div className="tech-value">273 种常用中药</div>
                        </div>
                        <div className="tech-item">
                            <div className="tech-label">模型F1分数</div>
                            <div className="tech-value">0.386 (测试集)</div>
                        </div>
                        <div className="tech-item">
                            <div className="tech-label">并行融合</div>
                            <div className="tech-value">规则匹配 + 神经网络</div>
                        </div>
                    </div>
                </section>

                <section style={{ textAlign: 'center', padding: 'var(--space-2xl) 0' }}>
                    <h2 style={{ fontSize: '1.8rem', marginBottom: 'var(--space-lg)', letterSpacing: '3px' }}>📋 诊疗流程</h2>
                    <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', flexWrap: 'wrap', maxWidth: '900px', margin: '0 auto' }}>
                        {[
                            { icon: '👤', title: '患者登录', desc: '填写基本信息' },
                            { icon: '👁️', title: '望诊', desc: '面色舌象' },
                            { icon: '👂', title: '闻诊', desc: '声音气味' },
                            { icon: '💬', title: '问诊', desc: '症状病史' },
                            { icon: '✋', title: '切诊', desc: '脉象体征' },
                            { icon: '🤖', title: 'AI分析', desc: '双引擎推荐' },
                            { icon: '✅', title: '医生审核', desc: '确认处方' },
                        ].map((step, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <div className="card" style={{ padding: '16px 20px', textAlign: 'center', minWidth: '100px' }}>
                                    <div style={{ fontSize: '1.8rem', marginBottom: '4px' }}>{step.icon}</div>
                                    <div style={{ fontFamily: 'var(--font-serif)', fontWeight: 600, fontSize: '0.95rem' }}>{step.title}</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--ink-gray)' }}>{step.desc}</div>
                                </div>
                                {i < 6 && <span style={{ color: 'var(--ancient-gold)', fontSize: '1.2rem' }}>→</span>}
                            </div>
                        ))}
                    </div>
                </section>
            </main>

            <footer className="footer">
                <div className="footer-text">
                    <span>🏥</span>
                    <span>岐黄AI · 中医智能辅助诊疗系统</span>
                    <span>|</span>
                    <span>仅供辅助参考，不替代专业医疗诊断</span>
                </div>
            </footer>
        </>
    );
}
