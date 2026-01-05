# 🏗️ SYSTEM ARCHITECTURE

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   STREAMLIT USER INTERFACE                  │
│  ┌────────────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Chat Assistant │  │ Issue Mgr│  │ Knowledge Base   │   │
│  └────────────────┘  └──────────┘  └──────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
            ┌──────────────────────┐
            │   Issue Detector     │ (detect_issue)
            │  - Keyword matching  │
            │  - Category tagging  │
            └──────────┬───────────┘
                       │
         ┌─────────────┴─────────────┐
         ↓                           ↓
    ┌─────────┐              ┌──────────────┐
    │  QUERY  │              │  ACTION/ISSUE│
    │  MODE   │              │   MODE       │
    └────┬────┘              └──────┬───────┘
         │                          │
         ↓                          ↓
    ┌──────────────┐        ┌──────────────────┐
    │  RAG System  │        │  Action Tools    │
    │              │        │                  │
    │ • Vector DB  │        │ • create_ticket  │
    │ • FAISS      │        │ • schedule_mtg   │
    │ • Retriever  │        │ • issue_detector │
    └────┬─────────┘        └──────┬───────────┘
         │                         │
         ├─ HuggingFace Embeddings │
         ├─ Document Chunks       │
         │                        │
         ↓                        ↓
    ┌──────────────┐        ┌────────────────┐
    │  LangChain   │        │  Database      │
    │  RetrievalQA │        │                │
    └──────┬───────┘        │ • Tickets      │
           │                │ • Meetings     │
           ↓                └────────┬───────┘
    ┌────────────────┐              │
    │   LLM Response │              ↓
    │  (Gemini 1.5)  │       ┌────────────────┐
    └────────┬───────┘       │   SMTP Email   │
             │               │   Notifications│
             ↓               └────────────────┘
    ┌─────────────────────────┐
    │  Format & Display       │
    │  - Chat History         │
    │  - Source Documents     │
    │  - Confirmation         │
    └─────────────────────────┘
```

---

## Module Interaction Diagram

```
app.py (Main UI)
    ├── backend/agent.py
    │   ├── backend/prompts.py
    │   ├── backend/rag_engine.py
    │   │   ├── FAISS Index
    │   │   └── HuggingFace Embeddings
    │   └── backend/tools.py
    │       ├── Gmail SMTP
    │       └── In-Memory Storage
    │
    └── Streamlit Framework
        ├── Chat History
        ├── Sidebar Config
        └── Dashboard
```

---

## Data Flow for Different Query Types

### **Type 1: Information Query** 📚
```
User: "What was Q4 revenue?"
  ↓
Issue Detector: "Not an issue → QUERY"
  ↓
RAG System:
  - Embed query with HuggingFace
  - Search FAISS vector DB
  - Retrieve top 3 documents
  ↓
LLM Processing:
  - Prompt: "Answer based on documents..."
  - Gemini: Generates answer from docs
  ↓
Response:
  "According to the 2024 report, Q4 revenue was $2.5B"
  + Source documents
```

### **Type 2: System Issue** 🔧
```
User: "The login server is down"
  ↓
Issue Detector: "Keywords: 'down' → ISSUE, Type: IT_ISSUE"
  ↓
Agent Tools:
  - Routes to: create_it_ticket
  - Passes: issue description
  ↓
create_it_ticket():
  - Generates ticket ID
  - Stores in database
  - Sends email to user
  ↓
Response:
  "✅ Ticket TICKET-1001 created"
  + Confirmation email sent
```

### **Type 3: HR Request** 👔
```
User: "I want to meet with HR about promotion"
  ↓
Issue Detector: "Keywords: 'meet', 'hr' → ISSUE, Type: HR_MEETING"
  ↓
Agent Tools:
  - Routes to: schedule_meeting
  - Passes: reason, user info
  ↓
schedule_meeting():
  - Generates meeting ID
  - Stores request
  - Emails HR department
  - Confirms to user
  ↓
Response:
  "✅ Meeting MEETING-2001 requested"
  + HR notified
  + User confirmation email
```

---

## File Responsibilities

```
📁 Project Root
│
├── app.py ⭐ MAIN ENTRY POINT
│   Responsibilities:
│   • Streamlit UI setup
│   • Session state management
│   • User input handling
│   • Multi-mode routing
│   • Chat history tracking
│   • Dashboard rendering
│
├── requirement.txt
│   • All Python dependencies
│   • Exact versions pinned
│
├── .env (CONFIG - NOT IN REPO)
│   • API keys
│   • SMTP credentials
│   • Email addresses
│
├── backend/agent.py ⭐ AGENT LOGIC
│   Responsibilities:
│   • LLM initialization
│   • Tool registration
│   • Prompt templates
│   • Agent execution
│   • Issue detection
│
├── backend/prompts.py
│   Responsibilities:
│   • System prompts
│   • Agent instructions
│   • Classification prompts
│
├── backend/rag_engine.py
│   Responsibilities:
│   • PDF loading
│   • Document chunking
│   • Embedding generation
│   • Vector DB creation
│   • Vector DB loading
│
├── backend/tools.py ⭐ ACTION TOOLS
│   Responsibilities:
│   • Ticket creation
│   • Meeting scheduling
│   • Email sending
│   • Data persistence
│   • Status retrieval
│
├── data/
│   └── Annual-Report-2024-25.pdf
│       • Knowledge base
│       • Vector DB source
│
├── vector_store/faiss_index/
│   └── index.faiss
│       • Pre-built embeddings
│       • Fast similarity search
│
├── test_components.py 🧪 TESTING
│   • Import validation
│   • Environment check
│   • Component testing
│   • Integration testing
│
├── CODE_REVIEW_SUMMARY.md 📖 DOCUMENTATION
│   • Issues found & fixed
│   • Improvements made
│   • Testing guide
│   • Deployment checklist
│
├── DEPLOYMENT_GUIDE.md 🚀 DEPLOYMENT
│   • Setup instructions
│   • Testing procedures
│   • Cloud deployment
│   • Security setup
│   • Troubleshooting
│
└── README_NEW.md 📚 USER GUIDE
    • Feature overview
    • Quick start
    • Configuration
    • Use cases
