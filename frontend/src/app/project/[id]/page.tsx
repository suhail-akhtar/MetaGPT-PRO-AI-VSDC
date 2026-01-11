'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { use } from 'react';
import {
    AlertTriangle,
    TrendingUp,
    ListTodo,
    Bug,
    Zap,
    MessageCircle,
    LayoutGrid,
    Check,
    Code,
    ListTree,
    Lightbulb,
    Pencil,
    ClipboardList,
} from 'lucide-react';
import { Navbar } from '@/components/layout';
import { Button, Card, ErrorDisplay, LoadingState, ProgressBar, Avatar } from '@/components/ui';
import { useProjectMetrics, useBugMetrics, useProjectStatus, useResumeProject, useProjectAgents, useProjectActivity, useProjectArtifacts, useProjectDetails, useDeleteProject, useRestartProject } from '@/lib/hooks';
import styles from './page.module.css';
import { useRouter } from 'next/navigation';

function getActivityIcon(type: string) {
    switch (type) {
        case 'task_complete':
            return { icon: <Check size={14} />, className: styles.activityIconSuccess };
        case 'bug_created':
            return { icon: <Bug size={14} />, className: styles.activityIconDanger };
        case 'message':
            return { icon: <MessageCircle size={14} />, className: styles.activityIconInfo };
        case 'commit':
            return { icon: <Code size={14} />, className: styles.activityIconAccent };
        case 'task_moved':
            return { icon: <ListTree size={14} />, className: styles.activityIconWarning };
        default:
            return { icon: <Check size={14} />, className: styles.activityIconSuccess };
    }
}

interface PageProps {
    params: Promise<{ id: string }>;
}

