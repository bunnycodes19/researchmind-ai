#=====================================================
# RESEARCHMIND AI - REAL-WORLD TESTING SETUP SCRIPT
#=====================================================
# This script sets up everything for full E2E testing

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  RESEARCHMIND AI - REAL-WORLD SETUP SCRIPT            ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Configuration
$projectRoot = $PSScriptRoot
$backendDir = "$projectRoot\backend"
$frontendDir = "$projectRoot\frontend"
$pgUser = "researchmind"
$pgPassword = "ResearchMind123!"
$pgDatabase = "researchmind_prod"
$pgHost = "localhost"

# Colors
$success = "Green"
$error = "Red"
$warning = "Yellow"
$info = "Cyan"

function Log-Success { Write-Host "✅ $args" -ForegroundColor $success }
function Log-Error { Write-Host "❌ $args" -ForegroundColor $error }
function Log-Warning { Write-Host "⚠️  $args" -ForegroundColor $warning }
function Log-Info { Write-Host "ℹ️  $args" -ForegroundColor $info }
function Log-Step { Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $info; Write-Host "📍 $args" -ForegroundColor $info }

#=====================================================
# STEP 1: VERIFY PREREQUISITES
#=====================================================
Log-Step "STEP 1: Verifying Prerequisites"

# Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) { Log-Success "Python: $pythonVersion" } else { Log-Error "Python not found"; exit 1 }

# Check Node.js
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) { Log-Success "Node.js: $nodeVersion" } else { Log-Error "Node.js not found"; exit 1 }

# Check PostgreSQL
$pgVersion = & "C:\Program Files\PostgreSQL\16\bin\psql.exe" --version 2>&1
if ($LASTEXITCODE -eq 0) { Log-Success "PostgreSQL: $pgVersion" } else { Log-Error "PostgreSQL not found"; exit 1 }

Write-Host ""

#=====================================================
# STEP 2: CREATE POSTGRESQL USER & DATABASE
#=====================================================
Log-Step "STEP 2: Creating PostgreSQL User & Database"

# Create SQL script to run
$sqlScript = @"
-- Create user
DO $`$`$ BEGIN
  CREATE USER $pgUser WITH PASSWORD '$pgPassword';
EXCEPTION WHEN DUPLICATE_OBJECT THEN
  ALTER USER $pgUser WITH PASSWORD '$pgPassword';
END
$`$`$;

-- Create database
SELECT 'CREATE DATABASE $pgDatabase' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$pgDatabase')\gexec

-- Grant privileges
ALTER DATABASE $pgDatabase OWNER TO $pgUser;
GRANT ALL PRIVILEGES ON DATABASE $pgDatabase TO $pgUser;

-- Grant schema privileges
GRANT USAGE ON SCHEMA public TO $pgUser;
GRANT CREATE ON SCHEMA public TO $pgUser;
"@

Write-Host ""
Log-Info "PostgreSQL Password: $pgPassword"
Log-Info "Username: $pgUser"
Log-Info "Database: $pgDatabase"
Write-Host ""
Log-Info "Running SQL setup (you may be prompted for postgres password)..."

# Create temp SQL file
$sqlFile = "$env:TEMP\researchmind_setup.sql"
$sqlScript | Out-File -FilePath $sqlFile -Encoding UTF8

# Run the SQL
try {
    $env:PGPASSWORD = 'postgres'
    & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h $pgHost -f $sqlFile 2>&1 | Where-Object { $_ -notmatch "^Password:" }
    Remove-Item env:PGPASSWORD -ErrorAction SilentlyContinue
    Log-Success "PostgreSQL user and database created"
} catch {
    Remove-Item env:PGPASSWORD -ErrorAction SilentlyContinue
    Log-Warning "Database creation had issues (may already exist): $_"
}

Remove-Item $sqlFile -Force -ErrorAction SilentlyContinue

Write-Host ""

#=====================================================
# STEP 3: UPDATE ENVIRONMENT CONFIGURATION
#=====================================================
Log-Step "STEP 3: Updating .env Configuration"

$envFile = "$projectRoot\.env"
$newEnv = @"
# Google Gemini API
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY

# Database Configuration - PRODUCTION READY
DATABASE_URL=postgresql+asyncpg://$pgUser`:$pgPassword@$pgHost`:5432/$pgDatabase

# JWT Configuration
JWT_SECRET=qwertyuiopasdfghjklzxcvbnm123456
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=30

# Server Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:8000"]

# File Upload Configuration
MAX_UPLOAD_SIZE_MB=100
UPLOAD_DIRECTORY=./uploads

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_CHUNKS=5
MIN_CONFIDENCE_SCORE=0.3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Feature Flags
ENABLE_VECTOR_STORE=true
ENABLE_HALLUCINATION_CHECK=true
ENABLE_CITATION_TRACKING=true
"@

$newEnv | Out-File -FilePath $envFile -Encoding UTF8 -Force
Log-Success ".env updated with production database configuration"
Write-Host ""

#=====================================================
# STEP 4: INSTALL BACKEND DEPENDENCIES
#=====================================================
Log-Step "STEP 4: Installing Backend Dependencies"

Push-Location $backendDir

# Activate venv
& ".\.venv\Scripts\Activate.ps1"

# Upgrade pip
Log-Info "Upgrading pip..."
python -m pip install --upgrade pip -q

