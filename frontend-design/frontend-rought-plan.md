# 🎯 Next.js 14 Hybrid Implementation Plan for MetaGPT-Pro

## **Architecture Overview**

```
Next.js 15+ Frontend
├── App Router (Server Components by default)
├── Client Components (for interactivity)
├── TailwindCSS + FontAwesome
└── Connects to → FastAPI Backend (Port 8000)
```

---

## 📋 **IMPLEMENTATION PHASES** (5 Phases, ~4-5 Weeks)

---

### **PHASE 1: Project Foundation & Layout**
**Duration:** 3-4 days  
**Goal:** Create Next.js project with base layout and navigation

#### High-Level Tasks:
1. **Initialize Next.js 14 project**
   - Use App Router (not Pages Router)
   - Setup TypeScript configuration
   - Configure TailwindCSS with the design system
   - Add FontAwesome icons

2. **Create project structure**
   ```
   frontend/
   ├── layout.tsx          # Root layout with navigation
   ├── page.tsx            # Home/redirect
   ├── projects/           # Projects routes
   ├── dashboard/          # Dashboard routes
   ├── conversation/       # Conversation routes
   └── components/         # Reusable components
   ```

3. **Build base layout components**
   - Top navigation bar (sticky header)
   - Sidebar (if needed)
   - Footer
   - Use Server Components by default

