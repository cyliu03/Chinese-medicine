'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/shared/Header';
import { useApp } from '@/context/AppContext';
import Link from 'next/link';
import { 
    findSimilarFormulas, 
    getAllFormulas, 
    getFormulasByCategory, 
    saveCustomFormula, 
    deleteCustomFormula,
    parseFormulaFromText,
    getFormulaStats
} from '@/lib/formulaKnowledge';

export default function DoctorPage() {
    const { diagnoses, updateDiagnosisStatus, doctorInfo } = useApp();
    const [selectedId, setSelectedId] = useState(null);
    const [filter, setFilter] = useState('all');
    const [doctorNote, setDoctorNote] = useState('');
    const [editingHerbs, setEditingHerbs] = useState([]);
    const [activeTab, setActiveTab] = useState('diagnoses');
    const [formulaSearch, setFormulaSearch] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [similarFormulas, setSimilarFormulas] = useState([]);
    const [showAddFormula, setShowAddFormula] = useState(false);
    const [newFormulaText, setNewFormulaText] = useState('');
    const [formulaStats, setFormulaStats] = useState(null);

    const filteredDiagnoses = diagnoses.filter(d => {
        if (filter === 'all') return true;
        return d.status === filter;
    });

    const selected = diagnoses.find(d => d.id === selectedId);

    const allFormulas = getAllFormulas();
    const categories = getFormulasByCategory();

    useEffect(() => {
        if (selected) {
            setDoctorNote(selected.doctorNote || '');
            setEditingHerbs(selected?.aiResults?.recommendations?.[0]?.composition || []);
            
            const symptomTags = selected?.aiResults?.tags || [];
            const similar = findSimilarFormulas(symptomTags, 5);
            setSimilarFormulas(similar);
        }
    }, [selectedId, selected]);

    useEffect(() => {
        setFormulaStats(getFormulaStats());
    }, [activeTab]);

    const handleApprove = () => {
        if (!selected?.aiResults?.recommendations?.[0]) {
            updateDiagnosisStatus(selectedId, 'approved', doctorNote, null);
            setSelectedId(null);
            return;
        }
        updateDiagnosisStatus(selectedId, 'approved', doctorNote, {
            ...selected.aiResults,
            recommendations: [{
                ...selected.aiResults.recommendations[0],
                composition: editingHerbs
            }]
        });
        setSelectedId(null);
    };

    const handleReject = () => {
        updateDiagnosisStatus(selectedId, 'rejected', doctorNote);
        setSelectedId(null);
    };

    const handleModifyHerb = (index, field, value) => {
        setEditingHerbs(prev => prev.map((h, i) => 
            i === index ? { ...h, [field]: value } : h
        ));
    };

    const handleRemoveHerb = (index) => {
        setEditingHerbs(prev => prev.filter((_, i) => i !== index));
    };

    const handleAddHerb = () => {
        setEditingHerbs(prev => [...prev, { herb: '', amount: '9g' }]);
    };

    const handleAddFormula = () => {
        const formula = parseFormulaFromText(newFormulaText);
        if (formula.name) {
            saveCustomFormula(formula);
            setNewFormulaText('');
            setShowAddFormula(false);
            setFormulaStats(getFormulaStats());
        }
    };

    const handleUseFormula = (formula) => {
        setEditingHerbs(formula.composition.map(c => ({
            herb: c.herb,
            amount: c.amount
        })));
    };

    const stats = {
        total: diagnoses.length,
        pending: diagnoses.filter(d => d.status === 'pending').length,
        approved: diagnoses.filter(d => d.status === 'approved').length,
        rejected: diagnoses.filter(d => d.status === 'rejected').length,
    };

    const filteredFormulas = allFormulas.filter(f => {
        const matchSearch = !formulaSearch || 
            f.name.toLowerCase().includes(formulaSearch.toLowerCase()) ||
            f.author?.toLowerCase().includes(formulaSearch.toLowerCase()) ||
            f.syndrome?.toLowerCase().includes(formulaSearch.toLowerCase());
        const matchCategory = selectedCategory === 'all' || f.category === selectedCategory;
        return matchSearch && matchCategory;
    });

    return (
        <>
            <Header />
            <main className="main-content">
                <div className="page-enter">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
                        <div>
                            <h1 style={{ fontSize: '1.8rem', letterSpacing: '3px', marginBottom: '4px' }}>👨‍⚕️ 医生工作台</h1>
                            <p style={{ color: 'var(--ink-gray)', fontSize: '0.9rem' }}>
                                欢迎，{doctorInfo.name} · {doctorInfo.title}
                            </p>
                        </div>
                        <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                            <div className="stat-card">
                                <div className="stat-value">{stats.total}</div>
                                <div className="stat-label">诊断总数</div>
                            </div>
                            <div className="stat-card pending">
                                <div className="stat-value">{stats.pending}</div>
                                <div className="stat-label">待审核</div>
                            </div>
                            <div className="stat-card approved">
                                <div className="stat-value">{stats.approved}</div>
                                <div className="stat-label">已批准</div>
                            </div>
                        </div>
                    </div>

                    {/* 标签页切换 */}
                    <div style={{ display: 'flex', gap: 'var(--space-sm)', marginBottom: 'var(--space-lg)', borderBottom: '2px solid var(--bg-secondary)', paddingBottom: 'var(--space-sm)' }}>
                        <button
                            className={`btn ${activeTab === 'diagnoses' ? 'btn-primary' : 'btn-ghost'}`}
                            onClick={() => setActiveTab('diagnoses')}
                        >
                            📋 诊断审核 {stats.pending > 0 && `(${stats.pending})`}
                        </button>
                        <button
                            className={`btn ${activeTab === 'formulas' ? 'btn-primary' : 'btn-ghost'}`}
                            onClick={() => setActiveTab('formulas')}
                        >
                            📚 药方知识库
                        </button>
                    </div>

                    {/* 药方知识库 */}
                    {activeTab === 'formulas' && (
                        <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
                                <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                                    <input
                                        type="text"
                                        className="form-input"
                                        placeholder="搜索药方、医家、证候..."
                                        value={formulaSearch}
                                        onChange={(e) => setFormulaSearch(e.target.value)}
                                        style={{ width: '300px' }}
                                    />
                                    <select
                                        className="form-input"
                                        value={selectedCategory}
                                        onChange={(e) => setSelectedCategory(e.target.value)}
                                        style={{ width: '150px' }}
                                    >
                                        <option value="all">全部类别</option>
                                        {Object.keys(categories).map(cat => (
                                            <option key={cat} value={cat}>{cat}</option>
                                        ))}
                                    </select>
                                </div>
                                <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
                                    {formulaStats && (
                                        <span style={{ fontSize: '0.85rem', color: 'var(--ink-gray)' }}>
                                            共 {formulaStats.total} 个药方（经典 {formulaStats.famous} + 自定义 {formulaStats.custom}）
                                        </span>
                                    )}
                                    <button
                                        className="btn btn-primary btn-sm"
                                        onClick={() => setShowAddFormula(!showAddFormula)}
                                    >
                                        + 添加药方
                                    </button>
                                </div>
                            </div>

                            {/* 添加药方表单 */}
                            {showAddFormula && (
                                <div className="card" style={{ marginBottom: 'var(--space-lg)' }}>
                                    <div className="card-header">
                                        <div className="card-icon">📝</div>
                                        <div>
                                            <div className="card-title">添加自定义药方</div>
                                            <div className="card-subtitle">支持粘贴文本或手动输入</div>
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">药方内容（支持以下格式）</label>
                                        <textarea
                                            className="form-textarea"
                                            placeholder={`示例格式：
方名：归脾汤
组成：人参6g、黄芪12g、白术9g、茯苓9g、龙眼肉12g、酸枣仁12g、当归9g、远志6g、木香6g、甘草3g
主治：心悸怔忡、健忘失眠、盗汗虚热、体倦食少
证候：心脾气血两虚证
用法：水煎服，每日一剂`}
                                            value={newFormulaText}
                                            onChange={(e) => setNewFormulaText(e.target.value)}
                                            rows={8}
                                        />
                                    </div>
                                    <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
                                        <button className="btn btn-primary" onClick={handleAddFormula}>
                                            保存药方
                                        </button>
                                        <button className="btn btn-ghost" onClick={() => setShowAddFormula(false)}>
                                            取消
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* 药方列表 */}
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 'var(--space-md)' }}>
                                {filteredFormulas.map(formula => (
                                    <div key={formula.id} className="card" style={{ position: 'relative' }}>
                                        {formula.type === 'custom' && (
                                            <button
                                                style={{ position: 'absolute', top: '8px', right: '8px', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--zhu-red)', fontSize: '0.8rem' }}
                                                onClick={() => { deleteCustomFormula(formula.id); setFormulaStats(getFormulaStats()); }}
                                            >
                                                ✕
                                            </button>
                                        )}
                                        <div style={{ marginBottom: 'var(--space-sm)' }}>
                                            <span className="formula-name" style={{ fontSize: '1.2rem' }}>{formula.name}</span>
                                            {formula.type === 'custom' && (
                                                <span style={{ marginLeft: 'var(--space-sm)', fontSize: '0.75rem', padding: '2px 6px', background: 'var(--ancient-gold-light)', borderRadius: '4px' }}>
                                                    自定义
                                                </span>
                                            )}
                                        </div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--ink-gray)', marginBottom: 'var(--space-sm)' }}>
                                            {formula.author && <span>📚 {formula.author}</span>}
                                            {formula.source && <span> · {formula.source}</span>}
                                            {formula.dynasty && <span> ({formula.dynasty})</span>}
                                        </div>
                                        {formula.syndrome && (
                                            <div style={{ fontSize: '0.85rem', marginBottom: 'var(--space-sm)', color: 'var(--zhu-red-dark)' }}>
                                                <strong>证候：</strong>{formula.syndrome}
                                            </div>
                                        )}
                                        <div style={{ marginBottom: 'var(--space-sm)' }}>
                                            <strong style={{ fontSize: '0.85rem' }}>组成：</strong>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: 'var(--space-xs)' }}>
                                                {formula.composition?.slice(0, 6).map((c, i) => (
                                                    <span key={i} style={{ fontSize: '0.75rem', padding: '2px 6px', background: 'var(--ancient-gold-light)', borderRadius: '4px' }}>
                                                        {c.herb} {c.amount}
                                                    </span>
                                                ))}
                                                {formula.composition?.length > 6 && (
                                                    <span style={{ fontSize: '0.75rem', color: 'var(--ink-gray)' }}>
                                                        +{formula.composition.length - 6}味
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        {formula.indications && formula.indications.length > 0 && (
                                            <div style={{ fontSize: '0.8rem', color: 'var(--ink-gray)' }}>
                                                <strong>主治：</strong>{formula.indications.slice(0, 4).join('、')}
                                                {formula.indications.length > 4 && '...'}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* 诊断审核 */}
                    {activeTab === 'diagnoses' && !selected && (
                        <>
                            <div style={{ marginBottom: 'var(--space-lg)', display: 'flex', gap: 'var(--space-sm)' }}>
                                {[
                                    { key: 'all', label: '全部', count: stats.total },
                                    { key: 'pending', label: '待审核', count: stats.pending },
                                    { key: 'approved', label: '已批准', count: stats.approved },
                                    { key: 'rejected', label: '已驳回', count: stats.rejected },
                                ].map(f => (
                                    <button
                                        key={f.key}
                                        className={`btn ${filter === f.key ? 'btn-primary' : 'btn-ghost'}`}
                                        onClick={() => setFilter(f.key)}
                                    >
                                        {f.label} ({f.count})
                                    </button>
                                ))}
                            </div>

                            {diagnoses.length === 0 ? (
                                <div className="empty-state">
                                    <div className="empty-state-icon">📋</div>
                                    <h2>暂无待审处方</h2>
                                    <p style={{ marginBottom: '16px' }}>目前没有患者提交的处方需要审核</p>
                                    <Link href="/patient" className="btn btn-primary">模拟患者问诊</Link>
                                </div>
                            ) : (
                                <div className="card">
                                    <div className="card-header">
                                        <div className="card-icon">📋</div>
                                        <div>
                                            <div className="card-title">诊断列表</div>
                                            <div className="card-subtitle">共 {filteredDiagnoses.length} 条记录</div>
                                        </div>
                                    </div>

                                    {filteredDiagnoses.map((diag) => (
                                        <div
                                            key={diag.id}
                                            className="patient-queue-item"
                                            onClick={() => setSelectedId(diag.id)}
                                            style={{ marginBottom: '8px', cursor: 'pointer' }}
                                        >
                                            <div className="patient-avatar">
                                                {diag.patientName?.slice(-1) || '?'}
                                            </div>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontWeight: 600 }}>{diag.patientName}</div>
                                                <div style={{ fontSize: '0.8rem', color: 'var(--ink-gray)' }}>
                                                    {diag.patientInfo?.age}岁 · {diag.patientInfo?.gender}
                                                    {' · '}{new Date(diag.createdAt).toLocaleString('zh-CN')}
                                                </div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--light-ink)', marginTop: '2px' }}>
                                                    {diag.aiResults?.recommendations?.[0]?.name || 'AI分析中...'}
                                                </div>
                                            </div>
                                            <span className={`status-badge ${diag.status}`}>
                                                {diag.status === 'pending' ? '待审核' : diag.status === 'approved' ? '已批准' : '已驳回'}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    )}

                    {/* 审核详情 */}
                    {activeTab === 'diagnoses' && selected && (
                        <div>
                            <button className="btn btn-ghost" onClick={() => setSelectedId(null)} style={{ marginBottom: 'var(--space-lg)' }}>
                                ← 返回列表
                            </button>

                            <div className="review-layout">
                                {/* 左侧 — 患者信息 */}
                                <div className="card review-panel">
                                    <div className="card-header">
                                        <div className="card-icon">🩺</div>
                                        <div>
                                            <div className="card-title">{selected.patientName} 四诊信息</div>
                                            <div className="card-subtitle">
                                                {selected.patientInfo?.age}岁 · {selected.patientInfo?.gender} · 
                                                {new Date(selected.createdAt).toLocaleString('zh-CN')}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="diagnosis-category" style={{ marginBottom: '12px' }}>
                                        <h4>👁️ 望诊</h4>
                                        {selected.diagnosis.wangZhen.faceColor && <div className="diagnosis-item">面色：{selected.diagnosis.wangZhen.faceColor}</div>}
                                        {selected.diagnosis.wangZhen.tongueColor && <div className="diagnosis-item">舌色：{selected.diagnosis.wangZhen.tongueColor}</div>}
                                        {selected.diagnosis.wangZhen.tongueCoating && <div className="diagnosis-item">舌苔：{selected.diagnosis.wangZhen.tongueCoating}</div>}
                                        {selected.diagnosis.wangZhen.tongueShape && <div className="diagnosis-item">舌形：{selected.diagnosis.wangZhen.tongueShape}</div>}
                                        {selected.diagnosis.wangZhen.bodyType && <div className="diagnosis-item">体态：{selected.diagnosis.wangZhen.bodyType}</div>}
                                        {selected.diagnosis.wangZhen.spirit && <div className="diagnosis-item">精神：{selected.diagnosis.wangZhen.spirit}</div>}
                                    </div>

                                    <div className="diagnosis-category" style={{ marginBottom: '12px' }}>
                                        <h4>👂 闻诊</h4>
                                        {selected.diagnosis.wenZhen.voiceType && <div className="diagnosis-item">声音：{selected.diagnosis.wenZhen.voiceType}</div>}
                                        {selected.diagnosis.wenZhen.breathType && <div className="diagnosis-item">呼吸：{selected.diagnosis.wenZhen.breathType}</div>}
                                        {selected.diagnosis.wenZhen.coughType && <div className="diagnosis-item">咳嗽：{selected.diagnosis.wenZhen.coughType}</div>}
                                    </div>

                                    <div className="diagnosis-category" style={{ marginBottom: '12px' }}>
                                        <h4>💬 问诊</h4>
                                        {selected.diagnosis.wenZhenAsk.mainComplaint && <div className="diagnosis-item">主诉：{selected.diagnosis.wenZhenAsk.mainComplaint}</div>}
                                        {selected.diagnosis.wenZhenAsk.symptoms?.length > 0 && (
                                            <div className="diagnosis-item" style={{ flexWrap: 'wrap' }}>
                                                症状：{selected.diagnosis.wenZhenAsk.symptoms.map((s, i) => <span key={i} className="diagnosis-tag">{s}</span>)}
                                            </div>
                                        )}
                                        {selected.diagnosis.wenZhenAsk.duration && <div className="diagnosis-item">病程：{selected.diagnosis.wenZhenAsk.duration}</div>}
                                        {selected.diagnosis.wenZhenAsk.sweating && <div className="diagnosis-item">汗出：{selected.diagnosis.wenZhenAsk.sweating}</div>}
                                        {selected.diagnosis.wenZhenAsk.thirst && <div className="diagnosis-item">口渴：{selected.diagnosis.wenZhenAsk.thirst}</div>}
                                        {selected.diagnosis.wenZhenAsk.sleepQuality && <div className="diagnosis-item">睡眠：{selected.diagnosis.wenZhenAsk.sleepQuality}</div>}
                                    </div>

                                    <div className="diagnosis-category">
                                        <h4>✋ 切诊</h4>
                                        {selected.diagnosis.qieZhen.pulseType?.length > 0 && (
                                            <div className="diagnosis-item" style={{ flexWrap: 'wrap' }}>
                                                脉象：{selected.diagnosis.qieZhen.pulseType.map((p, i) => <span key={i} className="diagnosis-tag">{p}</span>)}
                                            </div>
                                        )}
                                        {selected.diagnosis.qieZhen.pulseStrength && <div className="diagnosis-item">脉力：{selected.diagnosis.qieZhen.pulseStrength}</div>}
                                    </div>

                                    {selected.aiResults?.tags?.length > 0 && (
                                        <div style={{ marginTop: 'var(--space-lg)', padding: 'var(--space-md)', background: 'rgba(201,169,110,0.1)', borderRadius: 'var(--radius-md)' }}>
                                            <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: 'var(--space-sm)' }}>🏷️ AI识别症状</div>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                                {selected.aiResults.tags.map((tag, i) => (
                                                    <span key={i} className="diagnosis-tag" style={{ fontSize: '0.75rem' }}>{tag}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* 右侧 — AI推荐 + 医生编辑 */}
                                <div className="card review-panel">
                                    <div className="card-header">
                                        <div className="card-icon">🤖</div>
                                        <div>
                                            <div className="card-title">AI推荐处方</div>
                                            <div className="card-subtitle">请审核并调整以下处方</div>
                                        </div>
                                    </div>

                                    {selected.aiResults?.recommendations?.[0] ? (
                                        <>
                                            <div style={{ marginBottom: 'var(--space-lg)' }}>
                                                <div className="formula-name" style={{ fontSize: '1.5rem', marginBottom: '4px' }}>
                                                    {selected.aiResults.recommendations[0].name}
                                                </div>
                                                <div className="formula-source">
                                                    📚 {selected.aiResults.recommendations[0].source}
                                                </div>
                                                <div className={`match-score ${selected.aiResults.recommendations[0].matchScore >= 60 ? 'high' : 'medium'}`} style={{ marginTop: '8px' }}>
                                                    匹配度 {selected.aiResults.recommendations[0].matchScore}%
                                                </div>
                                            </div>

                                            <div className="form-section">
                                                <div className="form-section-title">💊 方剂组成 (可编辑)</div>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                                                    {editingHerbs.map((herb, i) => (
                                                        <div key={i} style={{ display: 'flex', gap: 'var(--space-sm)', alignItems: 'center' }}>
                                                            <input
                                                                type="text"
                                                                className="form-input"
                                                                value={herb.herb}
                                                                onChange={(e) => handleModifyHerb(i, 'herb', e.target.value)}
                                                                placeholder="药名"
                                                                style={{ flex: 1 }}
                                                            />
                                                            <input
                                                                type="text"
                                                                className="form-input"
                                                                value={herb.amount}
                                                                onChange={(e) => handleModifyHerb(i, 'amount', e.target.value)}
                                                                placeholder="剂量"
                                                                style={{ width: '80px' }}
                                                            />
                                                            <button
                                                                className="btn btn-ghost btn-sm"
                                                                onClick={() => handleRemoveHerb(i)}
                                                                style={{ color: 'var(--zhu-red)' }}
                                                            >
                                                                ✕
                                                            </button>
                                                        </div>
                                                    ))}
                                                    <button
                                                        className="btn btn-outline btn-sm"
                                                        onClick={handleAddHerb}
                                                        style={{ marginTop: 'var(--space-sm)' }}
                                                    >
                                                        + 添加药材
                                                    </button>
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="empty-state"><p>无AI推荐结果</p></div>
                                    )}

                                    {/* 相似病情名医药方 */}
                                    {similarFormulas.length > 0 && (
                                        <div style={{ marginTop: 'var(--space-xl)' }}>
                                            <div className="form-section-title">📚 相似病情名医药方</div>
                                            <p style={{ fontSize: '0.8rem', color: 'var(--ink-gray)', marginBottom: 'var(--space-sm)' }}>
                                                根据患者症状，推荐以下经典方剂供参考
                                            </p>
                                            {similarFormulas.map((formula, i) => (
                                                <div 
                                                    key={formula.id} 
                                                    style={{ 
                                                        padding: 'var(--space-md)', 
                                                        background: 'rgba(91,140,90,0.05)', 
                                                        borderRadius: 'var(--radius-md)', 
                                                        marginBottom: 'var(--space-sm)',
                                                        border: '1px solid rgba(91,140,90,0.2)'
                                                    }}
                                                >
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
                                                        <div>
                                                            <span className="formula-name">{formula.name}</span>
                                                            <span style={{ marginLeft: 'var(--space-sm)', fontSize: '0.8rem', color: 'var(--ink-gray)' }}>
                                                                {formula.author} · {formula.source}
                                                            </span>
                                                        </div>
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                                                            <span className="match-score medium">{formula.matchScore}%相似</span>
                                                            <button 
                                                                className="btn btn-sm btn-outline"
                                                                onClick={() => handleUseFormula(formula)}
                                                            >
                                                                采用
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <div style={{ fontSize: '0.85rem', color: 'var(--zhu-red-dark)', marginBottom: 'var(--space-xs)' }}>
                                                        <strong>证候：</strong>{formula.syndrome}
                                                    </div>
                                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: 'var(--space-xs)' }}>
                                                        {formula.composition?.map((c, j) => (
                                                            <span key={j} style={{ fontSize: '0.75rem', padding: '2px 6px', background: 'var(--ancient-gold-light)', borderRadius: '4px' }}>
                                                                {c.herb} {c.amount}
                                                            </span>
                                                        ))}
                                                    </div>
                                                    <div style={{ fontSize: '0.75rem', color: 'var(--qing-green)' }}>
                                                        匹配症状：{formula.matchedTags.join('、')}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* 医生批注 */}
                                    <div className="form-group" style={{ marginTop: 'var(--space-xl)' }}>
                                        <label className="form-label">📝 医生批注</label>
                                        <textarea
                                            className="form-textarea"
                                            placeholder="请输入审核意见、修改建议或医嘱..."
                                            value={doctorNote}
                                            onChange={(e) => setDoctorNote(e.target.value)}
                                            rows={4}
                                        />
                                    </div>

                                    {/* 操作按钮 */}
                                    <div className="review-actions">
                                        <button className="btn btn-approve" onClick={handleApprove}>
                                            ✅ 批准处方
                                        </button>
                                        <button className="btn btn-modify" onClick={handleApprove}>
                                            ✏️ 修改后批准
                                        </button>
                                        <button className="btn btn-reject" onClick={handleReject}>
                                            ❌ 驳回
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </>
    );
}
