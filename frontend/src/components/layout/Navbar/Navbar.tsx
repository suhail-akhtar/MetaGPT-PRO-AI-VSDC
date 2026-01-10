'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Brain, FolderOpen, PlusCircle, Bell, Folder } from 'lucide-react';
import { Avatar } from '@/components/ui';
import styles from './Navbar.module.css';

interface NavItem {
    href: string;
    label: string;
    icon: React.ReactNode;
}

const navItems: NavItem[] = [
    { href: '/projects', label: 'Projects', icon: <Folder size={18} /> },
    { href: '/new', label: 'New Project', icon: <PlusCircle size={18} /> },
    { href: '/files', label: 'Files', icon: <FolderOpen size={18} /> },
];

export function Navbar() {
    const pathname = usePathname();

    const isActive = (href: string) => {
        if (href === '/projects') {
            return pathname === '/projects' || pathname.startsWith('/project/');
        }
        return pathname === href || pathname.startsWith(href);
    };

    return (
        <nav className={styles.nav}>
            <div className={styles.container}>
                <div className={styles.left}>
                    <Link href="/projects" className={styles.logo}>
                        <Brain size={28} className={styles.logoIcon} />
                        <span>MetaGPT-Pro</span>
                    </Link>

                    <div className={styles.navLinks}>
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`${styles.navLink} ${isActive(item.href) ? styles.navLinkActive : ''}`}
                            >
                                {item.icon}
                                {item.label}
                            </Link>
                        ))}
                    </div>
                </div>

                <div className={styles.right}>
                    <button className={styles.notificationBtn}>
                        <Bell size={20} />
                        <span className={styles.notificationDot} />
                    </button>

                    <button className={styles.userButton}>
                        <Avatar name="Admin" size="md" />
                    </button>
                </div>
            </div>
        </nav>
    );
}
