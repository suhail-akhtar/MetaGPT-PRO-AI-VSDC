'use client';

import { useState, useRef, useEffect, FormEvent } from 'react';
import Link from 'next/link';
import { use } from 'react';
import { ArrowLeft, Send, Clock, MessageCircle, AlertTriangle, Check, X, Users } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Navbar } from '@/components/layout';
import { Button, Avatar, Badge, Textarea, useToast, EmptyState, LoadingState, ErrorDisplay } from '@/components/ui';
import { config } from '@/lib/config';
import { useAgentConversations, useAgentThread, usePendingApprovals, useSendAgentMessage, useApproveRequest, useAgentStream, AgentThread, AgentMessage } from '@/lib/hooks';
import styles from './page.module.css';

interface Thread {
    id: string;
    topic: string;
    participants: string[];
    status: 'active' | 'resolved' | 'pending';
    lastMessage?: string;
    messages: AgentMessage[];
}



const agentDescriptions: Record<string, { role: string; description: string }> = {
    Alice: {
        role: 'Product Manager',
        description: config.agents.defaultMessages.ProductManager,
    },
    Bob: {
        role: 'Architect',
        description: config.agents.defaultMessages.Architect,
    },
    Alex: {
        role: 'Engineer',
        description: config.agents.defaultMessages.Engineer,
    },
};

interface PageProps {
    params: Promise<{ id: string }>;
}

