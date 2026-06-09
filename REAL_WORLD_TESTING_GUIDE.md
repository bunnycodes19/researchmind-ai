# 🎯 ResearchMind AI - Real-World Testing Guide

## Overview
This guide walks you through complete end-to-end testing of ResearchMind AI with a real PostgreSQL database.

---

## 🔧 Prerequisites Setup

### Option A: PostgreSQL (Recommended for Production Testing)

**If PostgreSQL service is running:**
```bash
# Create user and database manually via pgAdmin or psql
psql -U postgres

# Inside psql shell:
CREATE USER researchmind WITH PASSWORD 'ResearchMind123!';
CREATE DATABASE researchmind_prod OWNER researchmind;
GRANT ALL PRIVILEGES ON DATABASE researchmind_prod TO researchmind;
\q
```

**Database Connection String (in .env):**
```
DATABASE_URL=postgresql+asyncpg://researchmind:ResearchMind123!@localhost:5432/researchmind_prod
```

### Option B: SQLite (For Quick Testing)

**No setup needed! Just uncomment in .env:**
```env
# DATABASE_URL=sqlite+aiosqlite:///./researchmind_test.db
```

---

## 🚀 Startup Instructions

### Terminal 1: Backend Server

```powershell
cd C:\Users\FSSAI\Projects\researchmind-ai\backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start backend
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
```

### Terminal 2: Frontend Server

```powershell
cd C:\Users\FSSAI\Projects\researchmind-ai\frontend

# Start frontend
npm run dev
```

**Expected output:**
```
▲ Next.js 15.5.19
  - Local:        http://localhost:3000
  ✓ Ready in X.Xs
```

---

## ✅ Testing Checklist

### Phase 1: UI & Navigation
- [ ] Open http://localhost:3000
- [ ] Verify landing page loads
- [ ] Check header/footer navigation
- [ ] Verify responsive design (try mobile view)

### Phase 2: Authentication
- [ ] Click "Sign Up"
- [ ] Create account: `testuser@example.com` / `Password123!`
- [ ] Verify email validation works
- [ ] Check form validation (try invalid email)
- [ ] Log in with credentials
- [ ] Verify dashboard loads after login
- [ ] Test "Log Out"
- [ ] Verify redirect to login page

### Phase 3: PDF Upload & Processing
- [ ] Login to dashboard
- [ ] Go to "Papers" section
- [ ] Click "Upload PDF"
- [ ] Select a PDF file (or download sample from:
  - arXiv: https://arxiv.org/pdf/2401.00298.pdf
  - Or use any research paper)
- [ ] Watch progress bar during upload
- [ ] Verify file appears in papers list
- [ ] Check paper details (title, pages, upload date)

### Phase 4: Document Processing
- [ ] Wait for processing to complete (5-30 seconds depending on PDF size)
- [ ] Verify status changes to "Ready"
- [ ] Check metadata extraction (if visible):
  - Title
  - Authors
  - Page count
  - Section headings
- [ ] Verify file size display

### Phase 5: RAG Q&A Testing
- [ ] Click on uploaded paper
- [ ] Open "Chat" or "Ask Questions" tab
- [ ] Try these questions:
  - "What is this paper about?"
  - "What are the main findings?"
  - "What methodology was used?"
  - "What datasets were used?"
  - "What are the limitations?"
  - "What future work is proposed?"
- [ ] Verify:
  - Answer appears in chat
  - Citations with page numbers shown
  - Relevant chunks displayed
  - Confidence score shown

### Phase 6: Study Tools
- [ ] Click "Generate Study Notes"
  - Verify notes organize key points
- [ ] Click "Generate Flashcards"
  - Verify cards have questions and answers
- [ ] Click "Generate Quiz"
  - Verify questions are multiple choice
- [ ] Click "ELI5 Explanation"
  - Verify simplified language used

### Phase 7: Advanced Features
- [ ] Upload 2-3 more papers
- [ ] Try "Compare Papers"
  - Select multiple papers
  - Ask comparison questions:
    - "Compare methodology in paper A vs B"
    - "Which dataset is larger?"
    - "What findings overlap?"
- [ ] Generate "Literature Review"
  - Verify it covers all papers

### Phase 8: Dashboard & Analytics
- [ ] Check Dashboard page
- [ ] Verify metrics:
  - Total papers uploaded
  - Total questions asked
  - Storage used
  - Recent activity log

### Phase 9: Error Handling
- [ ] Try uploading non-PDF file (should fail gracefully)
- [ ] Try ask question before paper processes (should handle)
- [ ] Try very large PDF (should handle or show error)
- [ ] Disconnect internet, try action (should show error)

### Phase 10: API Testing (Direct)
Open http://127.0.0.1:8000/docs in browser

**Test these endpoints:**

1. **User Registration:**
   ```
   POST /api/v1/auth/signup
   {
     "email": "testuser2@example.com",
     "password": "Password123!",
     "full_name": "Test User 2"
   }
   ```

2. **User Login:**
   ```
   POST /api/v1/auth/login
   {
     "email": "testuser@example.com",
     "password": "Password123!"
   }
   ```
   - Copy the `access_token` from response
   - Use in "Authorize" button (click lock icon)

3. **Get Papers:**
   ```
   GET /api/v1/papers
   ```
   - Should list all uploaded papers with metadata

