'use client';

export default function StepIndicator({ steps, currentStep, onStepClick }) {
    return (
        <div className="step-indicator">
            {steps.map((step, index) => (
                <div 
                    key={index} 
                    className={`step-item ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''}`}
                    onClick={() => onStepClick?.(index)}
                >
                    <div className="step-number">
                        {index < currentStep ? '✓' : step.icon}
                    </div>
                    <div className="step-label">{step.label}</div>
                    {index < steps.length - 1 && <div className="step-connector" />}
                </div>
            ))}
        </div>
    );
}
