# 🏢 HCLTech Enterprise AI Assistant

> **Intelligent AI-Powered Enterprise Assistant** that combines RAG (Retrieval Augmented Generation), automated ticketing, HR meeting scheduling, and user authentication in a modern Streamlit interface.

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Features Deep Dive](#-features-deep-dive)
- [API Documentation](#-api-documentation)
- [Screenshots](#-screenshots)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)

---

## 🎯 Overview

The **HCLTech Enterprise AI Assistant** is a full-stack intelligent chatbot system designed for enterprise environments. It leverages state-of-the-art AI models (Groq LLaMA 3.3 70B) with Retrieval Augmented Generation (RAG) to provide accurate, document-grounded answers while automating support workflows.

### What Makes This Special?

- **🔍 Document-Grounded Responses** - Answers ONLY from enterprise documents with page-level citations
- **🎫 Automated IT Ticketing** - Intelligent issue detection and ticket creation with email notifications
- **📅 Smart Meeting Scheduling** - HR meeting requests with automated confirmations
- **🔐 Enterprise-Grade Auth** - Secure user authentication with bcrypt password hashing
- **🎨 Modern UI/UX** - Glassmorphic design with dark theme and responsive layout
- **📊 Real-Time Dashboards** - Track tickets, meetings, and user activity
- **💾 JSON Export** - Download all tickets and meetings as structured data

---

## ✨ Key Features

### 🤖 AI-Powered Intelligence

| Feature | Description | Status |
|---------|-------------|--------|
| **RAG Engine** | FAISS vector database with HuggingFace embeddings (all-MiniLM-L6-v2) | ✅ Active |
| **LLM** | Groq LLaMA 3.3 70B Versatile (Fast & Free) | ✅ Active |
| **Intent Detection** | Automatic classification of user queries (IT issues, HR requests, general queries) | ✅ Active |
| **Page Citations** | Every answer includes exact page references from source documents | ✅ Active |
| **Abuse Detection** | Filters inappropriate language and maintains professional conversations | ✅ Active |

### 🎫 Automated Workflows

- **IT Ticket Creation** - Automatic ticket generation with priority assignment
- **HR Meeting Scheduling** - Direct integration with HR department workflow
- **Email Notifications** - SMTP-based confirmations for all actions
- **User-Specific Views** - Personalized dashboards showing only user's tickets/meetings
- **SQLite Storage** - Persistent storage for tickets, meetings, and user data

### 🔐 Security & Authentication

- **Standalone Login Portal** - Modern floating authentication page (`floating-auth-page/`)
- **Bcrypt Password Hashing** - Industry-standard password security
- **Case-Insensitive Usernames** - Better UX with SQLite COLLATE NOCASE
- **Session Management** - URL-based session recovery
- **Input Validation** - Comprehensive validation on both frontend and backend
- **Flask API** - RESTful authentication endpoints

### 🎨 User Interface

- **Dark Theme Design** - Professional blue gradient with glassmorphism effects
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Tab Navigation** - Chat Assistant, HR Meetings, IT Tickets tabs
- **Real-Time Chat** - Message history with user/assistant bubbles
- **Interactive Dashboards** - Card-based layouts with modal dialogs
- **Toast Notifications** - Real-time feedback for all actions
- **JSON Export** - Download buttons for tickets and meetings

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  ┌────────────────────┐          ┌──────────────────────┐  │
│  │  Floating Auth     │          │  Streamlit App       │  │
│  │  (HTML/CSS/JS)     │──────────▶  (Main Interface)    │  │
│  └────────────────────┘          └──────────────────────┘  │
└───────────────────────┬────────────────────┬────────────────┘
                        │                     │
                        ▼                     ▼
┌───────────────────────────────────────────────────────────┐
│                   API LAYER (Flask)                        │
│  /api/login  |  /api/signup  |  /api/health               │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│                   BACKEND SERVICES                         │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │  Agent     │  │   RAG    │  │  Tools   │  │  Auth   ││
│  │  (Intent)  │  │ Engine   │  │(Tickets/ │  │ (Users) ││
│  │            │  │          │  │Meetings) │  │         ││
│  └────────────┘  └──────────┘  └──────────┘  └─────────┘│
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│                   DATA LAYER                               │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ SQLite DB    │  │ FAISS Index │  │ PDF Documents   │ │
│  │ (Users,      │  │ (Embeddings)│  │ (Knowledge Base)│ │
│  │  Tickets,    │  │             │  │                 │ │
│  │  Meetings)   │  │             │  │                 │ │
│  └──────────────┘  └─────────────┘  └─────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

### 🔄 Data Flow

1. **User Authentication** → Floating Auth Page → Flask API → SQLite DB
2. **Query Input** → Streamlit Chat → Agent (Intent Detection) → RAG Engine → Vector DB
3. **Issue Detection** → Agent → Confirmation Flow → Tools (Ticket/Meeting) → Email Notification
4. **Dashboard View** → Streamlit Tabs → SQLite Queries → Card Display → JSON Export

---

## 🛠️ Technology Stack

### Core AI & ML

- **LangChain** (0.3.7) - Agent orchestration and RAG pipeline
- **Groq API** - LLaMA 3.3 70B Versatile model (free tier)
- **FAISS** (1.8.0) - Facebook AI Similarity Search for vector storage
- **HuggingFace Embeddings** - all-MiniLM-L6-v2 (384-dim embeddings)
- **Sentence Transformers** (3.0.1) - Document embedding generation

### Backend Framework

- **Streamlit** (1.40.2) - Main application interface
- **Flask** (3.0.0) - Authentication API server
- **Flask-CORS** (4.0.0) - Cross-origin resource sharing
- **SQLite** - Lightweight database for users, tickets, meetings

### Security & Authentication

- **Bcrypt** (4.1.2) - Password hashing
- **Python-dotenv** (1.0.1) - Environment variable management
- **SMTP** - Email notifications (Gmail integration)

### Document Processing

- **PyPDF** (4.3.1) - PDF document loading
- **RecursiveCharacterTextSplitter** - Intelligent text chunking

### Utilities

- **Pandas** - Data manipulation for dashboards
- **Tiktoken** (0.7.0) - Token counting

---

## 📂 Project Structure

```
HCLTech-Enterprise-AI-Assistant/
│
├── 🎨 Frontend
│   ├── app.py                       # Main Streamlit application (1447 lines)
│   └── floating-auth-page/          # Standalone authentication portal
│       ├── index.html               # Login/Signup page with glassmorphism
│       ├── script.js                # Form validation & API integration
│       └── style.css                # Modern red-themed styling
│
├── 🔧 Backend
│   ├── Backend/
│   │   ├── __init__.py              # Package initializer
│   │   ├── agent.py                 # Enterprise AI Agent (234 lines)
│   │   │                            # - Intent detection
│   │   │                            # - Confirmation flow
│   │   │                            # - RAG query handling
│   │   ├── auth.py                  # User authentication (137 lines)
│   │   │                            # - Bcrypt password hashing
│   │   │                            # - Case-insensitive usernames
│   │   │                            # - Session management
│   │   ├── tools.py                 # Action tools (286 lines)
│   │   │                            # - IT ticket creation
│   │   │                            # - HR meeting scheduling
│   │   │                            # - Email notifications
│   │   │                            # - User-specific queries
│   │   ├── rag_engine.py            # Vector database manager
│   │   │                            # - FAISS index building
│   │   │                            # - Document chunking
│   │   │                            # - Embedding generation
│   │   └── prompts.py               # LLM system prompts
│   │
│   └── api.py                       # Flask authentication API (105 lines)
│       └── Endpoints: /api/login, /api/signup, /api/health
│
├── 💾 Data & Storage
│   ├── data/
│   │   └── Annual-Report-2024-25.pdf  # Knowledge base document
│   ├── vector_store/
│   │   └── faiss_index/
│   │       ├── index.faiss           # Vector embeddings
│   │       └── index.pkl             # Metadata
│   └── enterprise_db.sqlite          # Users, tickets, meetings
│
├── ⚙️ Configuration
│   ├── .env                          # Environment variables (API keys, SMTP)
│   ├── requirement.txt               # Python dependencies
│   ├── run.bat                       # Windows startup script
│   └── run.sh                        # Linux/Mac startup script
│
└── 📄 Documentation
    └── README.md                     # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+** (tested on 3.10, 3.11, 3.12)
- **Git** (for cloning)
- **Gmail Account** (optional, for email notifications)

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/HCLTech-Enterprise-AI-Assistant.git
cd HCLTech-Enterprise-AI-Assistant
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirement.txt
```

**Dependencies Installed:**
- langchain, langchain-community, langchain-groq, langchain-huggingface
- faiss-cpu, sentence-transformers, huggingface-hub
- streamlit, flask, flask-cors
- pypdf, bcrypt, python-dotenv

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Groq API (Required)
GROQ_API_KEY=gsk_YOUR_ACTUAL_GROQ_API_KEY_HERE

# Email Configuration (Optional but recommended)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password-here
HR_EMAIL=hr@hcltech.com
```

**Get Your Groq API Key:**
1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign up (free)
3. Create a new API key
4. Copy and paste into `.env`

**Gmail App Password Setup:**
1. Enable 2-Factor Authentication in Gmail
2. Go to Google Account → Security → App Passwords
3. Generate password for "Mail"
4. Use this password (not your regular password)

### Step 5: Build Vector Database

```bash
python Backend/rag_engine.py
```

**Expected Output:**
```
📄 Loading PDF...
✂️ Splitting documents...
🔢 Total chunks created: 450
🧠 Creating embeddings...
📦 Building FAISS index...
✅ Vector database created successfully.
```

---

## ⚙️ Configuration

### Environment Variables Explained

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GROQ_API_KEY` | ✅ Yes | API key for Groq LLM access | `gsk_abc123...` |
| `SMTP_SERVER` | ⚠️ Optional | SMTP server for emails | `smtp.gmail.com` |
| `SMTP_PORT` | ⚠️ Optional | SMTP port | `587` |
| `SENDER_EMAIL` | ⚠️ Optional | Email address for sending | `bot@company.com` |
| `SENDER_PASSWORD` | ⚠️ Optional | Email app password | `xxxx xxxx xxxx xxxx` |
| `HR_EMAIL` | ⚠️ Optional | HR department email | `hr@hcltech.com` |

### Customizing the RAG Engine

Edit `Backend/rag_engine.py`:

```python
# Adjust chunk size for better context
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # Increase for more context
    chunk_overlap=100,     # Increase overlap
)

# Change embedding model
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Higher quality
```

### Customizing the LLM

Edit `Backend/agent.py`:

```python
llm = ChatGroq(
    model="llama-3.1-8b-instant",    # Faster, less accurate
    temperature=0.3,                  # More creative responses
    groq_api_key=API_KEY,
)
```

**Available Models:**
- `llama-3.3-70b-versatile` (Best quality, free)
- `llama-3.1-8b-instant` (Faster, free)

---

## 🎯 Usage

### Starting the Application

#### Option 1: Batch Script (Windows)

```bash
.\run.bat
```

#### Option 2: Shell Script (Linux/Mac)

```bash
chmod +x run.sh
./run.sh
```

#### Option 3: Manual Start

```bash
# Terminal 1: Start Flask API
python api.py

# Terminal 2: Start Streamlit
streamlit run app.py
```

### Access Points

- **🌐 Streamlit App**: http://localhost:8501
- **🔐 Login Page**: Open `floating-auth-page/index.html` in browser
- **🔌 Flask API**: http://localhost:5000/api/health

### First-Time Setup

1. **Open Login Page** (`floating-auth-page/index.html`)
2. **Click "Create Account" Tab**
3. **Fill Registration Form:**
   - Full Name: John Doe
   - Username: johndoe
   - Email: john@hcltech.ac.in
   - Password: YourPassword123 (min 8 chars)
   - Confirm Password: YourPassword123
4. **Click "Create Account"**
5. **Switch to "Sign In" Tab**
6. **Login with Credentials**
7. **Redirected to Streamlit App** (http://localhost:8501?user=johndoe)

---

## 🎨 Features Deep Dive

### 1️⃣ Authentication System

#### Frontend: Floating Auth Page

**Location:** `floating-auth-page/`

**Design Features:**
- 🎨 **Glassmorphism Effect** - Frosted glass appearance with backdrop blur
- 🔴 **Red Accent Theme** - Professional red color scheme (#ef4444)
- 📱 **Responsive Design** - Mobile-friendly layout
- 🎭 **Tab Navigation** - Smooth transitions between Sign In/Sign Up
- 👁️ **Password Toggle** - Show/hide password functionality
- ✅ **Real-Time Validation** - Client-side form validation
- 🔗 **Dynamic "Forgot Password"** - Appears after failed login

**JavaScript Features** (`script.js`):
```javascript
// Input sanitization
username = username.trim();
email = email.trim();

// Password validation
if (password.length < 8) {
    showValidation(field, "Password must be at least 8 characters");
}

// Email validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
    showValidation(field, "Invalid email format");
}
```

#### Backend: Flask API + SQLite

**Endpoints:**

**POST /api/signup**
```json
Request:
{
    "username": "johndoe",
    "password": "SecurePass123",
    "full_name": "John Doe",
    "email": "john@hcltech.ac.in"
}

Response (Success):
{
    "success": true,
    "message": "User created successfully"
}

Response (Error):
{
    "success": false,
    "message": "Username already exists"
}
```

**POST /api/login**
```json
Request:
{
    "username": "johndoe",
    "password": "SecurePass123"
}

Response (Success):
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "john@hcltech.ac.in"
    }
}
```

**Security Features:**
- ✅ **Bcrypt Password Hashing** - Industry-standard algorithm
- ✅ **Case-Insensitive Usernames** - SQLite `COLLATE NOCASE`
- ✅ **SQL Injection Protection** - Parameterized queries
- ✅ **Input Validation** - Length checks, required fields
- ✅ **Error Messages** - Generic messages to prevent enumeration

### 2️⃣ AI Agent & RAG System

#### Intent Detection

The agent automatically classifies user input into 3 categories:

```python
# IT Issue Example
User: "My laptop is not connecting to Wi-Fi"
Agent Detection: {
    "type": "issue",
    "category": "it_issue",
    "requires_action": true
}

# HR Request Example
User: "I need to schedule a meeting with HR about my leave"
Agent Detection: {
    "type": "issue",
    "category": "hr_meeting",
    "requires_action": true
}

# General Query Example
User: "What was the company revenue in 2024?"
Agent Detection: {
    "type": "query",
    "category": "general_query",
    "requires_action": false
}
```

#### Confirmation Flow

For actionable requests, the agent asks for confirmation:

```
User: "The printer on Floor 3 is broken"

Agent: "I'll help you create an IT ticket.
       Do you want me to proceed?
       Reply yes or no."

User: "yes"

Agent: "IT ticket TICKET-1001 has been created. 
       Our support team will contact you shortly."
```

#### RAG Query Handling

**Process:**
1. User asks: *"What was the revenue in 2024?"*
2. Query is embedded using HuggingFace model
3. FAISS searches for top 10 most similar document chunks
4. LLM generates answer with exact page citations

**Example Response:**
```
According to the Annual Report, HCLTech achieved significant growth in 2024.

Key Financial Highlights:
• Total revenue: $12.3 billion [Page 8]
• Year-over-year growth: 15.2% [Page 8]
• Operating profit: $1.8 billion [Page 9]
• Employee count: 219,000+ [Page 12]
• Client satisfaction: 94% [Page 15]
```

#### Page Citation System

Every fact includes `[Page X]` reference:

```python
# From agent.py
context_with_pages = ""
for idx, d in enumerate(docs[:3], 1):
    page = d.metadata.get("page", "N/A")
    content = d.page_content[:800]
    context_with_pages += f"(Page {page})\n{content}\n\n---\n\n"
```

### 3️⃣ IT Ticket System

**Automatic Ticket Creation:**

```python
# When user reports an issue
create_it_ticket(
    issue="Printer on Floor 3 is not working",
    user_name="John Doe",
    user_email="john@hcltech.com",
    user_id=1
)

# Creates:
# - Ticket ID: TICKET-1001
# - Priority: MEDIUM (auto-assigned)
# - Status: OPEN
# - Assigned to: IT Support Team
# - Email notification sent
```

**SQLite Schema:**
```sql
CREATE TABLE tickets (
    ticket_id TEXT PRIMARY KEY,
    issue TEXT,
    user_name TEXT,
    user_email TEXT,
    user_id INTEGER,
    status TEXT,
    priority TEXT,
    assigned_to TEXT,
    created_at TEXT
)
```

**Dashboard Features:**
- 📊 **Grid Layout** - 2-column card display
- 🎨 **Priority Colors** - High (Red), Medium (Orange), Low (Blue)
- 🔍 **Modal Dialogs** - Click "View Details" for full ticket info
- 📥 **JSON Export** - Download all tickets as JSON file
- 👤 **User Filtering** - Only shows tickets created by logged-in user

### 4️⃣ HR Meeting Scheduler

**Meeting Request Flow:**

```
User: "I need to schedule a meeting with HR about my promotion"

Agent: "I'll help you schedule an HR meeting.
       Do you want me to proceed?
       Reply yes or no."

User: "yes"

Agent: "Meeting request MEETING-2001 submitted to HR. 
       You'll receive confirmation email shortly."
```

**Auto-Generated Emails:**

**To HR Department:**
```html
Subject: Meeting Request MEETING-2001

Meeting ID: MEETING-2001
Department: HR
Reason: Promotion discussion
Requester: John Doe (john@hcltech.com)

Please review and confirm availability.
```

**To User:**
```html
Subject: Meeting Request MEETING-2001 Submitted

Your request has been sent to HR Department.
You'll receive confirmation shortly.
```

### 5️⃣ User Interface Components

#### Chat Interface

**Features:**
- 💬 **Scrollable Container** - Dynamic height (200-500px)
- 🎨 **Custom Bubbles** - User (blue) vs Assistant (dark)
- ⌨️ **Chat Input** - Bottom-fixed with clear button
- 🔄 **Auto-Scroll** - New messages scroll into view

**Styling:**
```css
.user-bubble {
    background: #1e40af;
    color: white;
    border-bottom-right-radius: 4px;
}

.assistant-bubble {
    background: rgba(17, 31, 53, 0.85);
    color: #e2e8f0;
    border: 1px solid rgba(30, 58, 95, 0.4);
}
```

#### Dashboard Cards

**Ticket Card Example:**
```html
<div class="card priority-high">
    <h4>TICKET-1001</h4>
    <span class="tag tag-red">High Priority</span>
    <p>Printer on Floor 3 is not working</p>
    <span>IT Support Team</span>
    <button>View Details →</button>
</div>
```

**Interactive Elements:**
- 🎯 **Hover Effects** - Card lifts on hover
- 🎨 **Priority Border** - Left border color indicates urgency
- 📱 **Modal Dialogs** - Full ticket/meeting details
- 📊 **Status Tags** - Color-coded status badges

#### Sidebar Features

**User Profile:**
- 👤 **Avatar Initials** - First 2 letters of name
- 🟢 **Online Status** - Pulsing green dot
- 📧 **User Info** - Full name and email
- 🚪 **Logout Button** - Professional red button

**Notification System:**
- 🔔 **Toggle Switch** - Enable/disable notifications
- 📜 **Activity Log** - Expandable notification history
- 🌐 **Browser Alerts** - Native OS notifications (if permitted)

---

## 📡 API Documentation

### Flask Authentication API

**Base URL:** `http://localhost:5000`

#### Health Check

```http
GET /api/health

Response:
{
    "status": "ok",
    "message": "API is running"
}
```

#### User Registration

```http
POST /api/signup
Content-Type: application/json

Request Body:
{
    "username": "string",
    "password": "string (min 8 chars)",
    "full_name": "string",
    "email": "string"
}

Success Response (201):
{
    "success": true,
    "message": "User created successfully"
}

Error Response (400):
{
    "success": false,
    "message": "Username already exists"
}
```

#### User Login

```http
POST /api/login
Content-Type: application/json

Request Body:
{
    "username": "string",
    "password": "string"
}

Success Response (200):
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "john@hcltech.com"
    }
}

Error Response (401):
{
    "success": false,
    "message": "Invalid username or password"
}
```

### Internal Python Functions

#### Ticket Management

```python
# Create IT ticket
from Backend.tools import create_it_ticket

result = create_it_ticket(
    issue="Description of the issue",
    user_name="John Doe",
    user_email="john@hcltech.com",
    user_id=1
)
# Returns: {"action": "create_it_ticket", "ticket_id": "TICKET-1001", "status": "SUBMITTED"}

# Get user's tickets
from Backend.tools import get_user_tickets

tickets = get_user_tickets(user_id=1)
# Returns: [{"ticket_id": "TICKET-1001", "issue": "...", ...}, ...]
```

#### Meeting Scheduling

```python
# Schedule meeting
from Backend.tools import schedule_meeting

result = schedule_meeting(
    department="HR",
    reason="Promotion discussion",
    user_name="John Doe",
    user_email="john@hcltech.com",
    user_id=1
)
# Returns: {"action": "schedule_meeting", "meeting_id": "MEETING-2001", "status": "PENDING"}
```

---

## 📸 Screenshots

### Authentication Portal
- Modern glassmorphic login/signup page
- Red accent theme with smooth animations
- Password visibility toggle
- Real-time validation feedback

### Chat Interface
- Dark theme with blue gradient background
- User messages in blue bubbles (right-aligned)
- AI responses in dark cards with citations (left-aligned)
- Scrollable message history

### IT Tickets Dashboard
- Grid layout with priority-colored cards
- High priority tickets with red left border
- "View Details" modal with full ticket info
- JSON export button

### HR Meetings Dashboard
- Card-based meeting display
- Department badges and status tags
- Meeting details modal
- User avatar with initials

### Sidebar
- User profile with circular avatar
- Online status indicator (pulsing green dot)
- Notification toggle switch
- Activity log expander
- Professional logout button

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Vector Database Not Found

**Error:** `FileNotFoundError: FAISS index not found`

**Solution:**
```bash
python Backend/rag_engine.py
```

#### 2. Groq API Key Error

**Error:** `ValueError: GROQ_API_KEY missing`

**Solution:**
1. Check `.env` file exists in root directory
2. Verify key format: `GROQ_API_KEY=gsk_...`
3. No quotes needed around the key
4. Restart the application

#### 3. Email Notifications Not Sending

**Symptoms:** Tickets created but no emails received

**Solutions:**
- Check SMTP credentials in `.env`
- For Gmail: Use App Password, not regular password
- Enable "Less secure app access" (not recommended)
- Check spam/junk folder

#### 4. Database Lock Error

**Error:** `sqlite3.OperationalError: database is locked`

**Solution:**
```bash
# Close all applications using the database
# Delete the lock file
rm enterprise_db.sqlite-wal
```

#### 5. Import Errors

**Error:** `ModuleNotFoundError: No module named 'langchain'`

**Solution:**
```bash
# Activate virtual environment first
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirement.txt
```

#### 6. Port Already in Use

**Error:** `OSError: [Errno 48] Address already in use`

**Solution:**
```bash
# Find and kill process on port 8501
netstat -ano | findstr :8501  # Windows
lsof -ti:8501 | xargs kill  # Mac/Linux

# Or use different port
streamlit run app.py --server.port 8502
```

### Debugging Tips

**Enable Debug Mode:**
```bash
# Streamlit
streamlit run app.py --logger.level=debug

# Flask
export FLASK_DEBUG=1  # Mac/Linux
set FLASK_DEBUG=1  # Windows
python api.py
```

**Check Logs:**
```python
# In app.py or agent.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("Your debug message here")
```

---

## 🗺️ Roadmap

### Version 1.2 (Planned)

- [ ] **PostgreSQL Migration** - Replace SQLite for production scalability
- [ ] **User Roles & Permissions** - Admin, HR, Employee roles
- [ ] **Advanced Ticket Management** - Status updates, comments, file attachments
- [ ] **Calendar Integration** - Google Calendar / Outlook for meetings
- [ ] **Multi-Document Support** - Upload and index multiple PDFs
- [ ] **Voice Input** - Speech-to-text for queries
- [ ] **Multi-Language Support** - i18n for global deployment

### Version 2.0 (Future)

- [ ] **Real Jira Integration** - Sync with enterprise Jira boards
- [ ] **Azure DevOps Integration** - Work items and boards
- [ ] **Machine Learning Classifier** - Fine-tuned model for intent detection
- [ ] **Analytics Dashboard** - Usage metrics, response times, satisfaction scores
- [ ] **Mobile App** - React Native or Flutter
- [ ] **SSO Integration** - SAML/OAuth with corporate identity providers
- [ ] **Custom Workflows** - Visual workflow builder for approvals
- [ ] **Knowledge Base CMS** - Admin panel for document management

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 HCLTech

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 👥 Team & Acknowledgments

**Built with ❤️ by the HCLTech Enterprise AI Team**

### Special Thanks

- **LangChain** - For the amazing RAG framework
- **Groq** - For free access to LLaMA 3.3 70B
- **HuggingFace** - For open-source embeddings
- **Streamlit** - For rapid UI development
- **Meta AI** - For LLaMA models

---

## 📞 Support & Contact

### Getting Help

- 📚 **Documentation**: You're reading it!
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/YOUR_USERNAME/HCLTech-Enterprise-AI-Assistant/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/YOUR_USERNAME/HCLTech-Enterprise-AI-Assistant/discussions)
- 📧 **Email**: support@hcltech.com

### Quick Links

- 🔗 **Groq API**: https://console.groq.com
- 🔗 **LangChain Docs**: https://python.langchain.com
- 🔗 **Streamlit Docs**: https://docs.streamlit.io
- 🔗 **FAISS Docs**: https://faiss.ai

---

## ⭐ Show Your Support

If this project helped you, please consider:

- ⭐ **Starring the repository** on GitHub
- 🍴 **Forking and contributing** improvements
- 📢 **Sharing with your team** and community
- 🐦 **Tweeting about it** with #HCLTechAI

---

<div align="center">

**Made with 🚀 by HCLTech | Powered by AI**

[⬆ Back to Top](#-hcltech-enterprise-ai-assistant)

</div>
