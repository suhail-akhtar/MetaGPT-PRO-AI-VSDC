'use client';

import { ReactNode, useState, createContext, useContext } from 'react';
import { motion } from 'framer-motion';
import styles from './Tabs.module.css';

interface Tab {
    id: string;
    label: string;
    icon?: ReactNode;
    disabled?: boolean;
    badge?: string | number;
}

interface TabsContextValue {
    activeTab: string;
    setActiveTab: (id: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

export interface TabsProps {
    tabs: Tab[];
    defaultTab?: string;
    onChange?: (tabId: string) => void;
    variant?: 'default' | 'pills' | 'underline';
    children: ReactNode;
}

export function Tabs({
    tabs,
    defaultTab,
    onChange,
    variant = 'default',
    children,
}: TabsProps) {
    const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

    const handleTabChange = (id: string) => {
        setActiveTab(id);
        onChange?.(id);
    };

    return (
        <TabsContext.Provider value={{ activeTab, setActiveTab: handleTabChange }}>
            <div className={styles.tabs}>
                <div className={`${styles.tabList} ${styles[variant]}`} role="tablist">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            role="tab"
                            aria-selected={activeTab === tab.id}
                            aria-controls={`tabpanel-${tab.id}`}
                            className={`${styles.tab} ${activeTab === tab.id ? styles.active : ''}`}
                            onClick={() => !tab.disabled && handleTabChange(tab.id)}
                            disabled={tab.disabled}
                        >
                            {tab.icon && <span className={styles.tabIcon}>{tab.icon}</span>}
                            {tab.label}
                            {tab.badge !== undefined && (
                                <span className={styles.tabBadge}>{tab.badge}</span>
                            )}
                            {variant === 'underline' && activeTab === tab.id && (
                                <motion.div
                                    className={styles.activeIndicator}
                                    layoutId="activeTab"
                                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                                />
                            )}
                        </button>
                    ))}
                </div>
                <div className={styles.tabPanels}>{children}</div>
            </div>
        </TabsContext.Provider>
    );
}

export interface TabPanelProps {
    id: string;
    children: ReactNode;
}

export function TabPanel({ id, children }: TabPanelProps) {
    const context = useContext(TabsContext);
    if (!context) throw new Error('TabPanel must be used within Tabs');

    if (context.activeTab !== id) return null;

    return (
        <motion.div
            id={`tabpanel-${id}`}
            role="tabpanel"
            aria-labelledby={`tab-${id}`}
            className={styles.tabPanel}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
        >
            {children}
        </motion.div>
    );
}
