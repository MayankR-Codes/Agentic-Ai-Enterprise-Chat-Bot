# ✅ FINAL PRE-DEPLOYMENT CHECKLIST

## Phase 1: Configuration Setup ⚙️

- [ ] Python 3.10+ installed
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirement.txt`
- [ ] `.env` file created with required variables
- [ ] `GOOGLE_API_KEY` is valid
- [ ] SMTP credentials configured (if using email)
- [ ] Vector DB exists at `vector_store/faiss_index/`

---

## Phase 2: Component Testing 🧪

### Run Automated Test Suite
```bash
python test_components.py
```

Expected Results:
- [ ] ✅ Imports test PASS
- [ ] ✅ Environment Variables test PASS
- [ ] ✅ Vector Database test PASS
- [ ] ✅ LLM Connection test PASS
- [ ] ✅ Agent test PASS
- [ ] ✅ Tools test PASS
- [ ] ✅ Prompts test PASS

### Run Individual Component Tests
```bash
# Test imports
python -c "import langchain, streamlit, faiss; print('OK')"
- [ ] Output: OK

# Test vector DB
python backend/rag_engine.py
- [ ] Output: ✅ Vector database created successfully

# Test agent
python -c "from backend.agent import get_agent; print(get_agent())"
- [ ] Doesn't crash

# Test tools
python -c "from backend.tools import create_it_ticket; print(create_it_ticket('test'))"
- [ ] Returns ticket dict
```

---

## Phase 3: UI Testing 🎨

### Launch App
```bash
streamlit run app.py
```
- [ ] App starts without errors
- [ ] UI loads in browser at `localhost:8501`
- [ ] Sidebar visible with mode selector
- [ ] User input form visible

### Test Chat Assistant Mode 💬
1. Select "Chat Assistant" in sidebar
2. Enter name: "Test User"
3. Enter email: "test@test.com"

**Test 1: Information Query**
- [ ] Input: "What was the revenue in 2024?"
- [ ] Expected: Answer from PDF + source documents
- [ ] ✅ Verify: Shows document snippets

**Test 2: IT Issue Detection**
- [ ] Input: "The system is broken"
- [ ] Expected: "🚨 Issue Detected: it_issue" box appears
- [ ] ✅ Verify: Issue badge shows

**Test 3: HR Meeting Request**
- [ ] Input: "I need to meet with HR about promotion"
- [ ] Expected: Agent offers to schedule meeting
- [ ] ✅ Verify: Confirmation message

**Test 4: Chat History**
- [ ] Ask: "What was the revenue?"
- [ ] Then: "Tell me more about that"
- [ ] ✅ Verify: Both messages visible in chat

### Test Issue Manager Mode 🛡️
1. Select "Issue Manager" in sidebar

**Test 1: Should Accept Issues**
- [ ] Input: "Create ticket for printer error"
- [ ] Expected: Ticket created successfully
- [ ] ✅ Verify: Ticket ID returned

**Test 2: Should Reject Queries**
- [ ] Input: "What's our company policy?"
- [ ] Expected: "This doesn't appear to be an issue"
- [ ] ✅ Verify: Rejects informational query

### Test Knowledge Base Mode 📚
1. Select "Knowledge Base" in sidebar

**Test 1: Should Return Documents**
- [ ] Input: "Revenue"
- [ ] Expected: Found 3 relevant documents
- [ ] ✅ Verify: Shows document snippets

**Test 2: Should Work Without Issues**
- [ ] Doesn't try to create tickets
- [ ] Only returns document search

### Test Dashboard 📊
1. Check sidebar "Show Dashboard" checkbox
2. Click "Tickets" tab
- [ ] Shows created tickets
- [ ] Shows ticket ID, issue, status, date

3. Click "Meetings" tab
- [ ] Shows scheduled meetings
- [ ] Shows meeting ID, department, status, date

### Test Features
- [ ] Chat history clears when "Clear Chat History" clicked
- [ ] User info persists across queries
- [ ] Error messages are user-friendly
- [ ] Footer text visible (audit info)

---

## Phase 4: Tool Testing 🛠️

### Test Ticket Creation
```python
from backend.tools import create_it_ticket, get_all_tickets

# Create ticket
ticket = create_it_ticket(
    issue="Test printer issue",
    user_name="John Doe",
    user_email="john@test.com"
)
```
- [ ] Returns dict with ticket_id
- [ ] Ticket ID format: TICKET-XXXX
- [ ] Status = "SUBMITTED"

**Check ticket was stored:**
```python
all_tickets = get_all_tickets()
print(all_tickets)
```
- [ ] Ticket appears in list
- [ ] Has all required fields

### Test Meeting Scheduling
```python
from backend.tools import schedule_meeting, get_all_meetings

meeting = schedule_meeting(
    department="HR",
    date="2025-01-20",
    time="10:00",
    reason="Promotion discussion",
    user_name="John Doe",
    user_email="john@test.com"
)
```
- [ ] Returns dict with meeting_id
- [ ] Meeting ID format: MEETING-XXXX
- [ ] Status = "PENDING"

**Check meeting was stored:**
```python
all_meetings = get_all_meetings()
print(all_meetings)
```
- [ ] Meeting appears in list
- [ ] Has all required fields

### Test Email (if SMTP configured)
1. Create a ticket with valid email
2. Check email inbox
- [ ] Confirmation email received
- [ ] Email contains ticket ID
- [ ] Email has professional format
- [ ] Email is from SENDER_EMAIL

### Test Issue Detection
```python
from backend.agent import detect_issue

# Test query detection
result = detect_issue("What's the revenue?")
- [ ] Returns: {"type": "query", ...}

