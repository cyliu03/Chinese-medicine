'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useDiagnosis } from '@/context/DiagnosisContext';
import { getAIModelRecommendation } from '@/lib/aiEngine';

export default function DiagnosisSummary() {
    const router = useRouter();
    const { diagnosis, submitDiagnosis, setAiResults, setPatientSubmissions } = useDiagnosis();
    const { wangZhen, wenZhen, wenZhenAsk, qieZhen } = diagnosis;

    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async () => {
        setIsLoading(true);
        try {
            // 运行AI推荐 (改为调用深度学习模型)
            const results = await getAIModelRecommendation(diagnosis);
            setAiResults(results);

            // 创建提交记录
            const submission = {
                id: Date.now().toString(),
                patientName: '患者' + Math.floor(Math.random() * 1000),
                timestamp: new Date().toISOString(),
                diagnosis: JSON.parse(JSON.stringify(diagnosis)),
                aiResults: results,
                status: 'pending',
            };
            setPatientSubmissions(prev => [...prev, submission]);

            router.push('/result');
        } catch (error) {
            alert('AI分析请求失败，请检查网络连接或后端服务。');
        } finally {
            setIsLoading(false);
        }
    };

    const SummaryItem = ({ label, value }) => {
        if (!value || (Array.isArray(value) && value.length === 0)) return null;
        return (
            <div className="diagnosis-item">
                <span style={{ fontWeight: 500, minWidth: '70px' }}>{label}：</span>
                <span>
                    {Array.isArray(value) ? (
                        value.map((v, i) => <span key={i} className="diagnosis-tag">{v}</span>)
                    ) : value}
                </span>
            </div>
        );
    };

    return (
        <div className="page-enter">
            <div className="card" style={{ marginBottom: 'var(--space-lg)' }}>
                <div className="card-header">
                    <div className="card-icon">📋</div>
                    <div>
                        <div className="card-title">四诊信息汇总</div>
                        <div className="card-subtitle">请确认以下信息无误后提交AI分析</div>
                    </div>
                </div>

                <div className="diagnosis-summary">
                    {/* 望诊汇总 */}
                    <div className="diagnosis-category">
                        <h4>👁️ 望诊</h4>
                        <SummaryItem label="面色" value={wangZhen.faceColor} />
                        <SummaryItem label="舌色" value={wangZhen.tongueColor} />
                        <SummaryItem label="舌苔" value={wangZhen.tongueCoating} />
                        <SummaryItem label="舌形" value={wangZhen.tongueShape} />
                        <SummaryItem label="体态" value={wangZhen.bodyType} />
                        <SummaryItem label="精神" value={wangZhen.spirit} />
                        {wangZhen.facePhoto && <div className="diagnosis-item"><span className="diagnosis-tag">📷 已上传面部照片</span></div>}
                        {wangZhen.tonguePhoto && <div className="diagnosis-item"><span className="diagnosis-tag">📷 已上传舌象照片</span></div>}
                    </div>

                    {/* 闻诊汇总 */}
                    <div className="diagnosis-category">
                        <h4>👂 闻诊</h4>
                        <SummaryItem label="声音" value={wenZhen.voiceType} />
                        <SummaryItem label="呼吸" value={wenZhen.breathType} />
                        <SummaryItem label="咳嗽" value={wenZhen.coughType} />
                        <SummaryItem label="气味" value={wenZhen.bodySmell} />
                    </div>

                    {/* 问诊汇总 */}
                    <div className="diagnosis-category" style={{ gridColumn: 'span 2' }}>
                        <h4>💬 问诊</h4>
                        <SummaryItem label="主诉" value={wenZhenAsk.mainComplaint} />
                        <SummaryItem label="伴随症状" value={wenZhenAsk.symptoms} />
                        <SummaryItem label="病程" value={wenZhenAsk.duration} />
                        <SummaryItem label="饮食" value={wenZhenAsk.dietPreference} />
                        <SummaryItem label="汗出" value={wenZhenAsk.sweating} />
                        <SummaryItem label="口渴" value={wenZhenAsk.thirst} />
                        <SummaryItem label="睡眠" value={wenZhenAsk.sleepQuality} />
                        <SummaryItem label="情绪" value={wenZhenAsk.emotionState} />
                        {wenZhenAsk.medicalHistory && <SummaryItem label="既往史" value={wenZhenAsk.medicalHistory} />}
                    </div>

                    {/* 切诊汇总 */}
                    <div className="diagnosis-category" style={{ gridColumn: 'span 2' }}>
                        <h4>✋ 切诊</h4>
                        <SummaryItem label="脉象" value={qieZhen.pulseType} />
                        <SummaryItem label="脉力" value={qieZhen.pulseStrength} />
                    </div>
                </div>
            </div>

            <div style={{ textAlign: 'center' }}>
                <button 
                    className={`btn btn-primary btn-lg ${isLoading ? 'loading' : 'pulse-animation'}`} 
                    onClick={handleSubmit}
                    disabled={isLoading}
                >
                    <span className="btn-icon">{isLoading ? '⌛' : '🤖'}</span> 
                    {isLoading ? '正在AI分析...' : '提交AI智能分析'}
                </button>
                <p style={{ color: 'var(--ink-gray)', fontSize: '0.8rem', marginTop: 'var(--space-sm)' }}>
                    AI将基于您的四诊信息，从经典方剂中智能匹配推荐
                </p>
            </div>
        </div>
    );
}