export default function ProjectDashboard({ params }: PageProps) {
    const { id } = use(params);

    // API hooks
    const { data: metricsData, isLoading: metricsLoading, isError, error, refetch } = useProjectMetrics(id);
    const { data: statusData } = useProjectStatus(id);
    const { mutate: resumeProject, isLoading: isResuming } = useResumeProject(id);
    const { mutate: deleteProject, isLoading: isDeleting } = useDeleteProject(id);
    const { mutate: restartProject, isLoading: isRestarting } = useRestartProject(id);
    const { data: bugMetrics } = useBugMetrics(id);
    const router = useRouter();

    // Handlers
    const handleResume = async () => {
        try { await resumeProject(); refetch(); } catch (e) { console.error("Failed to resume:", e); }
    };

    const handleDelete = async () => {
        if (!confirm("Are you sure you want to delete this project? This action cannot be undone.")) return;
        try {
            await deleteProject();
            router.push('/');
        } catch (e) { console.error("Failed to delete:", e); }
    };

    const handleRestart = async () => {
        if (!confirm("Are you sure you want to restart? Current progress will be archived. Agents will be reset.")) return;
        try {
            await restartProject();
            window.location.reload();
        } catch (e) { console.error("Failed to restart:", e); }
    };

    // Merge API data with fallback
    const [project, setProject] = useState<any>(null);

    useEffect(() => {
        if (metricsData) {
            setProject((prev: any) => ({
                ...prev,
                name: prev?.name || `Project ${id}`, // Name might come from another source or default
                createdAt: 'Recently', // Backend doesn't return created date yet
                currentSprint: metricsData.current_sprint,
                totalSprints: metricsData.total_sprints,
                metrics: {
                    sprintProgress: metricsData.sprint_progress,
                    tasksCompleted: metricsData.tasks_completed,
                    totalTasks: metricsData.total_tasks,
                    openBugs: metricsData.open_bugs,
                    criticalBugs: metricsData.critical_bugs,
                    velocity: metricsData.velocity,
                },
                agents: [], // Agents API needs to be integrated more fully
                recentActivity: [], // History API needs integration
                criticalBugs: [], // Need bug names
                artifacts: [], // Needs API integration
            }));
        }
    }, [metricsData, id]);

    useEffect(() => {
        if (bugMetrics && project) {
            setProject((prev: any) => ({
                ...prev,
                metrics: {
                    ...prev.metrics,
                    openBugs: bugMetrics.open,
                    criticalBugs: bugMetrics.critical,
                },
            }));
        }
    }, [bugMetrics]);

    // Fetch artifacts
    const { data: artifactsData } = useProjectArtifacts(id);
    useEffect(() => {
        if (artifactsData && project) {
            setProject((prev: any) => ({
                ...prev,
                artifacts: artifactsData.artifacts
            }));
        }
    }, [artifactsData]);


    if (metricsLoading || !project) {
        return (
            <>
                <Navbar />
                <main className="container">
                    <LoadingState message="Loading dashboard..." />
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

                    {/* Approval Pause Banner */}
                    {statusData?.approval_required && (
                        <div className={`${styles.alertBanner} ${styles.alertBannerWarning}`}>
                            <div className={styles.alertContent}>
                                <Zap size={24} className={styles.alertIcon} />
                                <div>
                                    <p className={styles.alertTitle}>Approval Required</p>
                                    <p className={styles.alertDescription}>
                                        The AI Team has paused for your review. Please check the Board or Implementation Plan.
                                    </p>
                                </div>
                            </div>
                            <Button
                                onClick={handleResume}
                                loading={isResuming}
                                variant="primary"
                            >
                                Approve & Resume
                            </Button>
                        </div>
                    )}

                    {/* Header */}
                    <div className={styles.header}>
                        <div className={styles.headerLeft}>
                            <h1>{project.name}</h1>
                            <p>
                                Created {project.createdAt} • Sprint {project.currentSprint} of{' '}
                                {project.totalSprints}
                            </p>
                        </div>
                        <div className={styles.headerActions}>
                            <Link href={`/project/${id}/agents`}>
                                <Button variant="secondary" icon={<MessageCircle size={18} />}>
                                    Talk to Agents
                                </Button>
                            </Link>
                            <Link href={`/project/${id}/board`}>
                                <Button icon={<LayoutGrid size={18} />}>Sprint Board</Button>
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Requirements Card */}
                {project.description && (
                    <Card className={styles.requirementsCard}>
                        <h3>Initial Requirements</h3>
                        <p className={styles.requirementsText}>{project.description}</p>
                    </Card>
                )}

                {/* Critical Bugs Alert */}
                {project.metrics.criticalBugs > 0 && (
                    <div className={styles.alertBanner}>
                        <div className={styles.alertContent}>
                            <AlertTriangle size={24} className={styles.alertIcon} />
                            <div>
                                <p className={styles.alertTitle}>
                                    {project.metrics.criticalBugs} Critical Bugs Require Attention
                                </p>
                                <p className={styles.alertDescription}>
                                    {project.criticalBugs.join(', ')}
                                </p>
                            </div>
                        </div>
                        <Link href={`/project/${id}/bugs`}>
                            <button className={styles.alertAction}>View Bugs →</button>
                        </Link>
                    </div>
                )}

                {/* Stats Grid */}
                <div className={styles.statsGrid}>
                    <Card className={styles.statCard}>
                        <div className={styles.statHeader}>
                            <div>
                                <p className={styles.statLabel}>Sprint Progress</p>
                                <p className={styles.statValue}>{project.metrics.sprintProgress}%</p>
                            </div>
                            <div className={`${styles.statIcon} ${styles.statIconPrimary}`}>
                                <TrendingUp size={20} />
                            </div>
                        </div>
                        <ProgressBar value={project.metrics.sprintProgress} size="sm" />
                    </Card>

                    <Card className={styles.statCard}>
                        <div className={styles.statHeader}>
                            <div>
                                <p className={styles.statLabel}>Tasks Completed</p>
                                <p className={styles.statValue}>
                                    {project.metrics.tasksCompleted}/{project.metrics.totalTasks}
                                </p>
                            </div>
                            <div className={`${styles.statIcon} ${styles.statIconSuccess}`}>
                                <ListTodo size={20} />
                            </div>
                        </div>
                        <p className={`${styles.statFooter} ${styles.statPositive}`}>+3 today</p>
                    </Card>

                    <Card className={styles.statCard}>
                        <div className={styles.statHeader}>
                            <div>
                                <p className={styles.statLabel}>Open Bugs</p>
                                <p className={styles.statValue}>{project.metrics.openBugs}</p>
                            </div>
                            <div className={`${styles.statIcon} ${styles.statIconDanger}`}>
                                <Bug size={20} />
                            </div>
                        </div>
                        <p className={`${styles.statFooter} ${styles.statNegative}`}>
                            {project.metrics.criticalBugs} critical
                        </p>
                    </Card>

                    <Card className={styles.statCard}>
                        <div className={styles.statHeader}>
                            <div>
                                <p className={styles.statLabel}>Velocity</p>
                                <p className={styles.statValue}>{project.metrics.velocity} pts</p>
                            </div>
                            <div className={`${styles.statIcon} ${styles.statIconAccent}`}>
                                <Zap size={20} />
                            </div>
                        </div>
                        <p className={`${styles.statFooter} ${styles.statNeutral}`}>per sprint</p>
                    </Card>
                </div>

                {/* Main Content */}
                <div className={styles.mainContent}>
                    {/* Active Agents */}
                    <Card noPadding className={styles.agentsPanel}>
                        <h3 className={styles.sectionTitle}>Active Agents</h3>
                        <div className={styles.agentsList}>
                            {project.agents.map((agent: any) => (
                                <div
                                    key={agent.name}
                                    className={`${styles.agentCard} ${agent.color === 'pink'
                                        ? styles.agentCardPink
                                        : agent.color === 'blue'
                                            ? styles.agentCardBlue
                                            : styles.agentCardGreen
                                        }`}
                                >
                                    <div className={styles.agentInfo}>
                                        <Avatar name={agent.name} size="lg" />
                                        <div>
                                            <p className={styles.agentName}>
                                                {agent.name} - {agent.role}
                                            </p>
                                            <p className={styles.agentStatus}>
                                                <span
                                                    className={`${styles.statusDot} ${agent.status === 'online'
                                                        ? styles.statusDotOnline
                                                        : styles.statusDotBusy
                                                        }`}
                                                />
                                                {agent.currentTask}
                                            </p>
                                        </div>
                                    </div>
                                    <Link href={`/project/${id}/agents`}>
                                        <button
                                            className={`${styles.agentAction} ${agent.color === 'pink'
                                                ? styles.agentActionPink
                                                : agent.color === 'blue'
                                                    ? styles.agentActionBlue
                                                    : styles.agentActionGreen
                                                }`}
                                        >
                                            Message
                                        </button>
                                    </Link>
                                </div>
                            ))}
                        </div>
                    </Card>

                    {/* Recent Activity */}
                    <Card noPadding className={styles.activityPanel}>
                        <h3 className={styles.sectionTitle}>Recent Activity</h3>
                        <div className={styles.activityList}>
                            {project.recentActivity.map((activity: any, index: number) => {
                                const { icon, className } = getActivityIcon(activity.type);
                                return (
                                    <div key={index} className={styles.activityItem}>
                                        <div className={`${styles.activityIcon} ${className}`}>{icon}</div>
                                        <div className={styles.activityContent}>
                                            <p className={styles.activityText}>{activity.text}</p>
                                            <p className={styles.activityTime}>{activity.time}</p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </Card>
                </div>

                {/* Quick Actions (Middle) */}
                <div className={styles.quickActions}>
                    <Card interactive className={styles.actionCard}>
                        <Lightbulb size={24} className={`${styles.actionIcon} ${styles.actionIconYellow}`} />
                        <p className={styles.actionTitle}>Request Feature</p>
                        <p className={styles.actionDescription}>Propose new functionality</p>
                    </Card>

                    <Card interactive className={styles.actionCard}>
                        <Pencil size={24} className={`${styles.actionIcon} ${styles.actionIconBlue}`} />
                        <p className={styles.actionTitle}>Change Request</p>
                        <p className={styles.actionDescription}>Modify existing features</p>
                    </Card>

                    <Link href={`/project/${id}/bugs`}>
                        <Card interactive className={styles.actionCard}>
                            <Bug size={24} className={`${styles.actionIcon} ${styles.actionIconRed}`} />
                            <p className={styles.actionTitle}>Report Bug</p>
                            <p className={styles.actionDescription}>Submit issue manually</p>
                        </Card>
                    </Link>
                </div>

                {/* Artifacts List */}
                <Card className={styles.artifactsPanel} style={{ marginTop: '20px' }}>
                    <h3 className={styles.sectionTitle}>Artifacts</h3>
                    {project.artifacts?.length > 0 ? (
                        <ul className={styles.artifactList}>
                            {project.artifacts.map((art: any) => (
                                <li key={art.path}>
                                    <a href={`/project/${id}/files?path=${art.path}`} className={styles.artifactLink}>
                                        <ClipboardList size={16} /> {art.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className={styles.emptyText}>No artifacts generated yet</p>
                    )}
                </Card>

                {/* Danger Zone */}
                <div className={styles.quickActions} style={{ marginTop: '20px', borderTop: '1px solid #333', paddingTop: '20px' }}>
                    <Card interactive onClick={handleRestart} className={styles.actionCard} style={{ borderColor: '#eab308' }}>
                        <Zap size={24} className={styles.actionIcon} style={{ color: '#eab308' }} />
                        <p className={styles.actionTitle}>Restart Project</p>
                        <p className={styles.actionDescription}>Archive & Start Over</p>
                    </Card>
                    <Card interactive onClick={handleDelete} className={styles.actionCard} style={{ borderColor: '#ef4444' }}>
                        <Bug size={24} className={styles.actionIcon} style={{ color: '#ef4444' }} />
                        <p className={styles.actionTitle}>Delete Project</p>
                        <p className={styles.actionDescription}>Permanently Remove</p>
                    </Card>
                </div>
            </main>
        </>
    );
}
