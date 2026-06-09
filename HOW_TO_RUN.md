# 🚀 ResearchMind AI - How to Run

## ✅ Current Status

**Both servers are running:**
- **Backend**: http://127.0.0.1:8000 ✅
- **Frontend**: http://localhost:3000 ✅

---

## 🎯 Quick Start (Already Running)

```bash
# Backend is running in one terminal
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Frontend is running in another terminal  
cd frontend
npm run dev
```

Visit:
- **Frontend**: http://localhost:3000
- **Backend Docs**: http://127.0.0.1:8000/docs

---

## 🔧 First Time Setup

### Step 1: Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 16+
- pip & npm

### Step 2: Clone & Navigate
```bash
cd C:\Users\FSSAI\Projects\researchmind-ai
```

### Step 3: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
```

### Step 5: Environment Configuration
Create `.env` in project root with:
```env
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
JWT_SECRET=qwertyuiopasdfghjklzxcvbnm123456
DATABASE_URL=postgresql+asyncpg://researchmind:researchmind_secret@localhost:5432/researchmind
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### Step 6: PostgreSQL Setup (Optional, for full functionality)
```bash
# Create user (run in PostgreSQL psql)
psql -U postgres

# Inside psql:
CREATE USER researchmind WITH PASSWORD 'researchmind_secret';
CREATE DATABASE researchmind OWNER researchmind;
GRANT ALL PRIVILEGES ON DATABASE researchmind TO researchmind;
\q

# Initialize database schema
cd backend
alembic upgrade head
```

### Step 7: Start Services

**Terminal 1 - Backend:**
```bash
cd C:\Users\FSSAI\Projects\researchmind-ai\backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd C:\Users\FSSAI\Projects\researchmind-ai\frontend
npm run dev
```

---

## 📊 API Documentation

**Swagger UI**: http://127.0.0.1:8000/docs

**Available Endpoints:**
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/papers/upload` - Upload PDF
- `GET /api/v1/papers` - List papers
- `POST /api/v1/chat/ask` - Ask RAG question
- `GET /api/v1/dashboard` - Get dashboard stats

---

## 🎨 Frontend Pages

- **Landing Page**: http://localhost:3000
- **Login**: http://localhost:3000/login
- **Signup**: http://localhost:3000/signup
- **Dashboard**: http://localhost:3000/dashboard (requires login)
- **Papers**: http://localhost:3000/papers (requires login)
- **Chat**: http://localhost:3000/chat (requires login)

---

## ⚙️ Tech Stack Verification

### Backend
✅ FastAPI 0.104+
✅ SQLAlchemy 2.0+
✅ LangChain 0.1+
✅ FAISS vector database
✅ Google Gemini API
✅ JWT authentication
✅ Pydantic validation

### Frontend
✅ Next.js 15.5.19
✅ React 19.1.0
✅ TypeScript
✅ Tailwind CSS
✅ TanStack Query
✅ Zustand state management
✅ Framer Motion animations

### Database
⚠️ PostgreSQL 16 (optional for full features)
- Currently running without DB (graceful degradation)
- Auth API works fine without DB
- Chat/RAG requires DB setup

---

## 🐛 Troubleshooting

### Backend won't start: "email-validator not found"
```bash
cd backend
.venv\Scripts\Activate.ps1
pip install email-validator
```

### Backend won't start: "slowapi not found"
```bash
cd backend
.venv\Scripts\Activate.ps1
pip install slowapi
```

### Frontend won't start: "Port 3000 already in use"
```bash
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port
npm run dev -- -p 3001
```

### Backend won't connect to PostgreSQL
- Ensure PostgreSQL service is running
- Check credentials in `.env`
- Run setup commands above to create user/db

### "CORS error" from frontend
- Check `CORS_ORIGINS` in backend `.env`
- Ensure frontend URL matches exactly

---

## 📦 Docker (Alternative)

```bash
# Build and start with Docker Compose
docker-compose up --build

# Services will be available at:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# PostgreSQL: localhost:5432
```

---

## 🔑 API Key Management

**Google Gemini API Key:**
- Currently set to: `YOUR_GOOGLE_API_KEY`
- To replace: Edit `.env` and change `GOOGLE_API_KEY`
- Get new key: https://ai.google.dev

**JWT Secret:**
- Currently set to: `qwertyuiopasdfghjklzxcvbnm123456`
- To regenerate: Run in PowerShell:
```powershell
[Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

---

## 📝 Project Structure

```
researchmind-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── db/              # Database config
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   ├── requirements.txt      # Python dependencies
│   └── .venv/               # Virtual environment
│
├── frontend/
│   ├── app/
│   │   ├── components/      # React components
│   │   ├── pages/           # Next.js pages
│   │   ├── hooks/           # Custom hooks
│   │   └── lib/             # Utilities
│   ├── public/              # Static assets
│   ├── package.json         # NPM dependencies
│   └── next.config.js       # Next.js config
│
├── docker-compose.yml       # Docker setup
├── .env                     # Environment variables
└── HOW_TO_RUN.md           # This file
```

---

## 🎯 Next Steps

1. **Test Frontend**: Visit http://localhost:3000
2. **Test Backend**: Visit http://127.0.0.1:8000/docs
3. **Try Sign Up**: Use any email/password
4. **Upload PDF**: (Requires database setup)
5. **Ask Questions**: (Requires database setup)

---

## 📞 Support

For issues:
1. Check terminal output for error messages
2. Ensure all dependencies are installed
3. Verify environment variables in `.env`
4. Check PostgreSQL service is running (if needed)
5. Review logs in backend terminal

---

**Happy researching! 🚀**
