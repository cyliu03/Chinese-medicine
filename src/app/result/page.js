'use client';

import { useRouter } from 'next/navigation';
import Header from '@/components/shared/Header';
import { useDiagnosis } from '@/context/DiagnosisContext';
import Link from 'next/link';

export default function ResultPage() {
    const router = useRouter();
    const { aiResults, patientSubmissions } = useDiagnosis();

    if (!aiResults || !aiResults.recommendations || aiResults.recommendations.length === 0) {
        return (
            <>
                <Header />
                <main className="main-content">
                    <div className="empty-state">
                        <div className="empty-state-icon">🔍</div>
                        <h2>暂无分析结果</h2>
                        <p>请先完成四诊问诊流程</p>
                        <Link href="/patient" className="btn btn-primary" style={{ marginTop: '16px' }}>
                            去问诊
                        </Link>
                    </div>
                </main>
            </>
        );
    }

    const { tags, recommendations } = aiResults;

    return (
        <>
            <Header />
            <main className="main-content">
                <div className="page-enter">
                    <div style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>
                        <h1 style={{ fontSize: '1.8rem', letterSpacing: '3px', marginBottom: '8px' }}>🤖 AI分析结果</h1>
                        <p style={{ color: 'var(--ink-gray)' }}>基于您的四诊信息，AI从经典方剂库中匹配推荐</p>
                    </div>

                    {/* 证候标签 */}
                    <div className="card" style={{ marginBottom: 'var(--space-lg)' }}>
                        <div className="card-header">
                            <div className="card-icon">🏷️</div>
                            <div>
                                <div className="card-title">证候分析</div>
                                <div className="card-subtitle">从四诊信息中提取的证候标签</div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {tags.map((tag, i) => (
                                <span key={i} className="diagnosis-tag">{tag}</span>
                            ))}
                        </div>
                    </div>

                    {/* 推荐方剂 */}
                    {recommendations.map((rec) => (
                        <div key={rec.id} className="card recommendation-card">
                            <div className="recommendation-rank">
                                <div className={`rank-badge rank-${rec.rank}`}>{rec.rank}</div>
                                <div style={{ flex: 1 }}>
                                    <div className="formula-name">{rec.name}</div>
                                    <div className="formula-source">📚 {rec.source}  · {rec.author}</div>
                                </div>
                                <div className={`match-score ${rec.matchScore >= 60 ? 'high' : 'medium'}`}>
                                    匹配度 {rec.matchScore}%
                                </div>
                            </div>

                            {/* 组成 */}
                            <div className="form-section">
                                <div className="form-section-title">💊 方剂组成</div>
                                <div className="herb-list">
                                    {rec.composition.map((c, i) => (
                                        <span key={i} className="herb-tag">
                                            {c.herb} <span className="herb-amount">{c.amount}</span>
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* 主治 */}
                            <div className="form-section">
                                <div className="form-section-title">🎯 主治</div>
                                <p style={{ fontSize: '0.9rem', color: 'var(--ink-gray)', lineHeight: 1.8 }}>
                                    {rec.indications.join('，')}
                                </p>
                            </div>

                            {/* 匹配标签 */}
                            <div className="form-section">
                                <div className="form-section-title">🔗 匹配的症状标签</div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                    {rec.matchedTags.map((t, i) => (
                                        <span key={i} className="diagnosis-tag" style={{ background: 'rgba(91,140,90,0.1)', color: 'var(--qing-green)' }}>{t}</span>
                                    ))}
                                </div>
                            </div>

                            {/* 来源标注 */}
                            <div className="source-note">
                                <strong>📖 学习来源：</strong>本方来自 <strong>{rec.author}</strong> 所著 <strong>{rec.source.replace(rec.author, '').replace('《', '《').replace('》', '》')}</strong>，
                                原方主治「{rec.syndrome}」，与患者证候匹配度为 {rec.matchScore}%。
                            </div>

                            {/* AI修改建议 */}
                            {rec.suggestedModifications && rec.suggestedModifications.length > 0 && (
                                <div className="modification-note">
                                    <strong>🔧 AI加减建议：</strong>
                                    <ul style={{ margin: '8px 0 0 16px', fontSize: '0.85rem' }}>
                                        {rec.suggestedModifications.map((mod, i) => (
                                            <li key={i} style={{ marginBottom: '4px' }}>
                                                {mod.type === 'add' ? '➕ 加' : '➖ 减'} <strong>{mod.herb} {mod.amount}</strong> — {mod.reason}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* 原方加减说明 */}
                            {rec.modifications && (
                                <div style={{ marginTop: 'var(--space-sm)', padding: '8px 12px', background: 'rgba(201,169,110,0.08)', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: 'var(--ink-gray)' }}>
                                    <strong>📝 原方加减法：</strong>{rec.modifications}
                                </div>
                            )}
                        </div>
                    ))}

                    {/* 提交医生审核 */}
                    <div style={{ textAlign: 'center', marginTop: 'var(--space-xl)' }}>
                        <button
                            className="btn btn-secondary btn-lg"
                            onClick={() => router.push('/doctor')}
                        >
                            <span className="btn-icon">👨‍⚕️</span> 提交至医生审核
                        </button>
                        <p style={{ color: 'var(--ink-gray)', fontSize: '0.8rem', marginTop: 'var(--space-sm)' }}>
                            AI推荐仅供参考，需经执业中医师审核后方可使用
                        </p>
                    </div>
                </div>
            </main>
        </>
    );
}
