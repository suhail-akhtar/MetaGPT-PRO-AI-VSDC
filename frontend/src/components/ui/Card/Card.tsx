import { ReactNode, HTMLAttributes } from 'react';
import styles from './Card.module.css';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'glass' | 'glow';
    interactive?: boolean;
    noPadding?: boolean;
    children: ReactNode;
}

export function Card({
    variant = 'default',
    interactive = false,
    noPadding = false,
    className = '',
    children,
    ...props
}: CardProps) {
    const classNames = [
        styles.card,
        variant === 'glass' && styles.glass,
        variant === 'glow' && styles.glow,
        interactive && styles.interactive,
        noPadding && styles.noPadding,
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={classNames} {...props}>
            {children}
        </div>
    );
}

export interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
    gradient?: boolean;
    children: ReactNode;
}

export function CardHeader({ gradient = false, className = '', children, ...props }: CardHeaderProps) {
    const classNames = [
        styles.header,
        gradient && styles.gradientHeader,
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={classNames} {...props}>
            {children}
        </div>
    );
}

export interface CardBodyProps extends HTMLAttributes<HTMLDivElement> {
    size?: 'default' | 'large';
    children: ReactNode;
}

export function CardBody({ size = 'default', className = '', children, ...props }: CardBodyProps) {
    const classNames = [
        styles.body,
        size === 'large' && styles.bodyLarge,
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={classNames} {...props}>
            {children}
        </div>
    );
}

export interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {
    children: ReactNode;
}

export function CardFooter({ className = '', children, ...props }: CardFooterProps) {
    return (
        <div className={`${styles.footer} ${className}`} {...props}>
            {children}
        </div>
    );
}