export default function AgentsPage({ params }: PageProps) {
    const { id: projectId } = use(params);
    const { success, info, error: showError } = useToast();

    // API hooks
    const { data: conversationsData, isLoading, isError, error, refetch } = useAgentConversations();
    const { data: approvalsData } = usePendingApprovals();
    const sendMessageMutation = useSendAgentMessage();
    const approveRequestMutation = useApproveRequest();

    // WebSocket for real-time agent updates
    const { isConnected } = useAgentStream((message) => {
        if (message.type === 'agent_message' || message.type === 'approval_request') {
            refetch(); // Refresh conversations
            if (message.type === 'agent_message') {
                info('New message from agent');
            }
        }
    });

    // Local state
    const [threads, setThreads] = useState<Thread[]>([]);
    const [selectedThreadId, setSelectedThreadId] = useState<string>('');
    const [inputValue, setInputValue] = useState('');
    const [isSending, setIsSending] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Sync API data
    useEffect(() => {
        if (conversationsData?.threads) {
            // Transform API data to local format
            setThreads(conversationsData.threads.map((t: AgentThread) => ({
                ...t,
                lastMessage: 'Now',
                messages: [],
            })));
            if (conversationsData.threads.length > 0 && !selectedThreadId) {
                setSelectedThreadId(conversationsData.threads[0].id);
            }
        }
    }, [conversationsData, selectedThreadId]);

    const selectedThread = threads.find((t) => t.id === selectedThreadId);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [selectedThread?.messages]);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!inputValue.trim() || isSending || !selectedThread) return;

        setIsSending(true);

        // Optimistic update
        const newMessage: AgentMessage = {
            id: `msg-${Date.now()}`,
            from: 'You',
            to: selectedThread.participants[0],
            content: inputValue,
            type: 'question',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };

        setThreads((prev) =>
            prev.map((t) =>
                t.id === selectedThreadId
                    ? { ...t, messages: [...t.messages, newMessage] }
                    : t
            )
        );

        setInputValue('');

        // Call API
        const result = await sendMessageMutation.mutate([
            selectedThread.participants[0],
            inputValue,
            selectedThreadId,
        ]);

        if (result) {
            success('Message sent');
        } else {
            showError('Failed to send message');
        }

        setIsSending(false);
    };

    const handleApprove = async (messageId: string, approved: boolean) => {
        const result = await approveRequestMutation.mutate({
            messageId,
            approved,
        });

        if (result) {
            if (approved) {
                success('Request approved successfully');
            } else {
                info('Request was declined');
            }

            // Update local state
            setThreads((prev) =>
                prev.map((t) => ({
                    ...t,
                    messages: t.messages.map((m) =>
                        m.id === messageId
                            ? { ...m, isApproved: approved, requiresApproval: false }
                            : m
                    ),
                }))
            );
        }
    };

    const primaryAgent = selectedThread?.participants[0] || 'Alice';
    const agentInfo = agentDescriptions[primaryAgent] || agentDescriptions.Alice;

    // Get pending approvals from local state (derived from threads)
    const pendingApprovals = threads
        .flatMap((t) => t.messages)
        .filter((m) => m.requiresApproval && !m.isApproved);

    if (isLoading) {
        return (
            <>
                <Navbar />
                <main className="container">
                    <LoadingState message="Loading conversations..." />
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
                        <h1 className={styles.title}>Agent Collaboration</h1>
                    </div>

                    <div className={styles.mainLayout}>
                        {/* Threads Sidebar */}
                        <div className={styles.threadsSidebar}>
                            <div className={styles.sidebarHeader}>
                                <span className={styles.sidebarTitle}>Conversations</span>
                                <Badge variant="primary">{threads.length}</Badge>
                            </div>
                            <div className={styles.threadList}>
                                {threads.map((thread) => (
                                    <div
                                        key={thread.id}
                                        className={`${styles.threadItem} ${selectedThreadId === thread.id ? styles.threadItemActive : ''}`}
                                        onClick={() => setSelectedThreadId(thread.id)}
                                    >
                                        <div className={styles.threadParticipants}>
                                            {thread.participants.slice(0, 2).map((name) => (
                                                <Avatar key={name} name={name} size="sm" />
                                            ))}
                                        </div>
                                        <div className={styles.threadContent}>
                                            <p className={styles.threadTopic}>{thread.topic}</p>
                                            <div className={styles.threadMeta}>
                                                <Badge
                                                    variant={
                                                        thread.status === 'active' ? 'success' :
                                                            thread.status === 'pending' ? 'warning' : 'default'
                                                    }
                                                >
                                                    {thread.status}
                                                </Badge>
                                                <span>{thread.lastMessage}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Conversation Panel */}
                        <div className={styles.conversationPanel}>
                            {selectedThread ? (
                                <>
                                    <div className={styles.conversationHeader}>
                                        <div className={styles.conversationInfo}>
                                            <MessageCircle size={20} />
                                            <div>
                                                <h3 className={styles.conversationTitle}>{selectedThread.topic}</h3>
                                                <p className={styles.conversationStatus}>
                                                    {selectedThread.messages.length} messages • {selectedThread.status}
                                                </p>
                                            </div>
                                        </div>
                                        <div className={styles.conversationParticipants}>
                                            {selectedThread.participants.map((name) => (
                                                <Avatar key={name} name={name} size="sm" />
                                            ))}
                                        </div>
                                    </div>

                                    <div className={styles.messagesContainer}>
                                        <AnimatePresence>
                                            {selectedThread.messages.map((message) => (
                                                <motion.div
                                                    key={message.id}
                                                    className={`${styles.message} ${message.from === 'You' ? styles.messageFromUser : ''}`}
                                                    initial={{ opacity: 0, y: 10 }}
                                                    animate={{ opacity: 1, y: 0 }}
                                                >
                                                    <Avatar name={message.from} size="md" />
                                                    <div
                                                        className={`${styles.messageBubble} ${message.from === 'You' ? styles.messageBubbleUser : styles.messageBubbleAgent
                                                            }`}
                                                    >
                                                        <div className={styles.messageHeader}>
                                                            <span className={styles.messageSender}>{message.from}</span>
                                                            <span className={styles.messageTime}>{message.timestamp}</span>
                                                            {message.type === 'approval_request' && !message.isApproved && (
                                                                <Badge variant="warning">Needs Approval</Badge>
                                                            )}
                                                            {message.isApproved && (
                                                                <Badge variant="success">Approved</Badge>
                                                            )}
                                                        </div>
                                                        <p className={styles.messageContent}>
                                                            {message.content.split('\n').map((line, i) => (
                                                                <span key={i}>
                                                                    {line}
                                                                    {i < message.content.split('\n').length - 1 && <br />}
                                                                </span>
                                                            ))}
                                                        </p>
                                                        {message.requiresApproval && !message.isApproved && (
                                                            <div className={styles.approvalRequest}>
                                                                <div className={styles.approvalHeader}>
                                                                    <AlertTriangle size={14} />
                                                                    Approval Required
                                                                </div>
                                                                <div className={styles.approvalActions}>
                                                                    <Button
                                                                        size="sm"
                                                                        variant="success"
                                                                        icon={<Check size={14} />}
                                                                        onClick={() => handleApprove(message.id, true)}
                                                                        loading={approveRequestMutation.isLoading}
                                                                    >
                                                                        Approve
                                                                    </Button>
                                                                    <Button
                                                                        size="sm"
                                                                        variant="secondary"
                                                                        icon={<X size={14} />}
                                                                        onClick={() => handleApprove(message.id, false)}
                                                                    >
                                                                        Decline
                                                                    </Button>
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                </motion.div>
                                            ))}
                                        </AnimatePresence>
                                        <div ref={messagesEndRef} />
                                    </div>

                                    <form onSubmit={handleSubmit} className={styles.inputArea}>
                                        <div className={styles.inputContainer}>
                                            <div className={styles.inputField}>
                                                <Textarea
                                                    value={inputValue}
                                                    onChange={(e) => setInputValue(e.target.value)}
                                                    placeholder={`Message ${primaryAgent}...`}
                                                    rows={2}
                                                    noResize
                                                    onKeyDown={(e) => {
                                                        if (e.key === 'Enter' && !e.shiftKey) {
                                                            e.preventDefault();
                                                            handleSubmit(e);
                                                        }
                                                    }}
                                                />
                                            </div>
                                            <Button
                                                type="submit"
                                                disabled={!inputValue.trim() || isSending}
                                                loading={isSending}
                                                icon={<Send size={18} />}
                                            >
                                                Send
                                            </Button>
                                        </div>
                                    </form>
                                </>
                            ) : (
                                <EmptyState
                                    icon={<Users size={48} />}
                                    title="No conversation selected"
                                    description="Select a thread from the sidebar to view messages"
                                />
                            )}
                        </div>

                        {/* Agent Info Panel */}
                        <div className={styles.agentInfoPanel}>
                            <div className={styles.agentInfoHeader}>Agent Info</div>
                            <div className={styles.agentInfoContent}>
                                <div className={styles.agentCard}>
                                    <Avatar name={primaryAgent} size="xl" />
                                    <h4 className={styles.agentName}>{primaryAgent}</h4>
                                    <p className={styles.agentRole}>{agentInfo.role}</p>
                                    <p className={styles.agentDesc}>{agentInfo.description}</p>
                                </div>

                                <div className={styles.pendingApprovals}>
                                    <h5 className={styles.pendingTitle}>
                                        <Clock size={12} />
                                        Pending Approvals ({pendingApprovals.length})
                                    </h5>
                                    <div className={styles.pendingList}>
                                        {pendingApprovals
                                            .slice(0, 3)
                                            .map((m: AgentMessage) => (
                                                <div key={m.id} className={styles.pendingItem}>
                                                    {m.content.slice(0, 60)}...
                                                </div>
                                            ))}
                                        {pendingApprovals.length === 0 && (
                                            <div className={styles.pendingItem}>No pending approvals</div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </>
    );
}
