'use client';

import { useState } from 'react';
import Header from '@/components/shared/Header';
import StepIndicator from '@/components/shared/StepIndicator';
import WangZhen from '@/components/patient/WangZhen';
import WenZhen from '@/components/patient/WenZhen';
import WenZhenAsk from '@/components/patient/WenZhenAsk';
import QieZhen from '@/components/patient/QieZhen';
import DiagnosisSummary from '@/components/patient/DiagnosisSummary';
import { useDiagnosis } from '@/context/DiagnosisContext';

const steps = [
    { icon: '👁️', label: '望诊' },
    { icon: '👂', label: '闻诊' },
    { icon: '💬', label: '问诊' },
    { icon: '✋', label: '切诊' },
    { icon: '📋', label: '汇总' },
];

export default function PatientPage() {
    const { currentStep, setCurrentStep } = useDiagnosis();

    const renderStep = () => {
        switch (currentStep) {
            case 0: return <WangZhen />;
            case 1: return <WenZhen />;
            case 2: return <WenZhenAsk />;
            case 3: return <QieZhen />;
            case 4: return <DiagnosisSummary />;
            default: return <WangZhen />;
        }
    };

    return (
        <>
            <Header />
            <main className="main-content">
                <div className="page-enter">
                    <div style={{ textAlign: 'center', marginBottom: 'var(--space-lg)' }}>
                        <h1 style={{ fontSize: '1.8rem', letterSpacing: '3px', marginBottom: '4px' }}>
                            🩺 四诊合参
                        </h1>
                        <p style={{ color: 'var(--ink-gray)', fontSize: '0.9rem' }}>
                            请按步骤完成望、闻、问、切四诊信息采集
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

                    {currentStep < 4 && (
                        <div className="bottom-nav">
                            <button
                                className="btn btn-ghost"
                                disabled={currentStep === 0}
                                onClick={() => setCurrentStep(prev => Math.max(0, prev - 1))}
                            >
                                ← 上一步
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={() => setCurrentStep(prev => Math.min(4, prev + 1))}
                            >
                                下一步 →
                            </button>
                        </div>
                    )}
                </div>
            </main>
        </>
    );
}
