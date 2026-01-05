# 🚀 DEPLOYMENT GUIDE - HCLTech Enterprise Assistant

## ✅ PRE-DEPLOYMENT CHECKLIST

### 1. **Environment Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirement.txt
```

### 2. **Configuration Files**
Create a `.env` file in the project root:
```env
# Google Gemini API (Required)
GOOGLE_API_KEY=your_api_key_here

# Email Configuration (For ticket/meeting notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
HR_EMAIL=hr@hcltech.com

# Optional
LOG_LEVEL=INFO
```

**How to get Google Gemini API Key:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Copy and paste into `.env`

**How to set up Gmail:**
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password (16-character password)
3. Use that as `SENDER_PASSWORD` (not your regular password)

### 3. **Vector Database Setup**
The FAISS vector DB is already created at `vector_store/faiss_index/`. 
If you need to rebuild it with new documents:

```bash
python backend/rag_engine.py
```

This will:
- Load the PDF from `data/Annual-Report-2024-25.pdf`
- Split into chunks
- Create embeddings using HuggingFace
- Save to FAISS index

---

## 🧪 TESTING BEFORE DEPLOYMENT

### Test 1: Verify Dependencies
```bash
python -c "import langchain, streamlit, faiss; print('✅ All dependencies installed')"
```

### Test 2: Test Vector DB
```bash
python -c "from backend.rag_engine import load_vector_db; db = load_vector_db(); print('✅ Vector DB loaded')"
```

### Test 3: Test Agent
```bash
python -c "from backend.agent import get_agent; agent = get_agent(); print('✅ Agent initialized')"
```

### Test 4: Test Email (Optional)
```python
from backend.tools import send_email
result = send_email("your_email@gmail.com", "Test", "This is a test email")
print("Email sent:", result)
```

### Test 5: Run the App Locally
```bash
streamlit run app.py
```

Then test:
- **Chat Mode**: Ask a general question like "What was the revenue?"
- **Issue Mode**: Type "I have an error in the system"
- **Create Ticket**: Say "Create a ticket for the printer not working"
- **Schedule Meeting**: Say "Schedule a meeting with HR"

---

## 📋 KEY FEATURES TO TEST

1. **Query Resolution (RAG)**
   - Test: Ask "What was the revenue in 2024?"
   - Expected: Answer from the PDF + source documents

2. **Issue Detection**
   - Test: Say "The system is broken"
   - Expected: Should detect as ISSUE and offer to create ticket

3. **Ticket Creation**
   - Test: "Create an IT ticket for my laptop crashing"
   - Expected: Ticket ID generated + confirmation email sent

4. **Meeting Scheduling**
   - Test: "I need to meet with HR about a promotion"
   - Expected: Meeting request ID generated + email to HR

5. **Chat History**
   - Test: Ask multiple questions in sequence
   - Expected: Previous messages should remain visible

---

## 🐳 DOCKER DEPLOYMENT (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirement.txt .
RUN pip install -r requirement.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t hcltech-assistant .
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_key hcltech-assistant
```

---

## ☁️ CLOUD DEPLOYMENT OPTIONS

### **Option 1: Streamlit Cloud (Easiest)**
1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect GitHub repo
4. Set environment variables in Settings
5. Deploy! (automatic on push)

### **Option 2: AWS EC2**
```bash
# On EC2 instance
git clone your-repo
cd your-repo
python -m venv venv
source venv/bin/activate
pip install -r requirement.txt

# Run with systemd
sudo nano /etc/systemd/system/chatbot.service
# Add service config...
sudo systemctl start chatbot
```

### **Option 3: Azure App Service**
```bash
# Deploy using Azure CLI
az webapp up --name hcltech-assistant --resource-group your-rg
```

---

## 🔒 SECURITY CONSIDERATIONS

**Before going to production:**

1. ✅ Move API keys to `.env` (NEVER commit them)
2. ✅ Use environment variables in cloud deployment
3. ✅ Enable user authentication (add login)
4. ✅ Add request throttling/rate limiting
5. ✅ Log all actions for audit trail
6. ✅ Encrypt sensitive data in database
7. ✅ Use HTTPS only in production
8. ✅ Add input validation/sanitization

---

## 📊 MONITORING & LOGGING

Add monitoring to production:

```python
# In app.py (optional)
import logging

logging.basicConfig(
    filename="logs/chatbot.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"User {user_name} asked: {user_input}")
```

---

## 🐛 COMMON ISSUES & FIXES

| Issue | Cause | Fix |
|-------|-------|-----|
| "Vector DB not found" | FAISS index missing | Run `python backend/rag_engine.py` |
| "Google API error" | Invalid API key | Check `.env` file and API key |
| "Email not sending" | Gmail credentials wrong | Use App Password, not regular password |
| "Agent not responding" | LangChain version mismatch | Run `pip install -r requirement.txt --upgrade` |
| "Out of memory" | Large vector DB | Increase server RAM or use smaller embeddings |

---

## ✨ NEXT STEPS AFTER DEPLOYMENT

1. **Add Database**
   - Replace in-memory storage with PostgreSQL/MongoDB
   - Persist tickets and meetings

2. **User Authentication**
   - Add login system
   - Track which user created what

3. **Analytics**
   - Dashboard showing ticket trends
   - Most common issues
   - Response times

4. **Integration**
   - Connect to real HR system
   - Real ticketing system (Jira/Azure DevOps)
   - Calendar API for actual meeting scheduling

5. **ML Improvements**
   - Train custom classifier for issue detection
   - Learn from past interactions
   - Personalized responses

---

## 📞 SUPPORT

For issues or questions:
- Check logs in `logs/` directory
- Review error messages in Streamlit UI
- Test individual components separately
