'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { use } from 'react';
import { ArrowLeft, Folder, FileText, FileCode, ChevronRight, Grid, List, X, Copy, Home } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Navbar } from '@/components/layout';
import { Button, useToast, LoadingState, ErrorDisplay } from '@/components/ui';
import { useFileTree, useFileContent, FileNode } from '@/lib/hooks';
import styles from './page.module.css';

interface FileItem {
    name: string;
    type: 'folder' | 'file';
    size?: string;
    modified: string;
    extension?: string;
    content?: string;
}

interface BreadcrumbItem {
    name: string;
    path: string;
}

// Fallback file structure
const fallbackFiles: Record<string, FileItem[]> = {
    '/': [
        { name: 'src', type: 'folder', modified: '2 hours ago' },
        { name: 'tests', type: 'folder', modified: '1 day ago' },
        { name: 'docs', type: 'folder', modified: '3 days ago' },
        { name: 'README.md', type: 'file', size: '2.4 KB', modified: '1 day ago', extension: 'md' },
        { name: 'package.json', type: 'file', size: '1.2 KB', modified: '2 hours ago', extension: 'json' },
        { name: 'tsconfig.json', type: 'file', size: '0.8 KB', modified: '5 days ago', extension: 'json' },
    ],
    '/src': [
        { name: 'components', type: 'folder', modified: '1 hour ago' },
        { name: 'services', type: 'folder', modified: '3 hours ago' },
        { name: 'utils', type: 'folder', modified: '2 days ago' },
        { name: 'main.py', type: 'file', size: '3.1 KB', modified: '2 hours ago', extension: 'py' },
        { name: 'config.py', type: 'file', size: '1.5 KB', modified: '1 day ago', extension: 'py' },
        { name: 'types.ts', type: 'file', size: '4.2 KB', modified: '5 hours ago', extension: 'ts' },
    ],
    '/src/services': [
        {
            name: 'payment.py', type: 'file', size: '8.4 KB', modified: '30 min ago', extension: 'py', content: `"""Payment Service Module"""
import stripe
from typing import Optional
from ..config import settings

class PaymentService:
    """Handles all payment operations."""
    
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
    
    async def create_payment_intent(
        self, 
        amount: int, 
        currency: str = "usd",
        customer_id: Optional[str] = None
    ) -> dict:
        """Create a payment intent for checkout."""
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                automatic_payment_methods={"enabled": True}
            )
            return {"client_secret": intent.client_secret}
        except stripe.error.StripeError as e:
            raise PaymentError(str(e))
    
    async def process_refund(
        self, 
        payment_id: str, 
        amount: Optional[int] = None
    ) -> dict:
        """Process a refund for a payment."""
        refund = self.stripe.Refund.create(
            payment_intent=payment_id,
            amount=amount
        )
        return {"refund_id": refund.id, "status": refund.status}
` },
        { name: 'auth.py', type: 'file', size: '5.2 KB', modified: '1 hour ago', extension: 'py' },
        { name: 'email.py', type: 'file', size: '2.8 KB', modified: '2 days ago', extension: 'py' },
    ],
};

const getFileIcon = (extension?: string) => {
    if (!extension) return { icon: FileText, className: styles.iconFile };

    const iconMap: Record<string, { icon: typeof FileText; className: string }> = {
        py: { icon: FileCode, className: styles.iconPy },
        ts: { icon: FileCode, className: styles.iconTs },
        tsx: { icon: FileCode, className: styles.iconTs },
        js: { icon: FileCode, className: styles.iconTs },
        json: { icon: FileText, className: styles.iconJson },
        md: { icon: FileText, className: styles.iconMd },
    };

    return iconMap[extension] || { icon: FileText, className: styles.iconFile };
};

interface PageProps {
    params: Promise<{ id: string }>;
}

