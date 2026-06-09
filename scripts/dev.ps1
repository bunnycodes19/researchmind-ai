# Local development startup (Windows)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example — set GOOGLE_API_KEY and JWT_SECRET"
}

docker compose up postgres -d
Write-Host "Postgres started. Run backend and frontend in separate terminals:"
Write-Host "  cd backend; python -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt; uvicorn app.main:app --reload"
Write-Host "  cd frontend; npm run dev"
