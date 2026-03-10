'use client';

import { createContext, useContext, useState, useCallback } from 'react';

const DiagnosisContext = createContext(null);

const initialDiagnosisState = {
    // 望诊
    wangZhen: {
        faceColor: '',
        tongueColor: '',
        tongueCoating: '',
        tongueShape: '',
        bodyType: '',
        spirit: '',
        facePhoto: null,
        tonguePhoto: null,
    },
    // 闻诊
    wenZhen: {
        voiceType: '',
        breathType: '',
        coughType: '',
        bodySmell: '',
    },
    // 问诊
    wenZhenAsk: {
        mainComplaint: '',
        symptoms: [],
        duration: '',
        medicalHistory: '',
        dietPreference: '',
        stoolType: '',
        urineType: '',
        sleepQuality: '',
        emotionState: '',
        sweating: '',
        thirst: '',
        appetite: '',
        painLocation: '',
        painType: '',
    },
    // 切诊
    qieZhen: {
        pulseType: [],
        pulseStrength: '',
        pulseRhythm: '',
        abdomenPain: [],
    },
};

export function DiagnosisProvider({ children }) {
    const [diagnosis, setDiagnosis] = useState(initialDiagnosisState);
    const [currentStep, setCurrentStep] = useState(0);
    const [aiResults, setAiResults] = useState(null);
    const [doctorReviews, setDoctorReviews] = useState([]);
    const [patientSubmissions, setPatientSubmissions] = useState([]);

    const updateWangZhen = useCallback((data) => {
        setDiagnosis(prev => ({
            ...prev,
            wangZhen: { ...prev.wangZhen, ...data }
        }));
    }, []);

    const updateWenZhen = useCallback((data) => {
        setDiagnosis(prev => ({
            ...prev,
            wenZhen: { ...prev.wenZhen, ...data }
        }));
    }, []);

    const updateWenZhenAsk = useCallback((data) => {
        setDiagnosis(prev => ({
            ...prev,
            wenZhenAsk: { ...prev.wenZhenAsk, ...data }
        }));
    }, []);

    const updateQieZhen = useCallback((data) => {
        setDiagnosis(prev => ({
            ...prev,
            qieZhen: { ...prev.qieZhen, ...data }
        }));
    }, []);

    const submitDiagnosis = useCallback(() => {
        const submission = {
            id: Date.now().toString(),
            patientName: '患者' + Math.floor(Math.random() * 1000),
            timestamp: new Date().toISOString(),
            diagnosis: { ...diagnosis },
            status: 'pending',
        };
        setPatientSubmissions(prev => [...prev, submission]);
        return submission;
    }, [diagnosis]);

    const resetDiagnosis = useCallback(() => {
        setDiagnosis(initialDiagnosisState);
        setCurrentStep(0);
        setAiResults(null);
    }, []);

    const value = {
        diagnosis,
        currentStep,
        setCurrentStep,
        aiResults,
        setAiResults,
        doctorReviews,
        setDoctorReviews,
        patientSubmissions,
        setPatientSubmissions,
        updateWangZhen,
        updateWenZhen,
        updateWenZhenAsk,
        updateQieZhen,
        submitDiagnosis,
        resetDiagnosis,
    };

    return (
        <DiagnosisContext.Provider value={value}>
            {children}
        </DiagnosisContext.Provider>
    );
}

export function useDiagnosis() {
    const context = useContext(DiagnosisContext);
    if (!context) {
        throw new Error('useDiagnosis must be used within DiagnosisProvider');
    }
    return context;
}
