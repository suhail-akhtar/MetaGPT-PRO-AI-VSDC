import { HTMLAttributes, ReactNode } from 'react';
import styles from './Avatar.module.css';

type AvatarSize = 'sm' | 'md' | 'lg' | 'xl';
type AvatarStatus = 'online' | 'busy' | 'idle' | 'offline';

export interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
    src?: string;
    name: string;
    size?: AvatarSize;
    status?: AvatarStatus;
}

function getInitials(name: string): string {
    return name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
}

function getAvatarUrl(name: string, size: number = 32): string {
    const colors = ['EC4899', '3B82F6', '10B981', '8B5CF6', 'F59E0B', 'EF4444'];
    const colorIndex = name.charCodeAt(0) % colors.length;
    const bg = colors[colorIndex];
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=${bg}&color=fff&size=${size}`;
}

export function Avatar({
    src,
    name,
    size = 'md',
    status,
    className = '',
    ...props
}: AvatarProps) {
    const sizeMap = { sm: 24, md: 32, lg: 40, xl: 48 };
    const imageSrc = src || getAvatarUrl(name, sizeMap[size] * 2);

    return (
        <div
            className={`${styles.avatar} ${styles[size]} ${className}`}
            title={name}
            {...props}
        >
            <img src={imageSrc} alt={name} className={styles.image} />
            {status && (
                <span className={`${styles.statusIndicator} ${styles[status]}`} />
            )}
        </div>
    );
}

export interface AvatarGroupProps extends HTMLAttributes<HTMLDivElement> {
    children: ReactNode;
    max?: number;
}

export function AvatarGroup({ children, max, className = '', ...props }: AvatarGroupProps) {
    return (
        <div className={`${styles.group} ${className}`} {...props}>
            {children}
        </div>
    );
}
