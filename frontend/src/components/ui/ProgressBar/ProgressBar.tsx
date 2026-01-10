import { HTMLAttributes } from 'react';
import styles from './ProgressBar.module.css';

type ProgressVariant = 'primary' | 'success' | 'warning' | 'danger';
type ProgressSize = 'sm' | 'md' | 'lg';

export interface ProgressBarProps extends HTMLAttributes<HTMLDivElement> {
    value: number;
    max?: number;
    variant?: ProgressVariant;
    size?: ProgressSize;
    showLabel?: boolean;
    label?: string;
    animated?: boolean;
}

export function ProgressBar({
    value,
    max = 100,
    variant = 'primary',
    size = 'md',
    showLabel = false,
    label,
    animated = false,
    className = '',
    ...props
}: ProgressBarProps) {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

    return (
        <div
            className={`${styles.progressContainer} ${styles[size]} ${animated ? styles.animated : ''} ${className}`}
            {...props}
        >
            {showLabel && (
                <div className={styles.label}>
                    <span>{label}</span>
                    <span>{Math.round(percentage)}%</span>
                </div>
            )}
            <div className={styles.track}>
                <div
                    className={`${styles.bar} ${styles[variant]}`}
                    style={{ width: `${percentage}%` }}
                    role="progressbar"
                    aria-valuenow={value}
                    aria-valuemin={0}
                    aria-valuemax={max}
                />
            </div>
        </div>
    );
}
