'use client';

import { forwardRef, SelectHTMLAttributes, InputHTMLAttributes, ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';
import styles from './Select.module.css';

interface SelectOption {
    value: string;
    label: string;
    disabled?: boolean;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
    label?: string;
    helperText?: string;
    error?: string;
    required?: boolean;
    options: SelectOption[];
    placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
    (
        {
            label,
            helperText,
            error,
            required = false,
            options,
            placeholder,
            className = '',
            id,
            ...props
        },
        ref
    ) => {
        const selectId = id || `select-${Math.random().toString(36).slice(2)}`;

        return (
            <div className={styles.selectWrapper}>
                {label && (
                    <label htmlFor={selectId} className={styles.label}>
                        {label}
                        {required && <span className={styles.required}>*</span>}
                    </label>
                )}
                <div className={styles.selectContainer}>
                    <select
                        ref={ref}
                        id={selectId}
                        className={`${styles.select} ${error ? styles.selectError : ''} ${className}`}
                        aria-invalid={!!error}
                        {...props}
                    >
                        {placeholder && (
                            <option value="" disabled>
                                {placeholder}
                            </option>
                        )}
                        {options.map((option) => (
                            <option key={option.value} value={option.value} disabled={option.disabled}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                    <ChevronDown size={18} className={styles.chevron} />
                </div>
                {error && <p className={styles.errorText}>{error}</p>}
                {!error && helperText && <p className={styles.helperText}>{helperText}</p>}
            </div>
        );
    }
);

Select.displayName = 'Select';

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
    label: string;
    description?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
    ({ label, description, className = '', id, ...props }, ref) => {
        const checkId = id || `checkbox-${Math.random().toString(36).slice(2)}`;

        return (
            <div className={`${styles.checkWrapper} ${className}`}>
                <input
                    ref={ref}
                    type="checkbox"
                    id={checkId}
                    className={styles.checkInput}
                    {...props}
                />
                <div className={styles.checkContent}>
                    <label htmlFor={checkId} className={styles.checkLabel}>
                        {label}
                    </label>
                    {description && <p className={styles.checkDescription}>{description}</p>}
                </div>
            </div>
        );
    }
);

Checkbox.displayName = 'Checkbox';

export interface RadioProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
    label: string;
    description?: string;
}

export const Radio = forwardRef<HTMLInputElement, RadioProps>(
    ({ label, description, className = '', id, ...props }, ref) => {
        const radioId = id || `radio-${Math.random().toString(36).slice(2)}`;

        return (
            <div className={`${styles.checkWrapper} ${className}`}>
                <input
                    ref={ref}
                    type="radio"
                    id={radioId}
                    className={styles.checkInput}
                    {...props}
                />
                <div className={styles.checkContent}>
                    <label htmlFor={radioId} className={styles.checkLabel}>
                        {label}
                    </label>
                    {description && <p className={styles.checkDescription}>{description}</p>}
                </div>
            </div>
        );
    }
);

Radio.displayName = 'Radio';
