import { HTMLAttributes } from 'react';
import styles from './Spinner.module.css';

type SpinnerSize = 'sm' | 'md' | 'lg' | 'xl';

export interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
    size?: SpinnerSize;
    label?: string;
}

export function Spinner({ size = 'md', label, className = '', ...props }: SpinnerProps) {
    return (
        <div
            className={`${styles.spinner} ${styles[size]} ${className}`}
            role="status"
            aria-label={label || 'Loading'}
            {...props}
        >
            <div className={styles.ring} />
            {label && <span className={styles.label}>{label}</span>}
        </div>
    );
}

// Skeleton loading states
type SkeletonVariant = 'text' | 'circle' | 'rect' | 'card';

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
    variant?: SkeletonVariant;
    width?: string | number;
    height?: string | number;
    lines?: number;
}

export function Skeleton({
    variant = 'text',
    width,
    height,
    lines = 1,
    className = '',
    style,
    ...props
}: SkeletonProps) {
    const skeletonStyle = {
        ...style,
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
    };

    if (variant === 'text' && lines > 1) {
        return (
            <div className={`${styles.skeletonContainer} ${className}`} {...props}>
                {Array.from({ length: lines }).map((_, i) => (
                    <div
                        key={i}
                        className={`${styles.skeleton} ${styles.text}`}
                        style={{ width: i === lines - 1 ? '70%' : '100%' }}
                    />
                ))}
            </div>
        );
    }

    return (
        <div
            className={`${styles.skeleton} ${styles[variant]} ${className}`}
            style={skeletonStyle}
            {...props}
        />
    );
}
