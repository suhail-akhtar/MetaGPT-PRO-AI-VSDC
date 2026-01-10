'use client';

import { forwardRef, InputHTMLAttributes, TextareaHTMLAttributes, ReactNode, useState } from 'react';
import { AlertCircle, Eye, EyeOff } from 'lucide-react';
import styles from './Input.module.css';

type InputSize = 'sm' | 'md' | 'lg';

interface BaseInputProps {
    label?: string;
    helperText?: string;
    error?: string;
    required?: boolean;
    optional?: boolean;
    leftIcon?: ReactNode;
    rightIcon?: ReactNode;
    size?: InputSize;
}

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'>, BaseInputProps { }

export const Input = forwardRef<HTMLInputElement, InputProps>(
    (
        {
            label,
            helperText,
            error,
            required = false,
            optional = false,
            leftIcon,
            rightIcon,
            size = 'md',
            type = 'text',
            className = '',
            id,
            ...props
        },
        ref
    ) => {
        const [showPassword, setShowPassword] = useState(false);
        const inputId = id || `input-${Math.random().toString(36).slice(2)}`;
        const isPassword = type === 'password';

        const inputClassName = [
            styles.input,
            leftIcon && styles.hasLeftIcon,
            (rightIcon || isPassword) && styles.hasRightIcon,
            error && styles.inputError,
            className,
        ]
            .filter(Boolean)
            .join(' ');

        return (
            <div className={`${styles.inputWrapper} ${styles[size]}`}>
                {label && (
                    <label htmlFor={inputId} className={styles.label}>
                        {label}
                        {required && <span className={styles.required}>*</span>}
                        {optional && <span className={styles.optional}>(optional)</span>}
                    </label>
                )}
                <div className={styles.inputContainer}>
                    {leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}
                    <input
                        ref={ref}
                        id={inputId}
                        type={isPassword && showPassword ? 'text' : type}
                        className={inputClassName}
                        aria-invalid={!!error}
                        aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
                        {...props}
                    />
                    {isPassword && (
                        <button
                            type="button"
                            className={styles.rightIconBtn}
                            onClick={() => setShowPassword(!showPassword)}
                            tabIndex={-1}
                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                        >
                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                        </button>
                    )}
                    {!isPassword && rightIcon && <span className={styles.rightIcon}>{rightIcon}</span>}
                </div>
                {error && (
                    <p id={`${inputId}-error`} className={styles.errorText}>
                        <AlertCircle size={14} />
                        {error}
                    </p>
                )}
                {!error && helperText && (
                    <p id={`${inputId}-helper`} className={styles.helperText}>
                        {helperText}
                    </p>
                )}
            </div>
        );
    }
);

Input.displayName = 'Input';

export interface TextareaProps extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'size'>, BaseInputProps {
    noResize?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
    (
        {
            label,
            helperText,
            error,
            required = false,
            optional = false,
            leftIcon,
            size = 'md',
            noResize = false,
            className = '',
            id,
            ...props
        },
        ref
    ) => {
        const inputId = id || `textarea-${Math.random().toString(36).slice(2)}`;

        const inputClassName = [
            styles.input,
            styles.textarea,
            noResize && styles.noResize,
            error && styles.inputError,
            className,
        ]
            .filter(Boolean)
            .join(' ');

        return (
            <div className={`${styles.inputWrapper} ${styles[size]}`}>
                {label && (
                    <label htmlFor={inputId} className={styles.label}>
                        {label}
                        {required && <span className={styles.required}>*</span>}
                        {optional && <span className={styles.optional}>(optional)</span>}
                    </label>
                )}
                <div className={styles.inputContainer}>
                    <textarea
                        ref={ref}
                        id={inputId}
                        className={inputClassName}
                        aria-invalid={!!error}
                        aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
                        {...props}
                    />
                </div>
                {error && (
                    <p id={`${inputId}-error`} className={styles.errorText}>
                        <AlertCircle size={14} />
                        {error}
                    </p>
                )}
                {!error && helperText && (
                    <p id={`${inputId}-helper`} className={styles.helperText}>
                        {helperText}
                    </p>
                )}
            </div>
        );
    }
);

Textarea.displayName = 'Textarea';
