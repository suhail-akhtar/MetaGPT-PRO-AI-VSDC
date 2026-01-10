'use client';

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { config } from '@/lib/config';
import styles from './Toast.module.css';

type ToastType = 'success' | 'error' | 'warning' | 'info';
type ToastPosition = 'top-right' | 'top-left' | 'top-center' | 'bottom-right' | 'bottom-left' | 'bottom-center';

interface ToastAction {
    label: string;
    onClick: () => void;
}

interface Toast {
    id: string;
    type: ToastType;
    title?: string;
    message: string;
    duration?: number;
    action?: ToastAction;
    dismissible?: boolean;
}

interface ToastContextValue {
    toasts: Toast[];
    addToast: (toast: Omit<Toast, 'id'>) => string;
    removeToast: (id: string) => void;
    success: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => string;
    error: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => string;
    warning: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => string;
    info: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => string;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
}

const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
};

const toastVariants = {
    initial: { opacity: 0, x: 50, scale: 0.9 },
    animate: { opacity: 1, x: 0, scale: 1 },
    exit: { opacity: 0, x: 50, scale: 0.9 },
};

interface ToastProviderProps {
    children: ReactNode;
    position?: ToastPosition;
    maxToasts?: number;
}

export function ToastProvider({
    children,
    position = 'top-right',
    maxToasts = 5,
}: ToastProviderProps) {
    const [toasts, setToasts] = useState<Toast[]>([]);
    const [mounted, setMounted] = useState(false);

    // Only render portal after client-side hydration
    useEffect(() => {
        setMounted(true);
    }, []);

    const removeToast = useCallback((id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
        const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`;
        const duration = toast.duration ?? config.ui.toastDuration;

        setToasts((prev) => {
            const newToasts = [...prev, { ...toast, id }];
            return newToasts.slice(-maxToasts);
        });

        if (duration > 0) {
            setTimeout(() => removeToast(id), duration);
        }

        return id;
    }, [maxToasts, removeToast]);

    const success = useCallback((message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => {
        return addToast({ type: 'success', message, ...options });
    }, [addToast]);

    const error = useCallback((message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => {
        return addToast({ type: 'error', message, duration: 0, ...options });
    }, [addToast]);

    const warning = useCallback((message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => {
        return addToast({ type: 'warning', message, ...options });
    }, [addToast]);

    const info = useCallback((message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => {
        return addToast({ type: 'info', message, ...options });
    }, [addToast]);

    const positionClass = position.split('-').map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join('');

    return (
        <ToastContext.Provider value={{ toasts, addToast, removeToast, success, error, warning, info }}>
            {children}
            {mounted &&
                createPortal(
                    <div className={`${styles.toastContainer} ${styles[positionClass.charAt(0).toLowerCase() + positionClass.slice(1)]}`}>
                        <AnimatePresence mode="sync">
                            {toasts.map((toast) => {
                                const Icon = icons[toast.type];
                                return (
                                    <motion.div
                                        key={toast.id}
                                        className={`${styles.toast} ${styles[toast.type]}`}
                                        variants={toastVariants}
                                        initial="initial"
                                        animate="animate"
                                        exit="exit"
                                        layout
                                    >
                                        <Icon className={styles.toastIcon} size={20} />
                                        <div className={styles.toastContent}>
                                            {toast.title && <p className={styles.toastTitle}>{toast.title}</p>}
                                            <p className={styles.toastMessage}>{toast.message}</p>
                                            {toast.action && (
                                                <div className={styles.toastAction}>
                                                    <button
                                                        className={styles.toastActionBtn}
                                                        onClick={() => {
                                                            toast.action?.onClick();
                                                            removeToast(toast.id);
                                                        }}
                                                    >
                                                        {toast.action.label}
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                        {(toast.dismissible ?? true) && (
                                            <button
                                                className={styles.closeBtn}
                                                onClick={() => removeToast(toast.id)}
                                                aria-label="Dismiss"
                                            >
                                                <X size={16} />
                                            </button>
                                        )}
                                    </motion.div>
                                );
                            })}
                        </AnimatePresence>
                    </div>,
                    document.body
                )}
        </ToastContext.Provider>
    );
}

