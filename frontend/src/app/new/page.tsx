'use client';

import { useState, useRef, useEffect, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Send, FileText, Sparkles, Check, Lightbulb, Target, CheckSquare, AlertCircle, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Navbar } from '@/components/layout';
import { Button, Avatar, Badge, Textarea } from '@/components/ui';
import { startConversation, sendMessage, approveRequirements } from '@/lib/api';
import { config } from '@/lib/config';
import styles from './page.module.css';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface PRDPreview {
    projectName?: string;
    vision?: string;
    userStories?: { story: string; priority: string }[];
    technicalRequirements?: string[];
    successMetrics?: string[];
    clarifyingQuestions?: string[];
}

export default function NewProjectPage() {
    const router = useRouter();
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [prdPreview, setPrdPreview] = useState<PRDPreview | null>(null);
    const [canApprove, setCanApprove] = useState(false);
    const [isApproving, setIsApproving] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!inputValue.trim() || isLoading) return;

        const userMessage: Message = {
            id: `msg-${Date.now()}`,
            role: 'user',
            content: inputValue.trim(),
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);
        setIsTyping(true);

        try {
            if (!conversationId) {
                // Start new conversation
                const response = await startConversation(userMessage.content);
                setConversationId(response.conversation_id);

                const assistantMessage: Message = {
                    id: `msg-${Date.now()}-response`,
                    role: 'assistant',
                    content: response.first_question,
                    timestamp: new Date(),
                };
                setMessages((prev) => [...prev, assistantMessage]);
            } else {
                // Continue conversation
                const response = await sendMessage(conversationId, userMessage.content);

                const assistantMessage: Message = {
                    id: `msg-${Date.now()}-response`,
                    role: 'assistant',
                    content: response.ai_response,
                    timestamp: new Date(),
                };
                setMessages((prev) => [...prev, assistantMessage]);

                // Update PRD preview if enhanced requirements available
                if (response.enhanced_requirements) {
                    const reqs = response.enhanced_requirements as Record<string, unknown>;
                    setPrdPreview({
                        projectName: reqs.project_name as string,
                        vision: reqs.vision as string,
                        userStories: reqs.user_stories as { story: string; priority: string }[],
                        technicalRequirements: reqs.technical_requirements as string[],
                        successMetrics: reqs.success_metrics as string[],
                        clarifyingQuestions: reqs.clarifying_questions as string[],
                    });
                }

                setCanApprove(response.requires_approval);
            }
        } catch (error: any) {
            console.error('Error sending message:', error);
            const errorMessage: Message = {
                id: `msg-${Date.now()}-error`,
                role: 'assistant',
                content: `Error: ${error.message || 'Failed to communicate with AI. Please check backend connection.'}`,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
            setIsTyping(false);
        }
    };

    const handleApprove = async () => {
        if (!conversationId) return;

        setIsApproving(true);
        try {
            const response = await approveRequirements(conversationId);
            router.push(`/project/${response.project_id}`);
        } catch (error) {
            console.error('Error approving:', error);
            // Start new conversation
            console.error('Error approving:', error);
        }
    };

    return (
        <>
            <Navbar />
            <div className={styles.page}>
                {/* Conversation Panel */}
                <div className={styles.conversationPanel}>
                    <div className={styles.conversationHeader}>
                        <h1 className={styles.conversationTitle}>Start a New Project</h1>
                        <p className={styles.conversationSubtitle}>
                            Describe your idea to Alice, our AI Product Manager
                        </p>
                    </div>

                    <div className={styles.messagesContainer}>
                        {messages.length === 0 && (
                            <div className={styles.emptyState}>
                                <Sparkles size={48} className={styles.emptyIcon} />
                                <h3 className={styles.emptyTitle}>What would you like to build?</h3>
                                <p className={styles.emptyDescription}>
                                    Describe your project idea and Alice will help you refine the requirements.
                                </p>
                            </div>
                        )}

                        <AnimatePresence>
                            {messages.map((message, index) => (
                                <motion.div
                                    key={message.id}
                                    className={`${styles.message} ${message.role === 'user' ? styles.messageUser : ''}`}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                >
                                    <div className={styles.messageAvatar}>
                                        <Avatar
                                            name={message.role === 'user' ? 'You' : 'Alice'}
                                            size="md"
                                        />
                                    </div>
                                    <div>
                                        <div
                                            className={`${styles.messageBubble} ${message.role === 'user'
                                                ? styles.messageBubbleUser
                                                : styles.messageBubbleAssistant
                                                }`}
                                        >
                                            {message.content.split('\n').map((line, i) => (
                                                <p key={i} style={{ marginBottom: line ? '0.5rem' : 0 }}>
                                                    {line}
                                                </p>
                                            ))}
                                        </div>
                                        <p className={styles.messageTime}>
                                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {isTyping && (
                            <div className={styles.message}>
                                <Avatar name="Alice" size="md" />
                                <div className={`${styles.messageBubble} ${styles.messageBubbleAssistant}`}>
                                    <div className={styles.typingIndicator}>
                                        <span className={styles.typingDot} />
                                        <span className={styles.typingDot} />
                                        <span className={styles.typingDot} />
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    <form onSubmit={handleSubmit} className={styles.inputArea}>
                        <div className={styles.inputContainer}>
                            <div className={styles.inputField}>
                                <Textarea
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    placeholder="Describe your project idea..."
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
                                disabled={!inputValue.trim() || isLoading}
                                loading={isLoading}
                                icon={<Send size={18} />}
                            >
                                Send
                            </Button>
                        </div>
                    </form>
                </div>

                {/* PRD Preview Panel */}
                <div className={styles.previewPanel}>
                    <div className={styles.previewHeader}>
                        <h2 className={styles.previewTitle}>
                            <FileText size={20} style={{ marginRight: 8, opacity: 0.7 }} />
                            Product Requirements
                        </h2>
                        {prdPreview && <Badge variant="primary">Draft</Badge>}
                    </div>

                    <div className={styles.previewContent}>
                        {!prdPreview ? (
                            <div className={styles.emptyState}>
                                <FileText size={48} className={styles.emptyIcon} />
                                <h3 className={styles.emptyTitle}>PRD Preview</h3>
                                <p className={styles.emptyDescription}>
                                    As you chat with Alice, the requirements document will appear here.
                                </p>
                            </div>
                        ) : (
                            <>
                                {prdPreview.projectName && (
                                    <div className={styles.prdSection}>
                                        <h2 className={styles.prdSectionTitle}>
                                            <Target size={16} />
                                            Project Name
                                        </h2>
                                        <p className={styles.prdContent}>{prdPreview.projectName}</p>
                                    </div>
                                )}

                                {prdPreview.vision && (
                                    <div className={styles.prdSection}>
                                        <h2 className={styles.prdSectionTitle}>
                                            <Lightbulb size={16} />
                                            Vision
                                        </h2>
                                        <p className={styles.prdContent}>{prdPreview.vision}</p>
                                    </div>
                                )}

                                {prdPreview.userStories && prdPreview.userStories.length > 0 && (
                                    <div className={styles.prdSection}>
                                        <h2 className={styles.prdSectionTitle}>
                                            <CheckSquare size={16} />
                                            User Stories
                                        </h2>
                                        <div className={styles.prdList}>
                                            {prdPreview.userStories.map((story, index) => (
                                                <div key={index} className={styles.prdListItem}>
                                                    <span className={styles.prdItemDot} />
                                                    <span className={styles.prdItemContent}>{story.story}</span>
                                                    <Badge variant={story.priority === 'high' ? 'danger' : story.priority === 'medium' ? 'warning' : 'success'} >
                                                        {story.priority}
                                                    </Badge>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {prdPreview.technicalRequirements && prdPreview.technicalRequirements.length > 0 && (
                                    <div className={styles.prdSection}>
                                        <h2 className={styles.prdSectionTitle}>
                                            <AlertCircle size={16} />
                                            Technical Requirements
                                        </h2>
                                        <div className={styles.prdList}>
                                            {prdPreview.technicalRequirements.map((req, index) => (
                                                <div key={index} className={styles.prdListItem}>
                                                    <span className={styles.prdItemDot} />
                                                    <span className={styles.prdItemContent}>{req}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                    </div>

                    {canApprove && (
                        <div className={styles.previewFooter}>
                            <div className={styles.footerInfo}>
                                <Check size={16} />
                                Requirements ready for approval
                            </div>
                            <div className={styles.footerActions}>
                                <Button variant="secondary">Edit PRD</Button>
                                <Button
                                    onClick={handleApprove}
                                    loading={isApproving}
                                    icon={<ArrowRight size={18} />}
                                    iconPosition="right"
                                >
                                    Approve & Start
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
