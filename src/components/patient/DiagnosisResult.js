'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useApp } from '@/context/AppContext';
import { getHybridRecommendations, analyzeSyndrome } from '@/lib/aiEngine';

export default function DiagnosisResult() {
    const router = useRouter();
    const { currentPatient, setAiResults, submitDiagnosis, resetPatient } = useApp();
    const [isLoading, setIsLoading] = useState(true);
    const [results, setResults] = useState(null);
    const [syndromeAnalysis, setSyndromeAnalysis] = useState(null);
    const [submitted, setSubmitted] = useState(false);

    useEffect(() => {
        const analyze = async () => {
            setIsLoading(true);
            try {
                const [hybridResults, syndrome] = await Promise.all([
                    getHybridRecommendations(currentPatient.diagnosis),
                    Promise.resolve(analyzeSyndrome(currentPatient.diagnosis))
                ]);
                setResults(hybridResults);
                setSyndromeAnalysis(syndrome);
                setAiResults(hybridResults);
            } catch (error) {
                console.error('Analysis error:', error);
            } finally {
                setIsLoading(false);
            }
        };
        analyze();
    }, [currentPatient.diagnosis, setAiResults]);

    const handleSubmit = () => {
        submitDiagnosis();
        setSubmitted(true);
    };

    const handleNewDiagnosis = () => {
        resetPatient();
        router.push('/patient');
    };

    if (isLoading) {
        return (
            <div className="card" style={{ textAlign: 'center', padding: 'var(--space-3xl)' }}>
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p style={{ marginTop: 'var(--space-lg)', color: 'var(--ink-gray)' }}>
                        AI正在分析您的症状...
                    </p>
                    <p style={{ fontSize: '0.85rem', color: 'var(--light-ink)', marginTop: 'var(--space-sm)' }}>
                        推荐系统 + 深度学习模型并行处理中
                    </p>
                </div>
            </div>
        );
    }

    if (submitted) {
        return (
            <div className="card" style={{ textAlign: 'center', padding: 'var(--space-3xl)' }}>
                <div style={{ fontSize: '4rem', marginBottom: 'var(--space-lg)' }}>✅</div>
                <h2 style={{ fontSize: '1.5rem', marginBottom: 'var(--space-md)' }}>诊断已提交</h2>
                <p style={{ color: 'var(--ink-gray)', marginBottom: 'var(--space-xl)' }}>
                    您的诊断信息已发送给医生审核，请耐心等待医生确认处方。
                </p>
                <div style={{ display: 'flex', gap: 'var(--space-md)', justifyContent: 'center' }}>
                    <button className="btn btn-primary" onClick={handleNewDiagnosis}>
                        开始新问诊
                    </button>
                    <button className="btn btn-ghost" onClick={() => router.push('/')}>
                        返回首页
                    </button>
                </div>
            </div>
        );
    }

    const topRecommendation = results?.recommendations?.[0];

    return (
        <div className="page-enter">
            <div style={{ textAlign: 'center', marginBottom: 'var(--space-lg)' }}>
                <h2 style={{ fontSize: '1.5rem', marginBottom: 'var(--space-sm)' }}>📋 诊断结果</h2>
                <p style={{ color: 'var(--ink-gray)' }}>
                    AI已完成分析，请查看推荐处方
                </p>
            </div>

            {/* 症状标签 */}
            <div className="card" style={{ marginBottom: 'var(--space-lg)' }}>
                <div className="card-header">
                    <div className="card-icon">🏷️</div>
                    <div>
                        <div className="card-title">识别的症状</div>
                        <div className="card-subtitle">共 {results?.tags?.length || 0} 个症状标签</div>
                    </div>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-sm)' }}>
                    {results?.tags?.map((tag, i) => (
                        <span key={i} className="diagnosis-tag">{tag}</span>
                    ))}
                </div>
            </div>

            {/* 证候分析 */}
            {syndromeAnalysis?.primarySyndrome && (
                <div className="card" style={{ marginBottom: 'var(--space-lg)', borderLeft: '4px solid var(--ancient-gold)' }}>
                    <div className="card-header">
                        <div className="card-icon">🔍</div>
                        <div>
                            <div className="card-title">证候分析</div>
                            <div className="card-subtitle">AI初步判断的证候类型</div>
                        </div>
                    </div>
                    <div style={{ marginBottom: 'var(--space-md)' }}>
                        <div style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--zhu-red-dark)', marginBottom: 'var(--space-xs)' }}>
                            {syndromeAnalysis.primarySyndrome.name}
                        </div>
                        <div style={{ fontSize: '0.9rem', color: 'var(--ink-gray)', marginBottom: 'var(--space-sm)' }}>
                            {syndromeAnalysis.primarySyndrome.description}
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--qing-green)' }}>
                            治法：{syndromeAnalysis.primarySyndrome.treatment}
                        </div>
                        <div style={{ marginTop: 'var(--space-sm)' }}>
                            <span className="match-score medium">
                                置信度 {syndromeAnalysis.primarySyndrome.confidence}%
                            </span>
                        </div>
                    </div>
                    {syndromeAnalysis.possibleSyndromes.length > 1 && (
                        <div style={{ fontSize: '0.85rem', color: 'var(--ink-gray)' }}>
                            <strong>其他可能证候：</strong>
                            {syndromeAnalysis.possibleSyndromes.slice(1).map(s => s.name).join('、')}
                        </div>
                    )}
                </div>
            )}

            {/* AI推荐处方 */}
            {topRecommendation && (
                <div className="card recommendation-card" style={{ marginBottom: 'var(--space-lg)' }}>
                    <div className="card-header">
                        <div className="card-icon">🤖</div>
                        <div style={{ flex: 1 }}>
                            <div className="card-title">AI推荐处方</div>
                            <div className="card-subtitle">
                                {topRecommendation.source}
                                {results?.metadata?.modelAvailable && (
                                    <span style={{ marginLeft: 'var(--space-sm)', color: 'var(--qing-green)' }}>
                                        ✓ 深度学习模型可用
                                    </span>
                                )}
                            </div>
                        </div>
                        <div className={`match-score ${topRecommendation.matchScore >= 60 ? 'high' : 'medium'}`}>
                            匹配度 {topRecommendation.matchScore}%
                        </div>
                    </div>

                    <div style={{ marginBottom: 'var(--space-lg)' }}>
                        <div className="formula-name" style={{ fontSize: '1.5rem', marginBottom: 'var(--space-xs)' }}>
                            {topRecommendation.name}
                        </div>
                        {topRecommendation.author && (
                            <div className="formula-source">📚 {topRecommendation.author} · {topRecommendation.source}</div>
                        )}
                    </div>

                    <div className="form-section">
                        <div className="form-section-title">💊 方剂组成</div>
                        <div className="herb-list">
                            {topRecommendation.composition?.map((c, i) => (
                                <span key={i} className="herb-tag">
                                    {c.herb} <span className="herb-amount">{c.amount}</span>
                                    {c.probability && (
                                        <span style={{ fontSize: '0.7rem', color: 'var(--qing-green)', marginLeft: '4px' }}>
                                            {Math.round(c.probability * 100)}%
                                        </span>
                                    )}
                                </span>
                            ))}
                        </div>
                    </div>

                    {topRecommendation.suggestedModifications?.length > 0 && (
                        <div className="modification-note">
                            <strong>🔧 AI加减建议：</strong>
                            <ul style={{ margin: 'var(--space-sm) 0 0 16px', fontSize: '0.85rem' }}>
                                {topRecommendation.suggestedModifications.map((mod, i) => (
                                    <li key={i}>
                                        {mod.type === 'add' ? '➕ 加' : '➖ 减'} <strong>{mod.herb} {mod.amount}</strong> — {mod.reason}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* 其他推荐 */}
            {results?.recommendations?.length > 1 && (
                <div className="card" style={{ marginBottom: 'var(--space-lg)' }}>
                    <div className="card-header">
                        <div className="card-icon">📋</div>
                        <div>
                            <div className="card-title">其他推荐方剂</div>
                            <div className="card-subtitle">以下方剂也可作为参考</div>
                        </div>
                    </div>
                    {results.recommendations.slice(1).map((rec, i) => (
                        <div 
                            key={i} 
                            style={{ 
                                padding: 'var(--space-md)', 
                                background: 'rgba(245,240,232,0.5)', 
                                borderRadius: 'var(--radius-md)', 
                                marginBottom: 'var(--space-sm)',
                                fontSize: '0.9rem'
                            }}
                        >
                            <div style={{ fontWeight: 600, marginBottom: 'var(--space-xs)' }}>
                                {rec.rank}. {rec.name}
                            </div>
                            <div style={{ color: 'var(--ink-gray)', fontSize: '0.85rem' }}>
                                {rec.source} · 匹配度 {rec.matchScore}%
                            </div>
                            <div style={{ marginTop: 'var(--space-xs)', display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                {rec.composition?.slice(0, 5).map((c, j) => (
                                    <span key={j} style={{ 
                                        fontSize: '0.75rem', 
                                        padding: '2px 6px', 
                                        background: 'rgba(201,169,110,0.1)', 
                                        borderRadius: '4px' 
                                    }}>
                                        {c.herb}
                                    </span>
                                ))}
                                {rec.composition?.length > 5 && (
                                    <span style={{ fontSize: '0.75rem', color: 'var(--ink-gray)' }}>
                                        +{rec.composition.length - 5}味
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* 模型信息 */}
            {results?.metadata && (
                <div style={{ 
                    padding: 'var(--space-md)', 
                    background: 'rgba(91,140,90,0.05)', 
                    borderRadius: 'var(--radius-md)', 
                    marginBottom: 'var(--space-lg)',
                    fontSize: '0.85rem',
                    color: 'var(--ink-gray)'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-md)' }}>
                        <span>📊 规则匹配: {results.metadata.ruleBasedCount} 条</span>
                        <span>🧠 深度学习: {results.metadata.modelBasedCount} 条</span>
                        <span>⏱️ 处理时间: {results.metadata.processingTime}ms</span>
                    </div>
                </div>
            )}

            {/* 提示 */}
            <div style={{ 
                padding: 'var(--space-md)', 
                background: 'rgba(196,30,58,0.05)', 
                borderRadius: 'var(--radius-md)', 
                marginBottom: 'var(--space-lg)',
                fontSize: '0.85rem',
                color: 'var(--ink-gray)'
            }}>
                <p style={{ marginBottom: 'var(--space-sm)' }}>📌 <strong>温馨提示：</strong></p>
                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    <li>以上处方由AI推荐，仅供参考</li>
                    <li>需经医生审核确认后方可使用</li>
                    <li>如有疑问请咨询专业中医师</li>
                </ul>
            </div>

            {/* 操作按钮 */}
            <div className="bottom-nav">
                <button className="btn btn-ghost" onClick={() => router.push('/patient')}>
                    ← 返回修改
                </button>
                <button className="btn btn-primary" onClick={handleSubmit}>
                    提交诊断 →
                </button>
            </div>
        </div>
    );
}