export default function FilesPage({ params }: PageProps) {
    const { id: projectId } = use(params);
    const { success, error: showError } = useToast();
    const [currentPath, setCurrentPath] = useState('/');
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);

    // API hooks
    const { data: fileTreeData, isLoading, isError, error, refetch } = useFileTree(projectId);
    const { data: fileContentData } = useFileContent(
        projectId,
        selectedFile ? `${currentPath}/${selectedFile.name}` : null
    );

    // Local files state
    const [filesMap, setFilesMap] = useState<Record<string, FileItem[]>>(fallbackFiles);

    // Sync API data
    useEffect(() => {
        if (fileTreeData?.files) {
            // Transform API file tree to local format
            const newFilesMap: Record<string, FileItem[]> = { '/': [] };
            fileTreeData.files.forEach((file: FileNode) => {
                const parentPath = file.path.split('/').slice(0, -1).join('/') || '/';
                if (!newFilesMap[parentPath]) {
                    newFilesMap[parentPath] = [];
                }
                newFilesMap[parentPath].push({
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    modified: file.modified || 'Recently',
                    extension: file.name.includes('.') ? file.name.split('.').pop() : undefined,
                });
            });
            setFilesMap(newFilesMap);
        }
    }, [fileTreeData]);

    // Update file content when loaded
    useEffect(() => {
        if (fileContentData?.content && selectedFile) {
            setSelectedFile((prev) => prev ? { ...prev, content: fileContentData.content } : null);
        }
    }, [fileContentData, selectedFile]);

    const files = filesMap[currentPath] || [];

    const breadcrumbs: BreadcrumbItem[] = [
        { name: 'Root', path: '/' },
        ...currentPath.split('/').filter(Boolean).map((segment, index, arr) => ({
            name: segment,
            path: '/' + arr.slice(0, index + 1).join('/'),
        })),
    ];

    const handleNavigate = (file: FileItem) => {
        if (file.type === 'folder') {
            setCurrentPath(currentPath === '/' ? `/${file.name}` : `${currentPath}/${file.name}`);
            setSelectedFile(null);
        } else {
            setSelectedFile(file);
        }
    };

    const handleBreadcrumbClick = (path: string) => {
        setCurrentPath(path);
        setSelectedFile(null);
    };

    const handleCopyContent = () => {
        if (selectedFile?.content) {
            navigator.clipboard.writeText(selectedFile.content);
            success('Content copied to clipboard');
        }
    };

    if (isLoading) {
        return (
            <>
                <Navbar />
                <main className="container">
                    <LoadingState message="Loading files..." />
                </main>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <main className="container">
                <div className={styles.page}>
                    {/* Error Banner */}
                    {isError && (
                        <ErrorDisplay
                            error={error}
                            onRetry={refetch}
                        />
                    )}

                    {/* Header */}
                    <div className={styles.header}>
                        <div className={styles.headerLeft}>
                            <Link href={`/project/${projectId}`} className={styles.backBtn}>
                                <ArrowLeft size={20} />
                            </Link>
                            <h1 className={styles.title}>File Explorer</h1>
                        </div>
                        <div className={styles.headerRight}>
                            <div className={styles.viewToggle}>
                                <button
                                    className={`${styles.viewBtn} ${viewMode === 'grid' ? styles.viewBtnActive : ''}`}
                                    onClick={() => setViewMode('grid')}
                                >
                                    <Grid size={18} />
                                </button>
                                <button
                                    className={`${styles.viewBtn} ${viewMode === 'list' ? styles.viewBtnActive : ''}`}
                                    onClick={() => setViewMode('list')}
                                >
                                    <List size={18} />
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Breadcrumb */}
                    <div className={styles.breadcrumb}>
                        {breadcrumbs.map((crumb, index) => (
                            <span key={crumb.path} className={styles.breadcrumbItem}>
                                {index === 0 ? (
                                    <Home size={14} />
                                ) : (
                                    <ChevronRight size={14} className={styles.breadcrumbSeparator} />
                                )}
                                <span
                                    onClick={() => handleBreadcrumbClick(crumb.path)}
                                    className={index === breadcrumbs.length - 1 ? styles.breadcrumbCurrent : ''}
                                >
                                    {crumb.name}
                                </span>
                            </span>
                        ))}
                    </div>

                    {/* File Grid/List */}
                    {viewMode === 'grid' ? (
                        <div className={styles.fileGrid}>
                            <AnimatePresence mode="popLayout">
                                {files.map((file) => {
                                    const { icon: FileIcon, className: iconClassName } = file.type === 'folder'
                                        ? { icon: Folder, className: styles.iconFolder }
                                        : getFileIcon(file.extension);

                                    return (
                                        <motion.div
                                            key={file.name}
                                            className={styles.fileCard}
                                            onClick={() => handleNavigate(file)}
                                            layout
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            exit={{ opacity: 0, scale: 0.9 }}
                                            whileHover={{ y: -2 }}
                                        >
                                            <div className={`${styles.fileIcon} ${iconClassName}`}>
                                                <FileIcon size={24} />
                                            </div>
                                            <p className={styles.fileName}>{file.name}</p>
                                            <p className={styles.fileMeta}>
                                                {file.size || 'Folder'} • {file.modified}
                                            </p>
                                        </motion.div>
                                    );
                                })}
                            </AnimatePresence>
                        </div>
                    ) : (
                        <div className={styles.fileTable}>
                            <table className={styles.table}>
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Size</th>
                                        <th>Modified</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {files.map((file) => {
                                        const { icon: FileIcon, className: iconClassName } = file.type === 'folder'
                                            ? { icon: Folder, className: styles.iconFolder }
                                            : getFileIcon(file.extension);

                                        return (
                                            <tr key={file.name} onClick={() => handleNavigate(file)}>
                                                <td>
                                                    <div className={styles.tableFileName}>
                                                        <div className={`${styles.tableFileIcon} ${iconClassName}`}>
                                                            <FileIcon size={18} />
                                                        </div>
                                                        {file.name}
                                                    </div>
                                                </td>
                                                <td>{file.size || '--'}</td>
                                                <td>{file.modified}</td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </main>

            {/* Preview Panel */}
            <AnimatePresence>
                {selectedFile && (
                    <motion.div
                        className={`${styles.previewPanel} ${selectedFile ? styles.previewPanelOpen : ''}`}
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 25 }}
                    >
                        <div className={styles.previewHeader}>
                            <h3 className={styles.previewTitle}>
                                <FileCode size={18} />
                                {selectedFile.name}
                            </h3>
                            <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                                <Button variant="ghost" size="sm" icon={<Copy size={16} />} onClick={handleCopyContent}>
                                    Copy
                                </Button>
                                <button className={styles.closeBtn} onClick={() => setSelectedFile(null)}>
                                    <X size={20} />
                                </button>
                            </div>
                        </div>
                        <div className={styles.previewContent}>
                            {selectedFile.content ? (
                                <div className={styles.codePreview}>
                                    {selectedFile.content.split('\n').map((line, i) => (
                                        <div key={i} className={styles.codeLine}>
                                            <span className={styles.lineNumber}>{i + 1}</span>
                                            <span className={styles.lineContent}>{line}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className={styles.emptyState}>
                                    <FileText size={48} className={styles.emptyIcon} />
                                    <h3 className={styles.emptyTitle}>Preview not available</h3>
                                    <p>This file type cannot be previewed.</p>
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
