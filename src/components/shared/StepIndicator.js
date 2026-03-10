'use client';

export default function StepIndicator({ steps, currentStep, onStepClick }) {
    return (
        <div className="step-indicator">
            {steps.map((step, index) => (
                <div key={index} style={{ display: 'flex', alignItems: 'center' }}>
                    <div
                        className={`step-item ${index === currentStep ? 'active' :
                                index < currentStep ? 'completed' : 'pending'
                            }`}
                        onClick={() => {
                            if (index <= currentStep && onStepClick) {
                                onStepClick(index);
                            }
                        }}
                        style={{ cursor: index <= currentStep ? 'pointer' : 'default' }}
                    >
                        <div className="step-number">
                            {index < currentStep ? '✓' : index + 1}
                        </div>
                        <span className="step-label">{step.icon} {step.label}</span>
                    </div>
                    {index < steps.length - 1 && (
                        <div className={`step-connector ${index < currentStep ? 'completed' : ''}`} />
                    )}
                </div>
            ))}
        </div>
    );
}