# Test issue detection
result = detect_issue("System is down")
- [ ] Returns: {"type": "issue", ...}

# Test HR detection
result = detect_issue("Need HR meeting")
- [ ] Returns: {"type": "issue", "category": "hr_meeting", ...}
```

---

## Phase 5: Error Handling & Edge Cases 🛡️

### Test Missing Vector DB
```python
# Temporarily rename vector_store
import os
os.rename("vector_store", "vector_store_backup")

# Try to load app
streamlit run app.py
- [ ] Should not crash
- [ ] Shows warning message
- [ ] Can still use Issue Manager mode
- [ ] Query mode shows error

# Restore
os.rename("vector_store_backup", "vector_store")
```

### Test Missing API Key
```python
# Temporarily comment out GOOGLE_API_KEY in .env
# Try to run tests
python test_components.py
- [ ] Should fail with clear error message
- [ ] Suggests checking API key
```

### Test Invalid Inputs
1. Send empty message: ""
- [ ] Shows warning: "Please enter a question"

2. Send very long message (>10000 chars)
- [ ] Either processes or shows limit message

3. Send special characters: "!@#$%^&*()"
- [ ] Doesn't crash
- [ ] Either processes or sanitizes

### Test Concurrent Requests
1. Ask multiple questions quickly
- [ ] Doesn't lose chat history
- [ ] Responses are in order

---

## Phase 6: Performance Testing ⚡

### Test Response Times
1. Ask simple query: "What was the revenue?"
- [ ] Response time: < 10 seconds
- [ ] Usually 2-5 seconds (LLM bottleneck)

2. Create ticket
- [ ] Response time: < 2 seconds
- [ ] Usually < 1 second

3. Schedule meeting
- [ ] Response time: < 2 seconds
- [ ] Usually < 1 second

### Test Memory Usage
```bash
# Monitor memory while running
# Start app and send several messages
streamlit run app.py
- [ ] Memory usage stays reasonable (< 1 GB)
- [ ] No memory leaks over time
```

### Test Vector DB Performance
```python
from backend.rag_engine import load_vector_db

# Time vector DB load
import time
start = time.time()
db = load_vector_db()
end = time.time()
print(f"Load time: {end-start}s")
- [ ] Load time: < 1 second (uses caching)
- [ ] Search time per query: < 100ms
```

---

## Phase 7: Security Review 🔐

- [ ] No API keys hardcoded in source files
- [ ] All secrets in `.env` only
- [ ] `.env` in `.gitignore`
- [ ] User info required before creating issues
- [ ] Email addresses validated
- [ ] No SQL injection possible (using in-memory storage)
- [ ] SMTP uses TLS/SSL
- [ ] Responses don't expose internal errors

---

## Phase 8: Documentation Review 📚

- [ ] README_NEW.md explains features
- [ ] DEPLOYMENT_GUIDE.md has setup instructions
- [ ] CODE_REVIEW_SUMMARY.md explains changes
- [ ] ARCHITECTURE.md shows system design
- [ ] test_components.py has good comments
- [ ] Code is reasonably commented
- [ ] Error messages are helpful

---

## Phase 9: Git & Version Control 🔄

- [ ] `.env` is in `.gitignore`
- [ ] `__pycache__/` is in `.gitignore`
- [ ] `logs/` directory is in `.gitignore`
- [ ] `venv/` is in `.gitignore`
- [ ] All source files are tracked
- [ ] README.md is updated
- [ ] No accidental secrets committed

---

## Phase 10: Final Validation ✅

### Quick Smoke Test
```bash
# Run full test suite
python test_components.py
- [ ] All 7 tests pass

# Start app
streamlit run app.py
- [ ] App loads
- [ ] Chat mode works
- [ ] Issue mode works
- [ ] Knowledge mode works

# Check dashboard
- [ ] Can see tickets
- [ ] Can see meetings
```

### Sign-Off Checklist
- [ ] All tests pass ✅
- [ ] All 3 modes work ✅
- [ ] Error handling works ✅
- [ ] Documentation complete ✅
- [ ] Security reviewed ✅
- [ ] No hardcoded secrets ✅
- [ ] Ready for deployment ✅

---

## Phase 11: Deployment Execution 🚀

Choose your deployment method:

### Option A: Streamlit Cloud (Easiest)
- [ ] Push code to GitHub
- [ ] Connect GitHub to Streamlit Cloud
- [ ] Add `.env` variables in Settings
- [ ] Deploy (automatic on push)
- [ ] Test live URL

### Option B: Docker
- [ ] Create Dockerfile (if needed)
- [ ] Build image: `docker build -t chatbot .`
- [ ] Run container: `docker run -p 8501:8501 chatbot`
- [ ] Test at localhost:8501

### Option C: AWS EC2
- [ ] Launch EC2 instance
- [ ] Install Python, pip, venv
- [ ] Clone repo
- [ ] Set up `.env`
- [ ] Install dependencies
- [ ] Run with systemd/supervisor
- [ ] Configure nginx reverse proxy
- [ ] Test public IP

### Option D: Azure App Service
- [ ] Create App Service
- [ ] Set up GitHub integration
- [ ] Deploy from repo
- [ ] Add application settings (env vars)
- [ ] Test live URL

---

## Phase 12: Post-Deployment 📊

- [ ] Monitor error logs
- [ ] Track response times
- [ ] Monitor memory/CPU usage
- [ ] Collect user feedback
- [ ] Plan improvements
- [ ] Set up alerts

---

## 🎉 YOU'RE READY!

If all checkboxes are checked, your chatbot is:
- ✅ Fully functional
- ✅ Well-tested
- ✅ Documented
- ✅ Secure
- ✅ Ready for production

**Next Step**: Choose deployment method and deploy! 🚀