# Install requirements
Log-Info "Installing Python packages..."
pip install -r requirements.txt -q

Log-Success "Backend dependencies installed"

Pop-Location
Write-Host ""

#=====================================================
# STEP 5: INSTALL FRONTEND DEPENDENCIES
#=====================================================
Log-Step "STEP 5: Installing Frontend Dependencies"

Push-Location $frontendDir

Log-Info "Installing npm packages..."
npm install --quiet

Log-Success "Frontend dependencies installed"

Pop-Location
Write-Host ""

#=====================================================
# STEP 6: RUN DATABASE MIGRATIONS
#=====================================================
Log-Step "STEP 6: Running Database Migrations"

Push-Location $backendDir

& ".\.venv\Scripts\Activate.ps1"

Log-Info "Running Alembic migrations..."
try {
    alembic upgrade head 2>&1 | Select-String "Running upgrade|Upgrading" -ErrorAction SilentlyContinue
    Log-Success "Database migrations completed"
} catch {
    Log-Warning "Migration had issues: $_"
}

Pop-Location
Write-Host ""

#=====================================================
# STEP 7: VERIFY DATABASE CONNECTION
#=====================================================
Log-Step "STEP 7: Verifying Database Connection"

Push-Location $backendDir

& ".\.venv\Scripts\Activate.ps1"

Log-Info "Testing database connection..."
$pythonTest = @"
import asyncio
from app.db.session import AsyncSessionLocal
async def test_db():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT 1")
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
asyncio.run(test_db())
"@

$pythonTest | python
Pop-Location
Write-Host ""

#=====================================================
# STEP 8: CREATE TEST DATA
#=====================================================
Log-Step "STEP 8: Creating Sample Test Data"

Push-Location $backendDir

& ".\.venv\Scripts\Activate.ps1"

Log-Info "Seeding test data..."
$seedScript = @"
import asyncio
from app.models.user import User
from app.db.session import AsyncSessionLocal
from app.core.security import hash_password

async def seed_test_user():
    async with AsyncSessionLocal() as session:
        try:
            # Create test user
            test_user = User(
                email="test@researchmind.ai",
                full_name="Test User",
                hashed_password=hash_password("TestPassword123!"),
                is_active=True,
                is_superuser=False
            )
            session.add(test_user)
            await session.commit()
            print("✅ Test user created: test@researchmind.ai / TestPassword123!")
        except Exception as e:
            print(f"ℹ️  Test user may already exist: {e}")

asyncio.run(seed_test_user())
"@

$seedScript | python

Pop-Location
Write-Host ""

#=====================================================
# FINAL SUMMARY
#=====================================================
Log-Step "SETUP COMPLETE!"

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║           🎉 SETUP SUCCESSFUL - READY FOR TESTING      ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📊 DATABASE INFORMATION:" -ForegroundColor Yellow
Write-Host "   Host:     $pgHost" -ForegroundColor Cyan
Write-Host "   Database: $pgDatabase" -ForegroundColor Cyan
Write-Host "   User:     $pgUser" -ForegroundColor Cyan
Write-Host "   Password: $pgPassword" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔐 TEST CREDENTIALS:" -ForegroundColor Yellow
Write-Host "   Email:    test@researchmind.ai" -ForegroundColor Cyan
Write-Host "   Password: TestPassword123!" -ForegroundColor Cyan
Write-Host ""

Write-Host "🚀 START SERVERS:" -ForegroundColor Yellow
Write-Host "   Terminal 1 (Backend):" -ForegroundColor White
Write-Host "      cd $backendDir" -ForegroundColor Cyan
Write-Host "      .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "      uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Terminal 2 (Frontend):" -ForegroundColor White
Write-Host "      cd $frontendDir" -ForegroundColor Cyan
Write-Host "      npm run dev" -ForegroundColor Cyan
Write-Host ""

Write-Host "🌐 ACCESS POINTS:" -ForegroundColor Yellow
Write-Host "   Frontend:        http://localhost:3000" -ForegroundColor Green
Write-Host "   Backend API:     http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "   Swagger Docs:    http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "   ReDoc Docs:      http://127.0.0.1:8000/redoc" -ForegroundColor Green
Write-Host ""

Write-Host "📝 TESTING CHECKLIST:" -ForegroundColor Yellow
Write-Host "   ☐ Visit http://localhost:3000" -ForegroundColor White
Write-Host "   ☐ Login with test@researchmind.ai / TestPassword123!" -ForegroundColor White
Write-Host "   ☐ Upload a PDF (samples/paper1.pdf)" -ForegroundColor White
Write-Host "   ☐ Wait for PDF processing (text extraction → chunking → embeddings)" -ForegroundColor White
Write-Host "   ☐ Ask a question about the paper" -ForegroundColor White
Write-Host "   ☐ Verify RAG returns relevant chunks + citations" -ForegroundColor White
Write-Host "   ☐ Generate study notes / flashcards" -ForegroundColor White
Write-Host "   ☐ Test literature review generation" -ForegroundColor White
Write-Host ""

Write-Host "📊 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Open 2 PowerShell terminals" -ForegroundColor White
Write-Host "   2. Run the commands in 'START SERVERS' section above" -ForegroundColor White
Write-Host "   3. Follow the testing checklist" -ForegroundColor White
Write-Host "   4. Check logs for any errors" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
