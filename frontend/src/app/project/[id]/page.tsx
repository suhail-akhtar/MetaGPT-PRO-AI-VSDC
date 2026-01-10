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
import { Button, Card, Avatar, ProgressBar, LoadingState, ErrorDisplay } from '@/components/ui';
import { useProjectMetrics, useBugMetrics } from '@/lib/hooks';
import styles from './page.module.css';

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
    const { data: bugMetrics } = useBugMetrics(id);

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

                    {/* Quick Actions */}
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

                        <Link href={`/project/${id}/versions`}>
                            <Card interactive className={styles.actionCard}>
                                <ClipboardList size={24} className={`${styles.actionIcon} ${styles.actionIconPurple}`} />
                                <p className={styles.actionTitle}>Implementation Plan</p>
                                <p className={styles.actionDescription}>View development roadmap</p>
                            </Card>
                        </Link>
                    </div>
                </div>
            </main>
        </>
    );
}
