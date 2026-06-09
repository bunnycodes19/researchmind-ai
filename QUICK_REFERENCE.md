# 🚀 ResearchMind AI - Quick Reference Card

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend App** | http://localhost:3000 | Main user interface |
| **Backend API** | http://127.0.0.1:8000 | REST API server |
| **Swagger Docs** | http://127.0.0.1:8000/docs | Interactive API testing |
| **ReDoc** | http://127.0.0.1:8000/redoc | Alternative API docs |

---

## 🔐 Test Accounts

### Pre-created (if DB initialized):
```
Email:    test@researchmind.ai
Password: TestPassword123!
```

### Create Your Own:
```
Any email + password during signup
```

---

## 📋 Testing Checklist

**Phase 1: Authentication (5 min)**
- [ ] Signup
- [ ] Login
- [ ] Access dashboard
- [ ] Logout

**Phase 2: PDF Upload (10 min)**
- [ ] Upload PDF
- [ ] Watch processing
- [ ] Verify in list
- [ ] View metadata

**Phase 3: RAG Q&A (10 min)**
- [ ] Ask 3 questions
- [ ] Check citations
- [ ] Verify answers
- [ ] Try different questions

**Phase 4: Study Tools (10 min)**
- [ ] Generate notes
- [ ] Generate flashcards
- [ ] Generate quiz
- [ ] Try ELI5

**Phase 5: Advanced Features (10 min)**
- [ ] Upload 2nd paper
- [ ] Compare papers
- [ ] Generate literature review
- [ ] Check dashboard stats

---

## 🛠️ Server Commands

### Start Backend
```bash
cd C:\Users\FSSAI\Projects\researchmind-ai\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd C:\Users\FSSAI\Projects\researchmind-ai\frontend
npm run dev
```

### Stop Servers
- Backend: Press `Ctrl+C` in backend terminal
- Frontend: Press `Ctrl+C` in frontend terminal

---

## 📊 Tech Stack

```
Frontend:  Next.js 15 + React 19 + TypeScript + Tailwind
Backend:   FastAPI + SQLAlchemy
AI:        LangChain + Google Gemini
Search:    FAISS vectors
Database:  PostgreSQL (optional)
Auth:      JWT + bcrypt
```

---

## 🧪 API Testing Examples

### Signup
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### Ask Question (requires token)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat/ask" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_id": "<paper_uuid>",
    "question": "What is this paper about?"
  }'
```

---

## 📊 Expected Results

### Signup Success
```json
{
  "id": "uuid",
  "email": "test@example.com",
  "is_active": true
}
```

### Q&A Success
```json
{
  "answer": "This paper proposes...",
  "confidence_score": 0.87,
  "citations": [
    {"page": 5, "section": "Introduction"}
  ],
  "chunks": [
    {"text": "...", "page": 5}
  ]
}
```

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| Frontend blank page | Check F12 console, refresh |
| API 404 errors | Verify backend is running |
| PDF won't upload | Check file size, format |
| Q&A returns empty | Verify PDF processed fully |
| Login fails | Check credentials, DB status |
| Slow responses | Check network, API limits |

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `.env` | Configuration (API keys, DB URL) |
| `backend/app/main.py` | FastAPI entry point |
| `frontend/app/page.tsx` | Next.js home page |
| `backend/app/api/v1/chat.py` | RAG endpoints |
| `backend/app/services/rag.py` | RAG implementation |

---

## 🔄 Data Processing Flow

```
PDF Upload
    ↓
Text Extraction (PyMuPDF)
    ↓
Chunking (1000 chars, 200 overlap)
    ↓
Embedding Generation (Google Gemini)
    ↓
FAISS Storage
    ↓
Ready for Q&A
```

---

## 🎯 Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Signup | <1s | Real-time |
| Login | <1s | Token generation |
| PDF Upload | 5-10s | 10MB file |
| PDF Processing | 10-30s | Depends on size |
| Q&A Response | 2-5s | Includes API call |
| Study Notes | 3-8s | LLM generation |

---

## 🔐 Security Features

- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ CORS protection
- ✅ Rate limiting
- ✅ Input validation
- ✅ Secure file upload
- ✅ SQL injection protection

---

## 📚 Additional Resources

**In this Project:**
- `HOW_TO_RUN.md` - Setup guide
- `REAL_WORLD_TESTING_GUIDE.md` - Full test plan
- `REAL_WORLD_SETUP_COMPLETE.md` - Architecture details

**Online:**
- FastAPI: https://fastapi.tiangolo.com
- Next.js: https://nextjs.org/docs
- Google Gemini: https://ai.google.dev
- SQLAlchemy: https://docs.sqlalchemy.org

---

## 🆘 Get Help

1. **Check Logs:**
   - Backend logs in terminal
   - Frontend logs in browser console (F12)

2. **API Docs:**
   - http://127.0.0.1:8000/docs (Swagger UI)
   - http://127.0.0.1:8000/redoc (ReDoc)

3. **Error Messages:**
   - Read carefully, often contains solution
   - Check troubleshooting guides

4. **Network Requests:**
   - Use browser DevTools (F12)
   - Check request/response in Network tab

---

## ✅ You're Ready!

**Everything is set up and running:**
- ✅ Frontend: http://localhost:3000
- ✅ Backend: http://127.0.0.1:8000
- ✅ Documentation ready
- ✅ Testing guides available

**Start here:** Open http://localhost:3000 in your browser!

---

**Generated:** June 3, 2026  
**Status:** Production Ready ✅
