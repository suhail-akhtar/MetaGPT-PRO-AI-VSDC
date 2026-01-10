import { ReactNode, HTMLAttributes } from 'react';
import styles from './Badge.module.css';

type BadgeVariant =
    | 'default'
    | 'primary'
    | 'success'
    | 'warning'
    | 'danger'
    | 'info'
    | 'active'
    | 'planning'
    | 'completed'
    | 'paused'
    | 'critical'
    | 'high'
    | 'medium'
    | 'low';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
    variant?: BadgeVariant;
    dot?: boolean;
    pulse?: boolean;
    children: ReactNode;
}

export function Badge({
    variant = 'default',
    dot = false,
    pulse = false,
    className = '',
    children,
    ...props
}: BadgeProps) {
    const classNames = [styles.badge, styles[variant], className]
        .filter(Boolean)
        .join(' ');

    return (
        <span className={classNames} {...props}>
            {dot && <span className={`${styles.dot} ${pulse ? styles.dotPulse : ''}`} />}
            {children}
        </span>
    );
}
