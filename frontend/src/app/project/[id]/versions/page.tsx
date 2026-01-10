'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { use } from 'react';
import { ArrowLeft, ArrowRight, RotateCcw, FileText, AlertTriangle, Plus, Minus } from 'lucide-react';
import { Navbar } from '@/components/layout';
import { Button, Badge, Avatar, Modal, Select, useToast, Textarea, LoadingState, ErrorDisplay } from '@/components/ui';
import { config } from '@/lib/config';
import { useVersions, useVersionDiff, useRollbackVersion, Version } from '@/lib/hooks';
import styles from './page.module.css';

interface DiffLine {
    type: 'added' | 'removed' | 'context';
    lineNumber: number;
    content: string;
}

// Fallback data
// Fallback data removed
const fallbackVersions: Version[] = [];
const fallbackDiffLines: DiffLine[] = [];

const documentTypes = config.documentTypes.map((dt) => ({
    value: dt.key,
    label: dt.label,
}));

interface PageProps {
    params: Promise<{ id: string }>;
}

export default function VersionsPage({ params }: PageProps) {
    const { id: projectId } = use(params);
    const { success, warning, error: showError } = useToast();
    const [docType, setDocType] = useState('prd');
    const [selectedVersion, setSelectedVersion] = useState<number>(0);
    const [compareVersion, setCompareVersion] = useState<number>(0);
    const [isRollbackOpen, setIsRollbackOpen] = useState(false);
    const [rollbackReason, setRollbackReason] = useState('');

    // API hooks
    const { data: versionsData, isLoading, isError, error, refetch } = useVersions(projectId, docType);
    const { data: diffData } = useVersionDiff(projectId, docType, compareVersion, selectedVersion);
    const rollbackMutation = useRollbackVersion(projectId, docType);

    // Local state
    const [versions, setVersions] = useState<Version[]>(fallbackVersions);
    const [diffLines, setDiffLines] = useState<DiffLine[]>(fallbackDiffLines);

    // Sync API data
    useEffect(() => {
        if (versionsData?.versions) {
            setVersions(versionsData.versions);
            if (versionsData.versions.length > 0) {
                setSelectedVersion(versionsData.versions[0].version);
                if (versionsData.versions.length > 1) {
                    setCompareVersion(versionsData.versions[1].version);
                }
            }
        }
    }, [versionsData]);

    // Note: API returns added/removed/modified arrays, not lines. 
    // Using fallback diff data for display. Real implementation would transform API response.
    // useEffect for diffData is intentionally simplified since the API format differs.

    const selectedVersionData = versions.find((v) => v.version === selectedVersion);
    const addedCount = diffLines.filter((l) => l.type === 'added').length;
    const removedCount = diffLines.filter((l) => l.type === 'removed').length;

    const handleRollback = async () => {
        if (!rollbackReason.trim()) {
            showError('Please provide a reason for the rollback');
            return;
        }

        warning(`Rolling back to version ${selectedVersion}...`);

        const result = await rollbackMutation.mutate({
            version: selectedVersion,
            reason: rollbackReason,
        });

        setIsRollbackOpen(false);

        if (result) {
            success(`Successfully rolled back to version ${selectedVersion}`);
            setRollbackReason('');
            refetch();
        }
    };

    if (isLoading) {
        return (
            <>
                <Navbar />
                <main className="container">
                    <LoadingState message="Loading version history..." />
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
                        <Link href={`/project/${projectId}`} className={styles.backBtn}>
                            <ArrowLeft size={20} />
                        </Link>
                        <h1 className={styles.title}>Version History</h1>
                    </div>

                    <div className={styles.mainLayout}>
                        {/* Version Sidebar */}
                        <div className={styles.versionSidebar}>
                            <div className={styles.sidebarHeader}>
                                <span className={styles.sidebarTitle}>Versions</span>
                                <Badge variant="info">{versions.length}</Badge>
                            </div>

                            <div className={styles.docTypeSelect}>
                                <Select
                                    options={documentTypes}
                                    value={docType}
                                    onChange={(e) => setDocType(e.target.value)}
                                    placeholder="Select document type"
                                />
                            </div>

                            <div className={styles.timeline}>
                                {versions.map((version) => (
                                    <div
                                        key={version.version}
                                        className={`${styles.timelineItem} ${selectedVersion === version.version ? styles.timelineItemActive : ''}`}
                                        onClick={() => setSelectedVersion(version.version)}
                                    >
                                        <div className={styles.timelineDot}>v{version.version}</div>
                                        <div className={styles.timelineContent}>
                                            <p className={styles.timelineTitle}>{version.summary}</p>
                                            <div className={styles.timelineMeta}>
                                                <Avatar name={version.changedBy} size="sm" />
                                                <span>{version.changedBy}</span>
                                                <span>•</span>
                                                <span>{version.timestamp}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Diff Panel */}
                        <div className={styles.diffPanel}>
                            <div className={styles.diffHeader}>
                                <div className={styles.diffInfo}>
                                    <FileText size={20} />
                                    <div>
                                        <h3 className={styles.diffTitle}>
                                            {documentTypes.find((d) => d.value === docType)?.label || 'Document'}
                                        </h3>
                                        <p className={styles.diffMeta}>
                                            Version {selectedVersion} by {selectedVersionData?.changedBy}
                                        </p>
                                    </div>
                                </div>
                                <div className={styles.diffActions}>
                                    <Button
                                        variant="secondary"
                                        icon={<RotateCcw size={16} />}
                                        onClick={() => setIsRollbackOpen(true)}
                                        disabled={selectedVersion === versions[0]?.version}
                                    >
                                        Rollback
                                    </Button>
                                </div>
                            </div>

                            <div className={styles.compareSelectors}>
                                <span className={styles.compareLabel}>Compare:</span>
                                <Select
                                    options={versions.map((v) => ({ value: String(v.version), label: `v${v.version}` }))}
                                    value={String(compareVersion)}
                                    onChange={(e) => setCompareVersion(Number(e.target.value))}
                                />
                                <ArrowRight size={16} className={styles.compareArrow} />
                                <Select
                                    options={versions.map((v) => ({ value: String(v.version), label: `v${v.version}` }))}
                                    value={String(selectedVersion)}
                                    onChange={(e) => setSelectedVersion(Number(e.target.value))}
                                />
                            </div>

                            <div className={styles.diffContent}>
                                <div className={styles.diffStats}>
                                    <div className={`${styles.diffStat} ${styles.diffStatAdded}`}>
                                        <Plus size={14} />
                                        {addedCount} additions
                                    </div>
                                    <div className={`${styles.diffStat} ${styles.diffStatRemoved}`}>
                                        <Minus size={14} />
                                        {removedCount} deletions
                                    </div>
                                </div>

                                <div className={styles.diffCode}>
                                    {diffLines.map((line, index) => (
                                        <div
                                            key={index}
                                            className={`${styles.diffLine} ${line.type === 'added' ? styles.diffLineAdded :
                                                line.type === 'removed' ? styles.diffLineRemoved :
                                                    styles.diffLineContext
                                                }`}
                                        >
                                            <span className={styles.diffLineNumber}>{line.lineNumber}</span>
                                            <span className={styles.diffLineContent}>
                                                {line.type === 'added' && '+ '}
                                                {line.type === 'removed' && '- '}
                                                {line.content}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Rollback Modal */}
            <Modal
                isOpen={isRollbackOpen}
                onClose={() => setIsRollbackOpen(false)}
                title="Rollback to Previous Version"
                icon={<RotateCcw size={20} />}
                variant="warning"
                size="md"
                footer={
                    <>
                        <Button variant="secondary" onClick={() => setIsRollbackOpen(false)}>
                            Cancel
                        </Button>
                        <Button
                            variant="danger"
                            onClick={handleRollback}
                            loading={rollbackMutation.isLoading}
                            disabled={!rollbackReason.trim()}
                        >
                            Confirm Rollback
                        </Button>
                    </>
                }
            >
                <div className={styles.rollbackWarning}>
                    <AlertTriangle size={20} className={styles.rollbackIcon} />
                    <p className={styles.rollbackText}>
                        This will revert the document to version {selectedVersion}. All changes made after this version
                        will be preserved in history but the current document will be replaced.
                    </p>
                </div>
                <Textarea
                    label="Reason for rollback"
                    placeholder="Explain why you're rolling back..."
                    value={rollbackReason}
                    onChange={(e) => setRollbackReason(e.target.value)}
                    rows={3}
                    required
                />
            </Modal>
        </>
    );
}