```

---

## Technology Stack Layers

```
┌─────────────────────────────────────────────────────┐
│           User Interface Layer                      │
│  Streamlit UI with sidebar, tabs, chat history     │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│        Application Logic Layer                      │
│  Agent orchestration, issue detection, routing     │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│         AI/ML Processing Layer                      │
│  LLM (Gemini), Embeddings (HuggingFace), Tools    │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│       Data & Storage Layer                          │
│  FAISS Vector DB, In-Memory Store, SMTP Email     │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│      External Services Layer                        │
│  Google Gemini API, Gmail SMTP, PDF Loader         │
└─────────────────────────────────────────────────────┘
```

---

## Request Processing Pipeline

```
1. USER INPUT
   ├── Text received via Streamlit
   └── Stored in session_state

2. PREPROCESSING
   ├── Validate input (not empty)
   ├── Store in chat history
   └── Display user message

3. ISSUE CLASSIFICATION
   ├── Run keyword detection
   ├── Categorize: QUERY vs ISSUE
   └── Determine severity

4. ROUTING
   ├── IF QUERY → Use RAG
   ├── IF ISSUE → Use Action Tools
   └── IF MODE SPECIFIC → Filter

5. PROCESSING
   ├── RAG Path:
   │   ├── Embed query
   │   ├── Search FAISS
   │   └── Retrieve documents
   │
   └── Action Path:
       ├── Route to tool
       ├── Execute tool
       └── Get confirmation

6. LLM PROCESSING
   ├── Build context/prompt
   ├── Call Gemini API
   └── Get response

7. POSTPROCESSING
   ├── Format response
   ├── Add citations (if RAG)
   ├── Add confirmations (if action)
   └── Update history

8. OUTPUT
   ├── Display response
   ├── Show source docs (if RAG)
   └── Confirmation messages

9. STORAGE
   ├── Save to session_state
   ├── Update dashboard data
   └── Log action
```

---

## Security & Data Flow

```
┌─────────────┐
│  User Input │
└──────┬──────┘
       │
       ├─ Validation (check not empty)
       ├─ Sanitization (remove special chars)
       └─ Classification (issue type)
       ↓
┌──────────────────────┐
│ LLM Processing       │
│ (Gemini API)         │
└──────┬───────────────┘
       │
       ├─ No data logging
       ├─ API key protected
       └─ Encrypted requests (HTTPS)
       ↓
┌──────────────────────┐
│ Action Processing    │
│ (Tool Execution)     │
└──────┬───────────────┘
       │
       ├─ Ticket stored locally
       ├─ User email verified
       ├─ Email sent (SMTP TLS)
       └─ Audit logged
       ↓
┌──────────────────────┐
│ Response             │
│ (To User)            │
└──────────────────────┘
```

---

## Scalability Considerations

Current: **Single Instance**
```
User → App.py → Agent → Tools → User
```

Future: **Distributed**
```
Users → Load Balancer → App Instances
            ↓
        Shared Database (PostgreSQL)
            ↓
        Message Queue (Redis/RabbitMQ)
            ↓
        Worker Processes
```

---

## Integration Points

Current Integrations:
- ✅ Google Gemini API
- ✅ HuggingFace Embeddings
- ✅ Gmail SMTP

Future Integration Points:
- 🔲 Jira/Azure DevOps (tickets)
- 🔲 Active Directory (auth)
- 🔲 Office 365 Calendar (meetings)
- 🔲 Slack (notifications)
- 🔲 ServiceNow (ticketing)
- 🔲 LDAP (user directory)

---

## Performance Metrics

| Operation | Time | Bottleneck |
|-----------|------|-----------|
| Embedding generation | ~100ms | Local HuggingFace |
| Vector DB search | ~10ms | FAISS (in-memory) |
| LLM inference | ~2-5s | Gemini API |
| Email sending | ~1-2s | SMTP |
| Total response | ~2-7s | LLM inference |

---

This architecture ensures:
- 🚀 **Fast response times** (local embeddings + FAISS)
- 🔐 **Data privacy** (local vector DB)
- 💰 **Cost efficiency** (free HuggingFace embeddings)
- 📈 **Scalability** (modular design)
- 🎯 **Reliability** (error handling everywhere)
