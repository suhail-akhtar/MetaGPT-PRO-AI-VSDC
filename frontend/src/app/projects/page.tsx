'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus, ListTodo, Bug, FolderKanban } from 'lucide-react';
import { Navbar } from '@/components/layout';
import { Button, Card, CardBody, Badge, Avatar, ProgressBar, LoadingState, ErrorDisplay } from '@/components/ui';
import { useProjects, Project } from '@/lib/hooks';
import styles from './page.module.css';

function getProgressVariant(progress: number) {
    if (progress === 100) return 'success';
    if (progress >= 60) return 'primary';
    if (progress >= 30) return 'warning';
    return 'primary';
}

function getStatusBadgeVariant(status: Project['status']) {
    switch (status) {
        case 'active': return 'success';
        case 'completed': return 'info';
        case 'planning': return 'warning';
        case 'paused': return 'default';
        default: return 'default';
    }
}

function getStatusLabel(status: Project['status']) {
    switch (status) {
        case 'active': return 'Active';
        case 'completed': return 'Completed';
        case 'planning': return 'Planning';
        case 'paused': return 'Paused';
        default: return status;
    }
}

export default function ProjectsPage() {
    // Fetch projects from API
    const { data: apiProjects, isLoading, isError, error, refetch } = useProjects();
    const [projects, setProjects] = useState<Project[]>([]);

    // Sync API data
    useEffect(() => {
        if (apiProjects) {
            setProjects(apiProjects);
        }
    }, [apiProjects]);

    if (isLoading) {
        return (
            <>
                <Navbar />
                <main className="container">
                    <LoadingState message="Loading projects..." />
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

                    <div className={styles.header}>
                        <h1 className={styles.title}>Your Projects</h1>
                        <Link href="/new">
                            <Button icon={<Plus size={18} />}>New Project</Button>
                        </Link>
                    </div>

                    <div className={styles.grid}>
                        {projects.map((project) => (
                            <Link key={project.id} href={`/project/${project.id}`}>
                                <Card interactive className={styles.projectCard}>
                                    <CardBody>
                                        <div className={styles.cardHeader}>
                                            <Badge variant={getStatusBadgeVariant(project.status)}>
                                                {getStatusLabel(project.status)}
                                            </Badge>
                                            <span className="text-sm text-secondary">
                                                Sprint {project.currentSprint || 0}/{project.totalSprints || 0}
                                            </span>
                                        </div>

                                        <h3 className={styles.cardTitle}>{project.name}</h3>
                                        <p className={styles.cardDescription}>{project.description}</p>

                                        <div className={styles.cardMeta}>
                                            <div className={styles.agents}>
                                                {project.agents.slice(0, 3).map((agent) => (
                                                    <Avatar key={agent} name={agent} size="sm" />
                                                ))}
                                                {project.agents.length > 3 && (
                                                    <span className={styles.moreAgents}>+{project.agents.length - 3}</span>
                                                )}
                                            </div>
                                            <span className={styles.progress}>
                                                {project.progress}% Complete
                                            </span>
                                        </div>

                                        <ProgressBar
                                            value={project.progress}
                                            variant={getProgressVariant(project.progress)}
                                            size="sm"
                                            className={styles.progressBar}
                                        />

                                        <div className={styles.cardFooter}>
                                            <span className={styles.stat}>
                                                <ListTodo size={14} />
                                                {project.taskCount} tasks
                                            </span>
                                            {project.bugCount > 0 && (
                                                <span className={styles.stat}>
                                                    <Bug size={14} className={styles.bugIcon} />
                                                    {project.bugCount} bugs
                                                </span>
                                            )}
                                        </div>
                                    </CardBody>
                                </Card>
                            </Link>
                        ))}
                    </div>

                    {projects.length === 0 && (
                        <div className={styles.emptyState}>
                            <FolderKanban size={48} className={styles.emptyIcon} />
                            <h2 className={styles.emptyTitle}>No projects yet</h2>
                            <p className={styles.emptyDescription}>
                                Start your first AI-powered software project
                            </p>
                            <Link href="/new">
                                <Button icon={<Plus size={18} />}>Create Project</Button>
                            </Link>
                        </div>
                    )}
                </div>
            </main>
        </>
    );
}
