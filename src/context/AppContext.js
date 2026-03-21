'use client';

import { createContext, useContext, useState, useCallback, useEffect } from 'react';

const AppContext = createContext(null);

const initialPatientState = {
    id: null,
    name: '',
    age: '',
    gender: '',
    phone: '',
    diagnosis: {
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
        wenZhen: {
            voiceType: '',
            breathType: '',
            coughType: '',
            bodySmell: '',
        },
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
        qieZhen: {
            pulseType: [],
            pulseStrength: '',
            pulseRhythm: '',
            abdomenPain: [],
        },
    },
    aiResults: null,
    status: 'pending',
    timestamp: null,
};

const initialDoctorState = {
    id: 'doctor_001',
    name: '李医生',
    title: '主任医师',
    department: '中医内科',
    avatar: null,
};

export function AppProvider({ children }) {
    const [currentUser, setCurrentUser] = useState(null);
    const [userType, setUserType] = useState(null);
    const [currentPatient, setCurrentPatient] = useState(initialPatientState);
    const [currentStep, setCurrentStep] = useState(0);
    const [patients, setPatients] = useState([]);
    const [diagnoses, setDiagnoses] = useState([]);
    const [notifications, setNotifications] = useState([]);
    const [doctorInfo, setDoctorInfo] = useState(initialDoctorState);

    useEffect(() => {
        const savedPatients = localStorage.getItem('tcm_patients');
        const savedDiagnoses = localStorage.getItem('tcm_diagnoses');
        if (savedPatients) setPatients(JSON.parse(savedPatients));
        if (savedDiagnoses) setDiagnoses(JSON.parse(savedDiagnoses));
    }, []);

    useEffect(() => {
        localStorage.setItem('tcm_patients', JSON.stringify(patients));
        localStorage.setItem('tcm_diagnoses', JSON.stringify(diagnoses));
    }, [patients, diagnoses]);

    const loginAsPatient = useCallback((patientInfo) => {
        const patient = {
            ...initialPatientState,
            id: 'patient_' + Date.now(),
            ...patientInfo,
            timestamp: new Date().toISOString(),
        };
        setCurrentPatient(patient);
        setUserType('patient');
        setCurrentUser(patient);
        return patient;
    }, []);

    const loginAsDoctor = useCallback((doctorData) => {
        setDoctorInfo(prev => ({ ...prev, ...doctorData }));
        setUserType('doctor');
        setCurrentUser({ ...initialDoctorState, ...doctorData });
        return doctorInfo;
    }, [doctorInfo]);

    const logout = useCallback(() => {
        setCurrentUser(null);
        setUserType(null);
        setCurrentPatient(initialPatientState);
        setCurrentStep(0);
    }, []);

    const updateDiagnosis = useCallback((section, data) => {
        setCurrentPatient(prev => ({
            ...prev,
            diagnosis: {
                ...prev.diagnosis,
                [section]: { ...prev.diagnosis[section], ...data }
            }
        }));
    }, []);

    const setAiResults = useCallback((results) => {
        setCurrentPatient(prev => ({
            ...prev,
            aiResults: results
        }));
    }, []);

    const submitDiagnosis = useCallback(() => {
        const diagnosis = {
            id: 'diag_' + Date.now(),
            patientId: currentPatient.id,
            patientName: currentPatient.name || '患者',
            patientInfo: {
                age: currentPatient.age,
                gender: currentPatient.gender,
                phone: currentPatient.phone,
            },
            diagnosis: currentPatient.diagnosis,
            aiResults: currentPatient.aiResults,
            status: 'pending',
            doctorNote: '',
            doctorModified: false,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
        };
        
        setDiagnoses(prev => [diagnosis, ...prev]);
        setPatients(prev => {
            const exists = prev.find(p => p.id === currentPatient.id);
            if (exists) {
                return prev.map(p => p.id === currentPatient.id ? { ...p, lastVisit: new Date().toISOString() } : p);
            }
            return [{ id: currentPatient.id, name: currentPatient.name, lastVisit: new Date().toISOString() }, ...prev];
        });

        addNotification({
            type: 'new_diagnosis',
            title: '新诊断提交',
            message: `患者 ${currentPatient.name || '匿名'} 提交了新的诊断请求`,
            diagnosisId: diagnosis.id,
        });

        return diagnosis;
    }, [currentPatient]);

    const updateDiagnosisStatus = useCallback((diagnosisId, status, doctorNote, modifiedResults) => {
        setDiagnoses(prev => prev.map(d => 
            d.id === diagnosisId ? {
                ...d,
                status,
                doctorNote,
                doctorModified: !!modifiedResults,
                aiResults: modifiedResults || d.aiResults,
                updatedAt: new Date().toISOString(),
                reviewedAt: new Date().toISOString(),
                reviewedBy: doctorInfo.name,
            } : d
        ));
    }, [doctorInfo.name]);

    const addNotification = useCallback((notification) => {
        const newNotification = {
            id: 'notif_' + Date.now(),
            ...notification,
            read: false,
            createdAt: new Date().toISOString(),
        };
        setNotifications(prev => [newNotification, ...prev]);
    }, []);

    const markNotificationRead = useCallback((notificationId) => {
        setNotifications(prev => prev.map(n => 
            n.id === notificationId ? { ...n, read: true } : n
        ));
    }, []);

    const resetPatient = useCallback(() => {
        setCurrentPatient(initialPatientState);
        setCurrentStep(0);
    }, []);

    const value = {
        currentUser,
        userType,
        currentPatient,
        currentStep,
        patients,
        diagnoses,
        notifications,
        doctorInfo,
        
        loginAsPatient,
        loginAsDoctor,
        logout,
        
        setCurrentStep,
        updateDiagnosis,
        setAiResults,
        submitDiagnosis,
        resetPatient,
        
        updateDiagnosisStatus,
        setDoctorInfo,
        
        addNotification,
        markNotificationRead,
    };

    return (
        <AppContext.Provider value={value}>
            {children}
        </AppContext.Provider>
    );
}

export function useApp() {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp must be used within AppProvider');
    }
    return context;
}