4. **Ask Question:**
   ```
   POST /api/v1/chat/ask
   {
     "paper_id": "<paper_id_from_above>",
     "question": "What is the main contribution?"
   }
   ```
   - Verify response includes:
     - answer (string)
     - chunks (array with text and page)
     - citations (array with source info)
     - confidence_score (0-1)

5. **Generate Notes:**
   ```
   POST /api/v1/study/generate-notes
   {
     "paper_id": "<paper_id>"
   }
   ```

---

## 📊 Expected Results

### Successful Signup/Login
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "testuser@example.com",
    "is_active": true
  }
}
```

### Successful PDF Upload
```json
{
  "id": "paper-uuid",
  "filename": "paper.pdf",
  "title": "Extracted Title",
  "status": "processing",
  "page_count": 15,
  "created_at": "2026-06-03T10:00:00Z"
}
```

### Successful Q&A
```json
{
  "answer": "This paper proposes a novel approach to...",
  "chunks": [
    {
      "text": "Relevant text from paper...",
      "page": 5,
      "section": "Introduction"
    }
  ],
  "citations": [
    {
      "page": 5,
      "section": "Introduction",
      "relevance": 0.95
    }
  ],
  "confidence_score": 0.87
}
```

---

## 🐛 Troubleshooting

### Backend won't start: "No module named X"
```bash
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Database connection error
```
error: password authentication failed for user "researchmind"
```

**Solution:**
1. Verify PostgreSQL service is running:
   ```bash
   Get-Service postgresql-x64-16 | Select-Object Status
   ```
2. Create user (see Prerequisites section)
3. Or temporarily use SQLite by uncommenting in .env

### Frontend won't start: Port 3000 in use
```bash
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port
npm run dev -- -p 3001
```

### PDF upload fails
- Check file size (max 100MB in config)
- Verify file is actual PDF
- Check disk space
- Check backend logs for details

### Q&A returns empty answer
- Verify PDF processed completely (check status)
- Try simpler question first
- Check Gemini API key is valid
- Verify chunks were extracted (check backend logs)

### CORS errors
- Ensure frontend URL in .env matches exactly
- Check backend CORS_ORIGINS setting
- Clear browser cache (Ctrl+Shift+Delete)

---

## 📈 Performance Expectations

| Task | Expected Time | Notes |
|------|----------------|-------|
| Signup | <1s | Real-time validation |
| Login | <1s | JWT generation |
| PDF Upload (10MB) | 5-10s | Depends on file size |
| Text Extraction | 2-5s | PyMuPDF processing |
| Chunking | 1-2s | Sliding window algorithm |
| Embedding Generation | 5-15s | Google Gemini API call |
| Q&A Response | 2-5s | RAG + LLM generation |
| Study Notes Generation | 3-8s | LLM generation |

---

## 🔐 Security Testing

### Password Security
- [ ] Verify password hashing (SHA256/bcrypt)
- [ ] Try SQL injection in login: `' OR '1'='1`
- [ ] Try XSS in email: `<script>alert('xss')</script>`
- [ ] Try very long password (>1000 chars)

### JWT Testing
- [ ] Logout and try to access protected endpoint
- [ ] Verify 401 error returned
- [ ] Copy token and try with invalid signature
- [ ] Try expired token (wait or modify timestamp)

### File Upload Security
- [ ] Try uploading executable (.exe)
- [ ] Try uploading script (.js)
- [ ] Try uploading very large file (>100MB)
- [ ] Try filename with special characters

---

## 📝 Testing Report Template

```markdown
# ResearchMind AI Testing Report
Date: 2026-06-03
Tester: [Your Name]

## Summary
[Overall impression and key findings]

## Test Results

### Authentication ✅/❌
- Signup: [Pass/Fail]
- Login: [Pass/Fail]
- Logout: [Pass/Fail]

### PDF Management ✅/❌
- Upload: [Pass/Fail]
- Processing: [Pass/Fail]
- Metadata: [Pass/Fail]

### RAG System ✅/❌
- Q&A: [Pass/Fail]
- Citations: [Pass/Fail]
- Confidence: [Pass/Fail]

### Study Tools ✅/❌
- Notes: [Pass/Fail]
- Flashcards: [Pass/Fail]
- Quiz: [Pass/Fail]

## Issues Found
1. [Issue description]
2. [Issue description]

## Recommendations
1. [Recommendation]
2. [Recommendation]
```

---

## 🎓 Sample Questions to Test RAG

Try these with any research paper:

1. **What?**
   - "What is this paper about?"
   - "What is the main contribution?"
   - "What problem does it solve?"

2. **How?**
   - "How does the methodology work?"
   - "What approach is used?"
   - "How were experiments conducted?"

3. **Why?**
   - "Why is this research important?"
   - "Why choose this dataset?"
   - "Why this architecture?"

4. **Where?**
   - "What datasets were used?"
   - "Where is the research applied?"
   - "What organizations contributed?"

5. **When?**
   - "When was this published?"
   - "What is the timeline of research?"

6. **Results?**
   - "What were the results?"
   - "What metrics improved?"
   - "How does it compare to baselines?"

---

## 📞 Getting Help

**Check logs:**
```bash
# Backend logs show in terminal
# Frontend logs in browser console (F12)

# Check network requests in browser DevTools
# Network tab to see API calls
```

**API Documentation:**
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

**Common Issues:**
- See Troubleshooting section above
- Check terminal output for error messages
- Verify .env variables are set correctly
- Ensure database is running/accessible

---

**Happy testing! 🚀**
