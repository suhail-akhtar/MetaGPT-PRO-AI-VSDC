'use client';

import { ReactNode, useEffect, useCallback, useState } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { motion, AnimatePresence, Variants } from 'framer-motion';
import styles from './Modal.module.css';

type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';
type ModalVariant = 'default' | 'success' | 'warning' | 'danger';

export interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    description?: string;
    icon?: ReactNode;
    variant?: ModalVariant;
    size?: ModalSize;
    showCloseButton?: boolean;
    closeOnOverlayClick?: boolean;
    closeOnEscape?: boolean;
    children: ReactNode;
    footer?: ReactNode;
    footerSpread?: boolean;
}

const overlayVariants: Variants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
};

const modalVariants: Variants = {
    hidden: { opacity: 0, scale: 0.95, y: 20 },
    visible: {
        opacity: 1,
        scale: 1,
        y: 0,
    },
    exit: {
        opacity: 0,
        scale: 0.95,
        y: 20,
    },
};

export function Modal({
    isOpen,
    onClose,
    title,
    description,
    icon,
    variant = 'default',
    size = 'md',
    showCloseButton = true,
    closeOnOverlayClick = true,
    closeOnEscape = true,
    children,
    footer,
    footerSpread = false,
}: ModalProps) {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const handleEscape = useCallback(
        (e: KeyboardEvent) => {
            if (e.key === 'Escape' && closeOnEscape) {
                onClose();
            }
        },
        [closeOnEscape, onClose]
    );

    useEffect(() => {
        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }
        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = '';
        };
    }, [isOpen, handleEscape]);

    const handleOverlayClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget && closeOnOverlayClick) {
            onClose();
        }
    };

    if (!mounted) return null;

    return createPortal(
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    className={styles.overlay}
                    onClick={handleOverlayClick}
                    variants={overlayVariants}
                    initial="hidden"
                    animate="visible"
                    exit="hidden"
                >
                    <motion.div
                        className={`${styles.modal} ${styles[size]}`}
                        variants={modalVariants}
                        initial="hidden"
                        animate="visible"
                        exit="exit"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby={title ? 'modal-title' : undefined}
                    >
                        {(title || showCloseButton) && (
                            <div className={styles.header}>
                                <div className={styles.headerContent}>
                                    {icon && (
                                        <div className={`${styles.icon} ${styles[`icon${variant.charAt(0).toUpperCase() + variant.slice(1)}`]}`}>
                                            {icon}
                                        </div>
                                    )}
                                    <div>
                                        {title && (
                                            <h2 id="modal-title" className={styles.title}>
                                                {title}
                                            </h2>
                                        )}
                                        {description && (
                                            <p className={styles.description}>{description}</p>
                                        )}
                                    </div>
                                </div>
                                {showCloseButton && (
                                    <button
                                        className={styles.closeBtn}
                                        onClick={onClose}
                                        aria-label="Close modal"
                                    >
                                        <X size={20} />
                                    </button>
                                )}
                            </div>
                        )}
                        <div className={styles.body}>{children}</div>
                        {footer && (
                            <div className={`${styles.footer} ${footerSpread ? styles.footerSpread : ''}`}>
                                {footer}
                            </div>
                        )}
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>,
        document.body
    );
}
