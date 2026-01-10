'use client';

import { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import Link from 'next/link';
import styles from './ErrorBoundary.module.css';

interface ErrorBoundaryProps {
    children: ReactNode;
    fallback?: ReactNode;
    onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('[ErrorBoundary]', error, errorInfo);
        this.props.onError?.(error, errorInfo);
    }

    handleRetry = () => {
        this.setState({ hasError: false, error: null });
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className={styles.errorContainer}>
                    <div className={styles.errorContent}>
                        <div className={styles.iconWrapper}>
                            <AlertTriangle size={48} />
                        </div>
                        <h2 className={styles.title}>Something went wrong</h2>
                        <p className={styles.message}>
                            We encountered an unexpected error. Please try again or return to the home page.
                        </p>
                        {process.env.NODE_ENV === 'development' && this.state.error && (
                            <pre className={styles.errorDetails}>
                                {this.state.error.message}
                                {'\n\n'}
                                {this.state.error.stack}
                            </pre>
                        )}
                        <div className={styles.actions}>
                            <button onClick={this.handleRetry} className={styles.retryBtn}>
                                <RefreshCw size={18} />
                                Try Again
                            </button>
                            <Link href="/projects" className={styles.homeBtn}>
                                <Home size={18} />
                                Go Home
                            </Link>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

// Error display component for inline errors
interface ErrorDisplayProps {
    error: Error | string | null;
    onRetry?: () => void;
    className?: string;
}

export function ErrorDisplay({ error, onRetry, className = '' }: ErrorDisplayProps) {
    if (!error) return null;

    const message = typeof error === 'string' ? error : error.message;

    return (
        <div className={`${styles.inlineError} ${className}`}>
            <AlertTriangle size={16} className={styles.inlineIcon} />
            <span className={styles.inlineMessage}>{message}</span>
            {onRetry && (
                <button onClick={onRetry} className={styles.inlineRetry}>
                    Retry
                </button>
            )}
        </div>
    );
}

// Empty state component
interface EmptyStateProps {
    icon?: ReactNode;
    title: string;
    description?: string;
    action?: ReactNode;
    className?: string;
}

export function EmptyState({ icon, title, description, action, className = '' }: EmptyStateProps) {
    return (
        <div className={`${styles.emptyState} ${className}`}>
            {icon && <div className={styles.emptyIcon}>{icon}</div>}
            <h3 className={styles.emptyTitle}>{title}</h3>
            {description && <p className={styles.emptyDescription}>{description}</p>}
            {action && <div className={styles.emptyAction}>{action}</div>}
        </div>
    );
}

// Loading state component
interface LoadingStateProps {
    message?: string;
    size?: 'sm' | 'md' | 'lg';
    className?: string;
}

export function LoadingState({ message, size = 'md', className = '' }: LoadingStateProps) {
    return (
        <div className={`${styles.loadingState} ${className}`}>
            <div className={`${styles.spinner} ${styles[size]}`} />
            {message && <p className={styles.loadingMessage}>{message}</p>}
        </div>
    );
}
