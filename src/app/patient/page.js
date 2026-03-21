'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/shared/Header';
import StepIndicator from '@/components/shared/StepIndicator';
import PatientInfo from '@/components/patient/PatientInfo';
import WangZhen from '@/components/patient/WangZhen';
import WenZhen from '@/components/patient/WenZhen';
import WenZhenAsk from '@/components/patient/WenZhenAsk';
import QieZhen from '@/components/patient/QieZhen';
import DiagnosisResult from '@/components/patient/DiagnosisResult';
import { useApp } from '@/context/AppContext';

const steps = [
    { icon: '👤', label: '基本信息' },
    { icon: '👁️', label: '望诊' },
    { icon: '👂', label: '闻诊' },
    { icon: '💬', label: '问诊' },
    { icon: '✋', label: '切诊' },
    { icon: '📋', label: '诊断结果' },
];

export default function PatientPage() {
    const router = useRouter();
    const { currentStep, setCurrentStep, currentPatient, loginAsPatient, resetPatient } = useApp();
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (!currentPatient.id && currentStep === 0) {
        }
    }, []);

    const renderStep = () => {
        switch (currentStep) {
            case 0: return <PatientInfo />;
            case 1: return <WangZhen />;
            case 2: return <WenZhen />;
            case 3: return <WenZhenAsk />;
            case 4: return <QieZhen />;
            case 5: return <DiagnosisResult />;
            default: return <PatientInfo />;
        }
    };

    const handleNext = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handlePrev = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const handleReset = () => {
        resetPatient();
        router.push('/');
    };

    return (
        <>
            <Header />
            <main className="main-content">
                <div className="page-enter">
                    <div style={{ textAlign: 'center', marginBottom: 'var(--space-lg)' }}>
                        <h1 style={{ fontSize: '1.8rem', letterSpacing: '3px', marginBottom: '4px' }}>
                            🩺 智能问诊
                        </h1>
                        <p style={{ color: 'var(--ink-gray)', fontSize: '0.9rem' }}>
                            请按步骤完成四诊信息采集，AI将为您智能推荐方剂
                        </p>
                    </div>

                    <StepIndicator
                        steps={steps}
                        currentStep={currentStep}
                        onStepClick={(i) => { if (i <= currentStep) setCurrentStep(i); }}
                    />

                    <div style={{ marginTop: 'var(--space-lg)' }}>
                        {renderStep()}
                    </div>

                    {currentStep < 5 && (
                        <div className="bottom-nav">
                            <button
                                className="btn btn-ghost"
                                disabled={currentStep === 0}
                                onClick={handlePrev}
                            >
                                ← 上一步
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={handleNext}
                            >
                                {currentStep === 4 ? '获取诊断 →' : '下一步 →'}
                            </button>
                        </div>
                    )}

                    {currentStep === 5 && (
                        <div className="bottom-nav">
                            <button className="btn btn-ghost" onClick={handleReset}>
                                返回首页
                            </button>
                            <button 
                                className="btn btn-primary"
                                onClick={() => {
                                    resetPatient();
                                    setCurrentStep(0);
                                }}
                            >
                                新的问诊
                            </button>
                        </div>
                    )}
                </div>
            </main>
        </>
    );
}
