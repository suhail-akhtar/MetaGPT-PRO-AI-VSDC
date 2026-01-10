'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { use } from 'react';
import { ArrowLeft, Bug, AlertTriangle, CheckCircle, Clock, Plus, Search, AlertCircle } from 'lucide-react';
import { Navbar } from '@/components/layout';
import { Button, Card, Badge, Avatar, Modal, Input, Textarea, Select, useToast, LoadingState, ErrorDisplay } from '@/components/ui';
import { config } from '@/lib/config';
import { useBugs, useBugMetrics, useReportBug, useUpdateBugStatus, useBugsStream, Bug as BugType } from '@/lib/hooks';
import { bugReportSchema, validate } from '@/lib/validation';
import styles from './page.module.css';

// Fallback mock data
// Mock data removed


type FilterStatus = 'all' | 'open' | 'in_progress' | 'fixed' | 'verified';

interface PageProps {
    params: Promise<{ id: string }>;
}

export default function BugTrackerPage({ params }: PageProps) {
    const { id: projectId } = use(params);
    const { success, error: showError } = useToast();

    // API hooks
    const { data: bugsData, isLoading, isError, error, refetch } = useBugs(projectId);
    const { data: metricsData } = useBugMetrics(projectId);
    const reportBugMutation = useReportBug(projectId);
    const updateStatusMutation = useUpdateBugStatus(projectId);

    // WebSocket for real-time bug updates
    const { isConnected } = useBugsStream(projectId, (message) => {
        if (message.type === 'bug_reported' || message.type === 'bug_updated') {
            refetch(); // Refresh bugs list
        }
    });

    // Local state
    const [bugs, setBugs] = useState<BugType[]>([]);
    const [filter, setFilter] = useState<FilterStatus>('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedBug, setSelectedBug] = useState<BugType | null>(null);
    const [isReportModalOpen, setIsReportModalOpen] = useState(false);

    // Form state
    const [newBugTitle, setNewBugTitle] = useState('');
    const [newBugDescription, setNewBugDescription] = useState('');
    const [newBugSeverity, setNewBugSeverity] = useState('');
    const [newBugFilePath, setNewBugFilePath] = useState('');
    const [newBugErrorTrace, setNewBugErrorTrace] = useState('');

    // Sync API data
    useEffect(() => {
        if (bugsData?.bugs) {
            setBugs(bugsData.bugs);
        }
    }, [bugsData]);

    const filteredBugs = bugs.filter((bug) => {
        const matchesFilter = filter === 'all' || bug.status === filter;
        const matchesSearch = bug.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            bug.id.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    const stats = {
        total: metricsData?.total ?? bugs.length,
        critical: metricsData?.critical ?? bugs.filter((b) => b.severity === 'critical').length,
        open: metricsData?.open ?? bugs.filter((b) => b.status === 'open' || b.status === 'in_progress').length,
        fixed: bugsData?.bugs?.filter((b) => b.status === 'fixed' || b.status === 'verified' || b.status === 'closed').length ??
            bugs.filter((b) => b.status === 'fixed' || b.status === 'verified' || b.status === 'closed').length,
    };

    const severityConfig = config.severities;

    const handleReportBug = async () => {
        // Validate with Zod
        const validation = validate(bugReportSchema, {
            title: newBugTitle,
            description: newBugDescription,
            severity: newBugSeverity || undefined,
            filePath: newBugFilePath || undefined,
            errorTrace: newBugErrorTrace || undefined,
        });

        if (!validation.success) {
            const firstError = Object.values(validation.errors || {})[0];
            showError(firstError || 'Please fill in all required fields correctly');
            return;
        }

        const result = await reportBugMutation.mutate({
            title: validation.data!.title,
            description: validation.data!.description,
            severity: validation.data!.severity,
            file_path: validation.data!.filePath || undefined,
            error_trace: validation.data!.errorTrace || undefined,
        });

        if (result) {
            success('Bug reported successfully');
            setIsReportModalOpen(false);
            // Reset form
            setNewBugTitle('');
            setNewBugDescription('');
            setNewBugSeverity('');
            setNewBugFilePath('');
            setNewBugErrorTrace('');
            refetch();
        }
    };

    const handleMarkAsFixed = async () => {
        if (!selectedBug) return;

        const result = await updateStatusMutation.mutate({
            bugId: selectedBug.id,
            status: 'fixed',
        });

        if (result) {
            success('Bug marked as fixed');
            setSelectedBug(null);
            refetch();
        }
    };

    if (isLoading) {
        return (
            <>
                <Navbar />
                <main className="container">
                    <LoadingState message="Loading bugs..." />
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
                            <h1 className={styles.title}>Bug Tracker</h1>
                        </div>
                        <div className={styles.headerRight}>
                            <Button icon={<Plus size={16} />} onClick={() => setIsReportModalOpen(true)}>
                                Report Bug
                            </Button>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className={styles.statsGrid}>
                        <Card className={styles.statCard}>
                            <div className={styles.statHeader}>
                                <div>
                                    <p className={styles.statLabel}>Total Bugs</p>
                                    <p className={styles.statValue}>{stats.total}</p>
                                </div>
                                <div className={`${styles.statIcon} ${styles.statIconInfo}`}>
                                    <Bug size={20} />
                                </div>
                            </div>
                        </Card>
                        <Card className={styles.statCard}>
                            <div className={styles.statHeader}>
                                <div>
                                    <p className={styles.statLabel}>Critical</p>
                                    <p className={styles.statValue}>{stats.critical}</p>
                                </div>
                                <div className={`${styles.statIcon} ${styles.statIconDanger}`}>
                                    <AlertTriangle size={20} />
                                </div>
                            </div>
                        </Card>
                        <Card className={styles.statCard}>
                            <div className={styles.statHeader}>
                                <div>
                                    <p className={styles.statLabel}>Open</p>
                                    <p className={styles.statValue}>{stats.open}</p>
                                </div>
                                <div className={`${styles.statIcon} ${styles.statIconWarning}`}>
                                    <Clock size={20} />
                                </div>
                            </div>
                        </Card>
                        <Card className={styles.statCard}>
                            <div className={styles.statHeader}>
                                <div>
                                    <p className={styles.statLabel}>Fixed</p>
                                    <p className={styles.statValue}>{stats.fixed}</p>
                                </div>
                                <div className={`${styles.statIcon} ${styles.statIconSuccess}`}>
                                    <CheckCircle size={20} />
                                </div>
                            </div>
                        </Card>
                    </div>

                    {/* Filters */}
                    <div className={styles.filters}>
                        <div className={styles.filterGroup}>
                            {(['all', 'open', 'in_progress', 'fixed', 'verified'] as FilterStatus[]).map((f) => (
                                <button
                                    key={f}
                                    className={`${styles.filterBtn} ${filter === f ? styles.filterBtnActive : ''}`}
                                    onClick={() => setFilter(f)}
                                >
                                    {f === 'all' ? 'All' : f === 'in_progress' ? 'In Progress' : f.charAt(0).toUpperCase() + f.slice(1)}
                                </button>
                            ))}
                        </div>
                        <div className={styles.searchInput}>
                            <Input
                                placeholder="Search bugs..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                leftIcon={<Search size={16} />}
                            />
                        </div>
                    </div>

                    {/* Bug Table */}
                    <div className={styles.tableContainer}>
                        {filteredBugs.length === 0 ? (
                            <div className={styles.emptyState}>
                                <Bug size={48} className={styles.emptyIcon} />
                                <h3 className={styles.emptyTitle}>No bugs found</h3>
                                <p>Try adjusting your filters or search query.</p>
                            </div>
                        ) : (
                            <table className={styles.table}>
                                <thead>
                                    <tr>
                                        <th>Bug</th>
                                        <th>Severity</th>
                                        <th>Status</th>
                                        <th>Assignee</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredBugs.map((bug) => (
                                        <tr key={bug.id} onClick={() => setSelectedBug(bug)}>
                                            <td>
                                                <p className={styles.bugTitle}>{bug.title}</p>
                                                <p className={styles.bugId}>{bug.id}</p>
                                            </td>
                                            <td>
                                                <div className={styles.severityCell}>
                                                    <span className={`${styles.severityDot} ${styles[`severity${bug.severity.charAt(0).toUpperCase() + bug.severity.slice(1)}`]}`} />
                                                    {severityConfig[bug.severity].label}
                                                </div>
                                            </td>
                                            <td>
                                                <Badge variant={config.statuses.bug[bug.status].color as 'danger' | 'primary' | 'success' | 'info' | 'default'}>
                                                    {config.statuses.bug[bug.status].label}
                                                </Badge>
                                            </td>
                                            <td>
                                                {bug.assignee ? (
                                                    <Avatar name={bug.assignee} size="sm" />
                                                ) : (
                                                    <span className={styles.timeAgo}>Unassigned</span>
                                                )}
                                            </td>
                                            <td className={styles.timeAgo}>{bug.createdAt}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            </main>

            {/* Bug Detail Modal */}
            <Modal
                isOpen={!!selectedBug}
                onClose={() => setSelectedBug(null)}
                title={selectedBug?.title}
                description={selectedBug?.id}
                icon={<Bug size={20} />}
                variant={selectedBug?.severity === 'critical' ? 'danger' : 'default'}
                size="lg"
                footer={
                    <>
                        <Button variant="secondary" onClick={() => setSelectedBug(null)}>
                            Close
                        </Button>
                        <Button
                            variant="success"
                            onClick={handleMarkAsFixed}
                            loading={updateStatusMutation.isLoading}
                            disabled={selectedBug?.status === 'fixed' || selectedBug?.status === 'verified'}
                        >
                            Mark as Fixed
                        </Button>
                    </>
                }
            >
                {selectedBug && (
                    <div className={styles.modalGrid}>
                        <div>
                            <div className={styles.modalSection}>
                                <h4 className={styles.modalSectionTitle}>Description</h4>
                                <p className={styles.modalContent}>{selectedBug.description}</p>
                            </div>
                            {selectedBug.errorTrace && (
                                <div className={styles.modalSection}>
                                    <h4 className={styles.modalSectionTitle}>Error Trace</h4>
                                    <pre className={styles.codeBlock}>{selectedBug.errorTrace}</pre>
                                </div>
                            )}
                        </div>
                        <div>
                            <div className={styles.metaItem}>
                                <span className={styles.metaLabel}>Severity</span>
                                <Badge variant={severityConfig[selectedBug.severity].color as 'danger' | 'warning' | 'info' | 'success'}>
                                    {severityConfig[selectedBug.severity].label}
                                </Badge>
                            </div>
                            <div className={styles.metaItem}>
                                <span className={styles.metaLabel}>Status</span>
                                <Badge variant={config.statuses.bug[selectedBug.status].color as 'danger' | 'primary' | 'success' | 'info' | 'default'}>
                                    {config.statuses.bug[selectedBug.status].label}
                                </Badge>
                            </div>
                            <div className={styles.metaItem}>
                                <span className={styles.metaLabel}>Assignee</span>
                                <span className={styles.metaValue}>{selectedBug.assignee || 'Unassigned'}</span>
                            </div>
                            <div className={styles.metaItem}>
                                <span className={styles.metaLabel}>Created By</span>
                                <span className={styles.metaValue}>{selectedBug.createdBy}</span>
                            </div>
                            {selectedBug.filePath && (
                                <div className={styles.metaItem}>
                                    <span className={styles.metaLabel}>File</span>
                                    <span className={styles.metaValue} style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
                                        {selectedBug.filePath}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </Modal>

            {/* Report Bug Modal */}
            <Modal
                isOpen={isReportModalOpen}
                onClose={() => setIsReportModalOpen(false)}
                title="Report a Bug"
                icon={<AlertCircle size={20} />}
                size="md"
                footer={
                    <>
                        <Button variant="secondary" onClick={() => setIsReportModalOpen(false)}>
                            Cancel
                        </Button>
                        <Button
                            onClick={handleReportBug}
                            loading={reportBugMutation.isLoading}
                            disabled={!newBugTitle || !newBugDescription || !newBugSeverity}
                        >
                            Submit Bug
                        </Button>
                    </>
                }
            >
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                    <Input
                        label="Bug Title"
                        placeholder="Brief description of the issue"
                        required
                        value={newBugTitle}
                        onChange={(e) => setNewBugTitle(e.target.value)}
                    />
                    <Textarea
                        label="Description"
                        placeholder="Detailed description of the bug..."
                        rows={4}
                        required
                        value={newBugDescription}
                        onChange={(e) => setNewBugDescription(e.target.value)}
                    />
                    <Select
                        label="Severity"
                        required
                        value={newBugSeverity}
                        onChange={(e) => setNewBugSeverity(e.target.value)}
                        options={[
                            { value: 'critical', label: 'Critical - System down or data loss' },
                            { value: 'high', label: 'High - Major feature broken' },
                            { value: 'medium', label: 'Medium - Feature works with issues' },
                            { value: 'low', label: 'Low - Minor cosmetic issue' },
                        ]}
                        placeholder="Select severity..."
                    />
                    <Input
                        label="File Path"
                        placeholder="src/components/..."
                        optional
                        value={newBugFilePath}
                        onChange={(e) => setNewBugFilePath(e.target.value)}
                    />
                    <Textarea
                        label="Error Trace"
                        placeholder="Paste any error messages or stack traces..."
                        rows={3}
                        optional
                        value={newBugErrorTrace}
                        onChange={(e) => setNewBugErrorTrace(e.target.value)}
                    />
                </div>
            </Modal>
        </>
    );
}
