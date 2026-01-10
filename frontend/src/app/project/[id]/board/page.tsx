'use client';

import { useState, useCallback, useEffect } from 'react';
import Link from 'next/link';
import { use } from 'react';
import { ArrowLeft, Target, CheckCircle, Clock, AlertTriangle, Bug, Zap, Filter, Plus } from 'lucide-react';
import {
    DndContext,
    DragOverlay,
    closestCorners,
    PointerSensor,
    useSensor,
    useSensors,
    DragStartEvent,
    DragEndEvent,
} from '@dnd-kit/core';
import { SortableContext, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Navbar } from '@/components/layout';
import { Button, Badge, Avatar, useToast, LoadingState, ErrorDisplay } from '@/components/ui';
import { config } from '@/lib/config';
import { useBoard, useMoveTask, useBoardStream, BoardTask, BoardData } from '@/lib/hooks';
import styles from './page.module.css';

type ColumnId = 'todo' | 'in_progress' | 'review' | 'testing' | 'done' | 'blocked';

const columns: { id: ColumnId; label: string }[] = [
    { id: 'todo', label: 'To Do' },
    { id: 'in_progress', label: 'In Progress' },
    { id: 'review', label: 'Review' },
    { id: 'testing', label: 'Testing' },
    { id: 'done', label: 'Done' },
];

// Fallback mock data when API is unavailable
// Fallback mock data removed
const fallbackTasks: BoardData = {
    todo: [],
    in_progress: [],
    review: [],
    testing: [],
    done: [],
    blocked: [],
};

function TaskCard({ task, isDragging = false }: { task: BoardTask; isDragging?: boolean }) {
    const priorityConfig = config.priorities[task.priority];

    return (
        <div className={`${styles.taskCard} ${isDragging ? styles.taskCardDragging : ''}`}>
            <div className={styles.taskHeader}>
                <span className={styles.taskId}>{task.id}</span>
                <Badge variant={priorityConfig.color as 'danger' | 'warning' | 'info' | 'success'}>
                    {priorityConfig.label}
                </Badge>
            </div>
            <p className={styles.taskTitle}>{task.title}</p>
            <div className={styles.taskMeta}>
                <div className={styles.taskTags}>
                    <span className={styles.taskPoints}>
                        <Zap size={12} />
                        {task.storyPoints} pts
                    </span>
                    {task.isBug && (
                        <span className={styles.bugIndicator}>
                            <Bug size={12} />
                            Bug
                        </span>
                    )}
                </div>
                {task.assignee && <Avatar name={task.assignee} size="sm" />}
            </div>
        </div>
    );
}

function SortableTaskCard({ task }: { task: BoardTask }) {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: task.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
    };

    return (
        <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
            <TaskCard task={task} isDragging={isDragging} />
        </div>
    );
}

interface PageProps {
    params: Promise<{ id: string }>;
}

