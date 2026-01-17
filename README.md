# 🤖 HCLTech Enterprise Assistant

An **Agentic AI Chatbot** that intelligently handles both **informational queries** and **action-based requests** (issues, ticket creation, HR meetings).

---

## ✨ **Features**

| Feature | Description |
|---------|-------------|
| 🔍 **Query Answering** | Retrieves answers from company documents using RAG + Vector DB |
| 🚨 **Issue Detection** | Automatically identifies and classifies problems |
| 🎫 **Ticket Creation** | Creates IT support tickets with auto-notification |
| 📅 **Meeting Scheduling** | Schedules HR meetings with email confirmations |
| 💬 **Chat History** | Maintains conversation context across interactions |
| 📊 **Dashboard** | View all tickets and meetings |
| 🔐 **Audit Trail** | Logs all actions with user tracking |
| 🛡️ **Enhanced Security** | Improved authentication with case-insensitive usernames & password validation |
| ✅ **Input Validation** | Comprehensive input validation for all user-facing APIs |
| 🎨 **Enhanced UI** | Improved metrics visibility with better contrast & styling |

---

## � **Recent Updates (v1.1)**

### **Authentication Security Enhancements** 🔐
- **Case-insensitive usernames**: Added `COLLATE NOCASE` to username field for consistent login experience
- **Password validation**: Minimum 8-character password requirement
- **Duplicate user detection**: Better error handling for duplicate username registrations
- **Improved error messages**: More descriptive feedback for login/signup failures

### **API Input Validation** ✅
- **Request validation**: Enhanced `/api/signup` endpoint with input sanitization
- **Field validation**: All required fields checked before processing
- **Error handling**: Improved exception handling with meaningful error messages
- **Type checking**: Email and username format validation

### **Frontend UI Improvements** 🎨
- **Metrics visibility**: Enhanced metric value visibility with white color and better contrast
- **Label styling**: Improved metric labels with muted text colors
- **Dark theme support**: Better styling for dark mode metrics display

---

## �🛠️ **Tech Stack**

- **LLM**: Google Gemini 1.5 Flash (via `langchain-google-genai`)
- **RAG Engine**: LangChain + FAISS Vector DB + HuggingFace Embeddings
- **Framework**: Streamlit (UI)
- **Vector Store**: FAISS (offline, fast)
- **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
- **Tools**: LangChain Agents with ReAct pattern
- **Notifications**: SMTP (Gmail)

---

## 📂 **Project Structure**

```
├── app.py                          # Main Streamlit application
├── requirement.txt                 # Dependencies
├── .env.example                    # Environment template
├── test_components.py              # Pre-deployment tests
├── DEPLOYMENT_GUIDE.md             # Deployment instructions
│
├── backend/
│   ├── agent.py                    # Agent initialization & logic
│   ├── prompts.py                  # System prompts
│   ├── rag_engine.py               # Vector DB management
│   └── tools.py                    # Ticket & Meeting tools
│
├── data/
│   └── Annual-Report-2024-25.pdf   # Knowledge base document
│
└── vector_store/
    └── faiss_index/                # Pre-built vector embeddings
        └── index.faiss
```

---

## 🚀 **Quick Start**

### **1. Clone & Setup**
```bash
git clone <your-repo>
cd Agentic Ai-Enterprise
python -m venv venv

# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### **2. Install Dependencies**
```bash
pip install -r requirement.txt
```

### **3. Configure Environment**
Create `.env` file:
```env
GOOGLE_API_KEY=your_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
HR_EMAIL=hr@hcltech.com
```

**Get Google API Key**: [https://aistudio.google.com/app/apikeys](https://aistudio.google.com/app/apikeys)

### **4. Run Tests**
```bash
python test_components.py
```

Expected output:
```
✅ PASS: Imports
✅ PASS: Environment Variables
✅ PASS: Vector Database
✅ PASS: LLM Connection
✅ PASS: Agent
✅ PASS: Tools
✅ PASS: Prompts

🎉 All tests passed! You're ready to deploy!
```

### **5. Launch the App**
```bash
streamlit run app.py
```

Open browser at `http://localhost:8501`

---

## 🎯 **How It Works**

### **Authentication Flow** (Updated v1.1)

**User Registration**:
```python
# Backend validation in Backend/auth.py
- Check if all fields provided (username, password, full_name, email)
- Validate password length >= 8 characters
- Check for duplicate username (case-insensitive)
- Hash password using bcrypt
- Store in SQLite with COLLATE NOCASE
```

**User Login**:
```python
# Backend/auth.py create_user() & login_user()
- Validate username and password provided
- Query user (case-insensitive due to COLLATE NOCASE)
- Verify password hash
- Return user profile on success
- Descriptive errors on failure
```

**API Endpoint** (`/api/signup`):
```python
# api.py api_signup()
- Validate JSON data provided
- Strip and validate username, password, full_name, email
- Check all fields present
- Create user via Backend/auth.py
- Return JSON response with success status
```

