// Project Types
export interface Project {
    id: string;
    name: string;
    description: string;
    status: 'planning' | 'active' | 'completed' | 'paused';
    currentSprint: number;
    totalSprints: number;
    progress: number;
    tasksCompleted: number;
    totalTasks: number;
    bugsCount: number;
    criticalBugsCount: number;
    agents: Agent[];
    createdAt: string;
    updatedAt: string;
}

// Agent Types
export interface Agent {
    id: string;
    name: string;
    role: 'ProductManager' | 'Architect' | 'Engineer' | 'QA' | 'Reviewer';
    avatar?: string;
    color: string;
    status: 'online' | 'busy' | 'idle' | 'offline';
    currentTask?: string;
}

// Conversation Types
export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    agentName?: string;
}

export interface ConversationSession {
    id: string;
    messages: Message[];
    status: 'active' | 'pending_approval' | 'approved' | 'closed';
    enhancedRequirements?: EnhancedPRD;
}

export interface EnhancedPRD {
    project_name: string;
    vision: string;
    user_stories: UserStory[];
    technical_requirements: string[];
    success_metrics: string[];
    clarifying_questions?: string[];
}

export interface UserStory {
    id: string;
    story: string;
    priority: 'high' | 'medium' | 'low';
    points?: number;
}

// Sprint/Backlog Types
export interface Sprint {
    number: number;
    name: string;
    status: 'planned' | 'active' | 'completed';
    startDate?: string;
    endDate?: string;
    goals: string[];
    tasks: string[];
    progress: number;
}

export interface Task {
    id: string;
    title: string;
    description?: string;
    status: TaskStatus;
    storyPoints: number;
    assignee?: string;
    epic?: string;
    priority: 'p0' | 'p1' | 'p2' | 'p3';
    isBug?: boolean;
    createdAt: string;
    updatedAt: string;
}

export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'testing' | 'done' | 'blocked';

export interface KanbanBoard {
    todo: Task[];
    in_progress: Task[];
    review: Task[];
    testing: Task[];
    done: Task[];
    blocked: Task[];
}

// Bug Types
export interface Bug {
    id: string;
    title: string;
    description: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    status: BugStatus;
    priority: 'p0' | 'p1' | 'p2' | 'p3';
    filePath?: string;
    errorTrace?: string;
    assignedTo?: string;
    source: 'manual' | 'test_failure' | 'agent';
    createdBy: string;
    createdAt: string;
    updatedAt: string;
}

export type BugStatus = 'open' | 'in_progress' | 'fixed' | 'verified' | 'closed' | 'wont_fix';

export interface BugMetrics {
    total: number;
    open: number;
    critical: number;
    fixedThisSprint: number;
    avgFixTimeHours: number;
}

// Agent Collaboration Types
export interface ConversationThread {
    id: string;
    topic: string;
    participants: string[];
    messages: AgentMessage[];
    status: 'active' | 'resolved' | 'pending';
    createdAt: string;
}

export interface AgentMessage {
    id: string;
    from: string;
    to: string;
    content: string;
    type: 'question' | 'response' | 'approval_request' | 'approval_response' | 'update';
    timestamp: string;
    attachments?: Attachment[];
    requiresApproval?: boolean;
}

export interface Attachment {
    name: string;
    type: string;
    url?: string;
}

export interface ApprovalRequest {
    id: string;
    messageId: string;
    from: string;
    to: string;
    description: string;
    status: 'pending' | 'approved' | 'rejected';
    createdAt: string;
}

// Version Types
export interface DocumentVersion {
    version: number;
    content: string | Record<string, unknown>;
    changedBy: string;
    changeReason?: string;
    timestamp: string;
    changesSummary?: string;
}

export interface Diff {
    added: string[];
    removed: string[];
    modified: string[];
    rawDiff?: string;
    isJsonDiff: boolean;
}

export interface VersionHistory {
    documentId: string;
    documentType: string;
    versions: DocumentVersion[];
    currentVersion: number;
}

// Activity Types
export interface ActivityItem {
    id: string;
    type: 'task_complete' | 'bug_created' | 'approval_request' | 'commit' | 'task_moved' | 'message';
    description: string;
    actor: string;
    timestamp: string;
    metadata?: Record<string, unknown>;
}

// Metrics Types
export interface ProjectMetrics {
    sprintProgress: number;
    tasksCompleted: number;
    totalTasks: number;
    openBugs: number;
    criticalBugs: number;
    velocity: number;
    currentSprint: number;
    totalSprints: number;
}

// API Response Types
export interface ApiResponse<T> {
    data?: T;
    error?: string;
    status: number;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    pageSize: number;
    hasMore: boolean;
}