4. **Setup environment configuration**
   - API endpoint configuration (http://localhost:8000)
   - Environment variables for backend URL
   - CORS configuration if needed

5. **Create API client utility**
   - Utility functions to call FastAPI endpoints
   - Error handling wrapper
   - Response parsing helpers

#### Deliverables:
- ✅ Working Next.js app running on localhost:3000
- ✅ Navigation bar matching mockup design
- ✅ TailwindCSS configured with colors/fonts from mockup
- ✅ Basic routing structure created
- ✅ API client utility ready to use

#### Success Criteria:
- Can navigate between routes
- Layout matches mockup design
- Can successfully call a test endpoint on FastAPI backend

---

### **PHASE 2: Core Views (Server Components)**
**Duration:** 5-7 days  
**Goal:** Implement main dashboard screens using Server Components

#### High-Level Tasks:

1. **Projects List View** (`/projects`)
   - Fetch projects data from `/v1/project/list` (Server Component)
   - Display project cards with status, progress, agents
   - Grid layout matching mockup
   - Click navigation to individual project

2. **Project Dashboard View** (`/dashboard/[projectId]`)
   - Fetch project details from `/v1/project/{id}`
   - Display stats cards (progress, tasks, bugs, velocity)
   - Active agents section
   - Recent activity feed
   - Quick action buttons (modals handled in Phase 4)

3. **New Project View** (`/projects/new`)
   - Two-panel layout (conversation + PRD preview)
   - Conversation panel structure (will add interactivity in Phase 3)
   - PRD preview panel showing generated requirements
   - Approve/modify buttons (functionality in Phase 3)

4. **Create shared components**
   - ProjectCard component
   - StatCard component
   - AgentCard component
   - ActivityItem component
   - All as Server Components initially

5. **Setup data fetching patterns**
   - Use Next.js fetch with caching strategy
   - Handle loading states with loading.tsx
   - Handle errors with error.tsx
   - Implement revalidation strategy

#### Deliverables:
- ✅ Projects list page working with real backend data
- ✅ Project dashboard displaying all sections
- ✅ New project conversation layout ready
- ✅ Shared components library started
- ✅ Proper loading and error states

#### Success Criteria:
- All views render correctly with backend data
- Navigation between views works smoothly
- Design matches mockup pixel-perfect
- Data updates when backend changes (with refresh)

---

### **PHASE 3: Interactive Features (Client Components)**
**Duration:** 6-8 days  
**Goal:** Add real-time updates and user interactions

#### High-Level Tasks:

1. **Convert interactive parts to Client Components**
   - Mark components with 'use client' directive
   - Chat message input and send
   - Modal triggers and handlers
   - Form inputs and submissions
   - Interactive buttons with state

2. **Implement New Project Conversation**
   - Chat message input (Client Component)
   - Send message to `/v1/conversation/{id}/message`
   - Display conversation thread
   - Auto-scroll to latest message
   - Show typing indicators

3. **Setup WebSocket connections**
   - Create WebSocket context provider
   - Connect to `/v1/stream/ws/{project_id}`
   - Handle real-time agent updates
   - Handle real-time message updates
   - Handle real-time sprint/task updates
   - Reconnection logic on disconnect

4. **Implement real-time updates**
   - Agent status changes (live pulse dots)
   - New messages appearing automatically
   - Task status updates on board
   - Bug count updates
   - Activity feed real-time additions

5. **Add state management**
   - Use React Context for global state (WebSocket connection, current project)
   - Local state for form inputs
   - Optimistic UI updates (show changes immediately, confirm with backend)

#### Deliverables:
- ✅ Conversation interface fully interactive
- ✅ WebSocket connected and receiving updates
- ✅ Real-time agent status updates working
- ✅ Forms can submit data to backend
- ✅ Optimistic UI feedback implemented

#### Success Criteria:
- Can create new project through conversation
- See agent responses appear in real-time
- Agent status dots pulse and update live
- No page refresh needed for updates
- Smooth, responsive interactions

---

### **PHASE 4: Advanced Views & Components**
**Duration:** 5-7 days  
**Goal:** Build complex interactive views (Sprint Board, Files, Bugs, Versions)

#### High-Level Tasks:

1. **Sprint Board View** (`/board/[projectId]`)
   - Kanban columns (To Do, In Progress, Review, Done)
   - Task cards with drag-and-drop
   - Use a drag-drop library recommendation: @dnd-kit/core
   - Update task status via API on drop
   - Filter by sprint, assignee, epic
   - Real-time task updates via WebSocket

2. **Agent Conversation View** (`/conversation/[projectId]`)
   - Thread list sidebar
   - Active thread display
   - Agent-to-agent message visualization
   - User can only message Alice (PM)
   - Message Alice input with send
   - Approval workflow UI (approve/reject buttons)

3. **Bug Tracker View** (`/bugs/[projectId]`)
   - Bug list table with sorting/filtering
   - Severity badges (Critical, High, Medium, Low)
   - Status filters (Open, In Progress, Fixed, Verified)
   - Click to view bug details
   - Bug count stats at top
   - Real-time bug creation notifications

4. **Version History View** (`/history/[projectId]`)
   - Timeline of file versions
   - Side-by-side diff viewer
   - Syntax highlighting for code diffs
   - Rollback functionality
   - Version comparison dropdown

5. **File Explorer View** (`/files/[projectId]`)
   - Directory tree navigation
   - File list with icons by type
   - File preview panel
   - Download buttons
   - Version history link per file

6. **Modal Components**
   - Feature Request modal
   - Change Request modal
   - Bug Report modal
   - Implementation Plan modal
   - Use modal overlay pattern
   - Form validation

#### Deliverables:
- ✅ Sprint board with drag-drop working
- ✅ Agent conversation fully functional
- ✅ Bug tracker with filtering
- ✅ Version diff viewer implemented
- ✅ File explorer browsing works
- ✅ All modals functional

#### Success Criteria:
- Can drag tasks and update status
- Can message Alice and see responses
- Can filter and sort bugs
- Can view code diffs clearly
- Can browse and preview files
- Modals open/close smoothly

---

### **PHASE 5: Polish, Performance & Testing**
**Duration:** 4-5 days  
**Goal:** Production-ready frontend with optimizations

#### High-Level Tasks:

1. **Performance Optimization**
   - Implement proper code splitting (automatic with Next.js)
   - Optimize images with Next.js Image component
   - Add proper loading skeletons
   - Implement pagination for long lists
   - Debounce search inputs
   - Lazy load heavy components

2. **Error Handling & UX**
   - Global error boundary
   - Toast notifications for actions
   - Empty states for no data
   - Loading states for all async operations
   - Retry logic for failed API calls
   - User-friendly error messages

3. **Responsive Design**
   - Mobile navigation (hamburger menu)
   - Responsive grid layouts
   - Touch-friendly interactive elements
   - Test on mobile, tablet, desktop
   - Adjust Sprint board for mobile (stack columns)

4. **Accessibility**
   - Keyboard navigation support
   - ARIA labels on interactive elements
   - Focus management in modals
   - Screen reader support for key features
   - Color contrast compliance

5. **Testing & Documentation**
   - Test all user flows end-to-end
   - Test WebSocket reconnection
   - Test concurrent user scenarios
   - Create README with setup instructions
   - Document environment variables
   - Document API integration points

6. **Deployment Preparation**
   - Build optimization
   - Environment configuration
   - Docker containerization (optional)
   - Deployment documentation

#### Deliverables:
- ✅ Optimized production build
- ✅ Error handling throughout
- ✅ Responsive on all screen sizes
- ✅ Accessible to keyboard/screen readers
- ✅ Comprehensive testing completed
- ✅ Deployment documentation

#### Success Criteria:
- Build completes without errors
- Lighthouse score > 90 (Performance, Accessibility)
- Works smoothly on mobile devices
- No console errors or warnings
- All features tested and working
- Ready for production deployment

---

## 🛠️ **TECHNOLOGY STACK DETAILS**

### **Frontend (Next.js 14)**
```
Core:
- Next.js 14.x (App Router)
- React 18.x
- TypeScript

Styling:
- TailwindCSS 3.x
- FontAwesome 6.x

State & Data:
- React Context (global state)
- SWR or React Query (data fetching, optional)
- WebSocket (native)

Utilities:
- @dnd-kit/core (drag and drop)
- date-fns (date formatting)
- react-hot-toast (notifications)
```

### **Integration**
```
Backend API: http://localhost:8000
WebSocket: ws://localhost:8000/v1/stream/ws
```

---

## 📁 **PROJECT STRUCTURE**

```
frontend/
├── app/                    # App Router pages
│   ├── layout.tsx          # Root layout with providers
│   ├── page.tsx            # Landing → redirect to /projects
│   ├── globals.css         # CSS variables + base styles
│   ├── projects/           # Projects list
│   ├── project/[id]/       # Project dashboard (dynamic)
│   │   ├── page.tsx        # Dashboard view
│   │   ├── board/          # Sprint board
│   │   ├── bugs/           # Bug tracker
│   │   ├── agents/         # Agent collaboration
│   │   ├── versions/       # Version history
│   │   └── files/          # File explorer
│   └── new/                # New project wizard
├── components/             # Reusable components
│   ├── ui/                 # Atomic UI components
│   ├── layout/             # Layout components
│   ├── project/            # Project-specific components
│   ├── chat/               # Conversation components
│   ├── board/              # Kanban board components
│   ├── bugs/               # Bug tracking components
│   └── agents/             # Agent collaboration components
├── lib/                    # Utilities
│   ├── api/                # API client functions
│   ├── hooks/              # Custom React hooks
│   ├── websocket/          # WebSocket manager
│   └── utils/              # Helper functions
├── styles/                 # Component CSS modules
└── types/                  # TypeScript definitions
```

---

## 🎯 **INSTRUCTIONS FOR CLAUDE OPUS 4.5**

### **Phase Execution Order:**
Execute phases **sequentially** (complete Phase 1 before Phase 2, etc.)

### **For Each Phase:**

1. **Read the phase objectives carefully**
2. **Review the mockup HTML** (`metagpt-pro-complete-dashboard.html`) for design reference
3. **Create the components and routes** as described
4. **Test each feature** before moving to next task
5. **Ensure design matches mockup** (colors, spacing, fonts, layout)
6. **Confirm success criteria** before completing phase

### **General Guidelines:**

1. **Server vs Client Components:**
   - Default to Server Components (better performance)
   - Only use Client Components when needed:
     - User interactions (forms, buttons with state)
     - Browser APIs (localStorage, etc.)
     - React hooks (useState, useEffect, etc.)
     - Event listeners

2. **API Integration:**
   - Use the existing FastAPI endpoints
   - Handle loading states (show skeletons)
   - Handle errors gracefully (show error messages)
   - Use proper TypeScript types for API responses

3. **Real-time Updates:**
   - Establish WebSocket connection on project pages
   - Subscribe to relevant events
   - Update UI optimistically (show changes immediately)
   - Confirm with backend response

4. **Design Consistency:**
   - Extract design tokens (colors, spacing, fonts) from mockup
   - Use consistent component patterns
   - Match mockup exactly (pixel-perfect)
   - Maintain responsive design principles

5. **Code Quality:**
   - Use TypeScript strictly (no `any` types)
   - Create reusable components
   - Keep components small and focused
   - Add proper prop validation
   - Include error boundaries

---

## 📊 **SUCCESS METRICS**

### **After All Phases Complete:**

✅ **Functionality:**
- All 8 views working (Projects, New Project, Dashboard, Board, Conversation, Bugs, History, Files)
- Real-time updates functioning
- Forms submitting successfully
- Navigation smooth and correct

✅ **Performance:**
- Initial load < 2 seconds
- Route transitions < 500ms
- WebSocket latency < 100ms
- Build size optimized

✅ **Quality:**
- Design matches mockup exactly
- Responsive on all devices
- No TypeScript errors
- No console warnings
- Accessible (keyboard navigation works)

✅ **Integration:**
- All FastAPI endpoints integrated
- WebSocket connection stable
- Error handling complete
- Loading states everywhere

---

## 🚀 **DEPLOYMENT NOTES**

### **Development:**
```bash
# Frontend runs on: http://localhost:3000
# Backend runs on: http://localhost:8000
```

### **Production:**
```
Option 1: Deploy separately
- Frontend: Vercel (recommended for Next.js)
- Backend: Railway/Render/AWS

Option 2: Docker Compose
- Both services in one deployment
- Nginx reverse proxy
```

---

## ✅ **FINAL CHECKLIST FOR CLAUDE OPUS**

Before marking project complete, verify:

- [ ] All 5 phases completed
- [ ] All success criteria met per phase
- [ ] Design matches mockup in all views
- [ ] Real-time features working smoothly
- [ ] All API endpoints integrated
- [ ] Error handling comprehensive
- [ ] Responsive design tested
- [ ] Performance optimized
- [ ] TypeScript types complete
- [ ] Documentation written
- [ ] Production build successful

---

## 🎬 **READY TO START?**

This plan is now ready to give to Claude Opus 4.5 in Google Antigravity IDE.