export default function SprintBoardPage({ params }: PageProps) {
    const { id: projectId } = use(params);
    const { success, error: showError } = useToast();

    // Fetch board data from API
    const { data: boardData, isLoading, isError, error, refetch, setData } = useBoard(projectId);
    const moveTaskMutation = useMoveTask(projectId);

    // WebSocket for real-time updates
    const { isConnected } = useBoardStream(projectId, (message) => {
        // Handle real-time board updates
        if (message.type === 'task_moved' || message.type === 'task_updated') {
            refetch(); // Refresh board data
        }
        if (message.type === 'task_created') {
            success('New task added to board');
            refetch();
        }
    });

    // Local state for optimistic updates
    const [tasks, setTasks] = useState<BoardData>(fallbackTasks);
    const [activeTask, setActiveTask] = useState<BoardTask | null>(null);

    // Sync API data to local state
    useEffect(() => {
        if (boardData) {
            setTasks(boardData);
        }
    }, [boardData]);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        })
    );

    const findColumnForTask = (taskId: string): ColumnId | null => {
        for (const [columnId, columnTasks] of Object.entries(tasks)) {
            if (columnTasks.find((t: BoardTask) => t.id === taskId)) {
                return columnId as ColumnId;
            }
        }
        return null;
    };

    const handleDragStart = (event: DragStartEvent) => {
        const { active } = event;
        const sourceColumn = findColumnForTask(active.id as string);
        if (sourceColumn) {
            const task = tasks[sourceColumn].find((t: BoardTask) => t.id === active.id);
            setActiveTask(task || null);
        }
    };

    const handleDragEnd = useCallback(async (event: DragEndEvent) => {
        const { active, over } = event;
        setActiveTask(null);

        if (!over) return;

        const sourceColumn = findColumnForTask(active.id as string);
        const overColumn = over.id as ColumnId;

        if (!sourceColumn || !columns.find((c) => c.id === overColumn)) return;
        if (sourceColumn === overColumn) return;

        const task = tasks[sourceColumn].find((t: BoardTask) => t.id === active.id);
        if (!task) return;

        // Optimistic update - update UI immediately
        setTasks((prev) => ({
            ...prev,
            [sourceColumn]: prev[sourceColumn].filter((t: BoardTask) => t.id !== active.id),
            [overColumn]: [...prev[overColumn], { ...task, status: overColumn }],
        }));

        const columnLabel = columns.find((c) => c.id === overColumn)?.label;
        success(`Moved task to ${columnLabel}`);

        // Call API in background
        const result = await moveTaskMutation.mutate({ taskId: active.id as string, newStatus: overColumn });

        if (!result) {
            // Rollback on failure
            setTasks((prev) => ({
                ...prev,
                [overColumn]: prev[overColumn].filter((t: BoardTask) => t.id !== active.id),
                [sourceColumn]: [...prev[sourceColumn], task],
            }));
            showError('Failed to move task. Please try again.');
        }
    }, [tasks, success, showError, moveTaskMutation]);

    const totalPoints = Object.values(tasks).flat().reduce((sum, t) => sum + t.storyPoints, 0);
    const donePoints = tasks.done.reduce((sum, t) => sum + t.storyPoints, 0);
    const inProgressCount = tasks.in_progress.length + tasks.review.length + tasks.testing.length;
    const blockedCount = tasks.blocked.length;

    if (isLoading) {
        return (
            <>
                <Navbar />
                <main className="container">
                    <LoadingState message="Loading sprint board..." />
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
                            className={styles.errorBanner}
                        />
                    )}

                    {/* Header */}
                    <div className={styles.header}>
                        <div className={styles.headerLeft}>
                            <Link href={`/project/${projectId}`} className={styles.backBtn}>
                                <ArrowLeft size={20} />
                            </Link>
                            <div>
                                <h1 className={styles.title}>Sprint Board</h1>
                                <p className={styles.subtitle}>Sprint 2 • E-commerce Platform</p>
                            </div>
                        </div>
                        <div className={styles.headerRight}>
                            <Button variant="secondary" icon={<Filter size={16} />}>
                                Filter
                            </Button>
                            <Button icon={<Plus size={16} />}>Add Task</Button>
                        </div>
                    </div>

                    {/* Sprint Stats */}
                    <div className={styles.sprintStats}>
                        <div className={styles.statItem}>
                            <div className={`${styles.statIcon} ${styles.statIconPrimary}`}>
                                <Target size={18} />
                            </div>
                            <div className={styles.statContent}>
                                <span className={styles.statValue}>{donePoints}/{totalPoints}</span>
                                <span className={styles.statLabel}>Story Points</span>
                            </div>
                        </div>
                        <div className={styles.statItem}>
                            <div className={`${styles.statIcon} ${styles.statIconSuccess}`}>
                                <CheckCircle size={18} />
                            </div>
                            <div className={styles.statContent}>
                                <span className={styles.statValue}>{tasks.done.length}</span>
                                <span className={styles.statLabel}>Completed</span>
                            </div>
                        </div>
                        <div className={styles.statItem}>
                            <div className={`${styles.statIcon} ${styles.statIconWarning}`}>
                                <Clock size={18} />
                            </div>
                            <div className={styles.statContent}>
                                <span className={styles.statValue}>{inProgressCount}</span>
                                <span className={styles.statLabel}>In Progress</span>
                            </div>
                        </div>
                        {blockedCount > 0 && (
                            <div className={styles.statItem}>
                                <div className={`${styles.statIcon} ${styles.statIconDanger}`}>
                                    <AlertTriangle size={18} />
                                </div>
                                <div className={styles.statContent}>
                                    <span className={styles.statValue}>{blockedCount}</span>
                                    <span className={styles.statLabel}>Blocked</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Kanban Board */}
                    <DndContext
                        sensors={sensors}
                        collisionDetection={closestCorners}
                        onDragStart={handleDragStart}
                        onDragEnd={handleDragEnd}
                    >
                        <div className={styles.board}>
                            {columns.map((column) => (
                                <div key={column.id} className={styles.column}>
                                    <div className={styles.columnHeader}>
                                        <span className={styles.columnTitle}>
                                            <span className={`${styles.columnDot} ${styles[`dot${column.id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('')}`] || styles.dotTodo}`} />
                                            {column.label}
                                        </span>
                                        <span className={styles.columnCount}>{tasks[column.id].length}</span>
                                    </div>
                                    <SortableContext
                                        id={column.id}
                                        items={tasks[column.id].map((t: BoardTask) => t.id)}
                                        strategy={verticalListSortingStrategy}
                                    >
                                        <div className={styles.columnBody}>
                                            {tasks[column.id].length === 0 ? (
                                                <div className={styles.columnEmpty}>No tasks</div>
                                            ) : (
                                                tasks[column.id].map((task: BoardTask) => (
                                                    <SortableTaskCard key={task.id} task={task} />
                                                ))
                                            )}
                                        </div>
                                    </SortableContext>
                                </div>
                            ))}
                        </div>
                        <DragOverlay>
                            {activeTask && (
                                <div className={styles.dragOverlay}>
                                    <TaskCard task={activeTask} />
                                </div>
                            )}
                        </DragOverlay>
                    </DndContext>
                </div>
            </main>
        </>
    );
}
