'use client';

import Header from '@/components/shared/Header';
import Link from 'next/link';

export default function HomePage() {
  return (
    <>
      <Header />
      <main className="main-content">
        {/* 英雄区 */}
        <section className="hero">
          <div className="hero-icon">🏥</div>
          <h1 className="hero-title">岐黄AI · 智能辅助诊疗</h1>
          <p className="hero-desc">
            传承千年中医智慧，融合现代人工智能技术。<br />
            通过望闻问切四诊合参，AI辅助推荐经典方剂，<br />
            医生审核把关，确保安全有效。
          </p>
          <div className="hero-buttons">
            <Link href="/patient" className="btn btn-primary btn-lg">
              <span className="btn-icon">🩺</span> 开始问诊
            </Link>
            <Link href="/doctor" className="btn btn-secondary btn-lg">
              <span className="btn-icon">👨‍⚕️</span> 医生入口
            </Link>
          </div>
        </section>

        <div className="divider" />

        {/* 特色介绍 */}
        <section className="features-grid">
          <div className="card feature-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, rgba(196,30,58,0.15), rgba(196,30,58,0.05))' }}>👁️</div>
            <h3>望闻问切</h3>
            <p>遵循传统中医四诊合参，全面采集面色舌象、声音嗅味、主诉症状、脉象体征，支持拍照辅助识别。</p>
          </div>
          <div className="card feature-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, rgba(91,140,90,0.15), rgba(91,140,90,0.05))' }}>🤖</div>
            <h3>AI智能推荐</h3>
            <p>基于海量经典方剂数据库深度学习，智能匹配证候，推荐最佳方剂，标注学习来源与修改说明。</p>
          </div>
          <div className="card feature-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, rgba(201,169,110,0.2), rgba(201,169,110,0.05))' }}>🛡️</div>
            <h3>医生审核</h3>
            <p>AI推荐的方剂交由执业中医师审核，可调整药材剂量、添加批注，确保处方的安全性与有效性。</p>
          </div>
          <div className="card feature-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, rgba(44,44,44,0.1), rgba(44,44,44,0.03))' }}>📚</div>
            <h3>经典传承</h3>
            <p>收录《伤寒论》《金匮要略》《温病条辨》等经典名著方剂，追溯每一个推荐的学术依据。</p>
          </div>
        </section>

        {/* 流程说明 */}
        <div className="divider" />
        <section style={{ textAlign: 'center', padding: 'var(--space-2xl) 0' }}>
          <h2 style={{ fontSize: '1.8rem', marginBottom: 'var(--space-lg)', letterSpacing: '3px' }}>📋 诊疗流程</h2>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', flexWrap: 'wrap', maxWidth: '900px', margin: '0 auto' }}>
            {[
              { icon: '👁️', title: '望诊', desc: '观察面色舌象' },
              { icon: '👂', title: '闻诊', desc: '听声音辨气味' },
              { icon: '💬', title: '问诊', desc: '详询症状病史' },
              { icon: '✋', title: '切诊', desc: '诊脉辨虚实' },
              { icon: '🤖', title: 'AI分析', desc: '智能推荐方剂' },
              { icon: '✅', title: '医生审核', desc: '确保安全有效' },
            ].map((step, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div className="card" style={{ padding: '16px 20px', textAlign: 'center', minWidth: '100px' }}>
                  <div style={{ fontSize: '1.8rem', marginBottom: '4px' }}>{step.icon}</div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontWeight: 600, fontSize: '0.95rem' }}>{step.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--ink-gray)' }}>{step.desc}</div>
                </div>
                {i < 5 && <span style={{ color: 'var(--ancient-gold)', fontSize: '1.2rem' }}>→</span>}
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