### **Query Flow**
```
User Input
    ↓
[Issue Detection] → Is it a problem?
    ↓                    ↓
   YES                   NO
    ↓                    ↓
[Action Tools]      [RAG System]
    ↓                    ↓
Create Ticket       Vector DB Search
Schedule Meeting    Return Answer + Sources
    ↓                    ↓
Email Notification  Display to User
    ↓
Display Result
```

### **Use Cases**

**1. Informational Query**
```
User: "What was the revenue in 2024?"
Bot: Searches vector DB → "According to page 45, revenue was $2.5B..."
     + Source documents
```

**2. IT Issue**
```
User: "The login system is down"
Bot: Detects ISSUE → Offers to create ticket
     Creates TICKET-1001 → Sends confirmation email
```

**3. HR Meeting**
```
User: "I need to meet with HR about my promotion"
Bot: Detects HR ISSUE → Offers to schedule meeting
     Creates MEETING-2001 → Notifies HR department
```

---

## 📋 **Modes**

The app supports 3 interaction modes:

### **1️⃣ Chat Assistant** (Full AI)
- Uses all tools (RAG + Tickets + Meetings)
- Automatically routes based on query type
- Best for general use

### **2️⃣ Issue Manager** (Action Only)
- Only processes issues
- Creates tickets and meetings
- Rejects informational queries

### **3️⃣ Knowledge Base** (Query Only)
- Only searches documents
- No ticket/meeting creation
- Best for FAQ/documentation

---

## 🔍 **Issue Detection**

The bot automatically detects issues using keyword analysis:

**IT Issues** (keywords):
- error, crash, bug, not working, broken, system down

**HR Issues** (keywords):
- meeting, hr, schedule, appointment, complaint, issue

**Generic Queries**:
- Everything else → RAG search

---

## 📊 **Dashboard**

Access the dashboard from the sidebar:
- **Tickets Tab**: All created support tickets
- **Meetings Tab**: All scheduled meetings
- Sort by status, date, department

---

## 🔐 **Security Features**

✅ User authentication (name + email)
✅ Audit logging (all actions tracked)
✅ Email notifications (confirmation trail)
✅ Environment variables (no hardcoded secrets)
✅ Input validation (sanitization)
✅ SMTP security (TLS/SSL)

---

## 🧪 **Testing**

### **Test Individual Components**
```bash
# Test imports
python -c "import langchain, streamlit, faiss; print('✅ OK')"

# Test vector DB
python -c "from backend.rag_engine import load_vector_db; load_vector_db()"

# Test agent
python -c "from backend.agent import get_agent; get_agent()"

# Full test suite
python test_components.py
```

### **Manual Testing**

1. Start app: `streamlit run app.py`
2. **Test Query**: "What was our revenue?"
3. **Test Issue**: "My computer is broken"
4. **Test Ticket**: "Create a ticket for the printer"
5. **Test Meeting**: "Schedule an HR meeting"
6. **Test Chat**: Ask follow-up questions (should maintain history)

---

## ⚙️ **Configuration**

### **Environment Variables**
```env
# Required
GOOGLE_API_KEY=sk-...

# Email (optional, but recommended)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=bot@hcltech.com
SENDER_PASSWORD=xxxx xxxx xxxx xxxx  # App Password
HR_EMAIL=hr@hcltech.com

# Logging (optional)
LOG_LEVEL=INFO
LOG_FILE=logs/chatbot.log
```

### **Adjust Retriever**
In `agent.py`, modify retriever search:
```python
retriever = vector_db.as_retriever(search_kwargs={"k": 5})  # Increase from 3
```

### **Change Model**
In `agent.py`:
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # Use newest model
    temperature=0.5,            # More creative
)
```

---

## 🚀 **Deployment**

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for:
- ✅ Pre-deployment checklist
- 🧪 Testing procedures
- 🐳 Docker containerization
- ☁️ Cloud deployment (Streamlit Cloud, AWS, Azure)
- 🔒 Production security

---

## 🐛 **Troubleshooting**

| Problem | Solution |
|---------|----------|
| "Vector DB not found" | Run: `python backend/rag_engine.py` |
| "Invalid API key" | Check `.env` file format |
| "Agent not responding" | Check LangChain version compatibility |
| "Emails not sending" | Use Gmail App Password (not regular password) |
| "Out of memory" | Reduce `search_kwargs["k"]` or increase server RAM |

---

## 📈 **Roadmap**

- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] User authentication & role management
- [ ] Real Jira/Azure DevOps integration
- [ ] Calendar API for actual meeting scheduling
- [ ] Custom ML classifier for issue detection
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Voice chat support

---

## 📞 **Support**

For issues:
1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Run: `python test_components.py`
3. Review logs in `logs/` directory
4. Check `.env` configuration

---

## 📄 **License**

Proprietary - HCLTech Internal Use Only

---

## 👥 **Contributors**

Built with ❤️ for HCLTech Enterprise

---

**Ready to deploy?** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) ↗️
