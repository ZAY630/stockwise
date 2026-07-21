# StockWise Deployment Script
# Run in PowerShell as Administrator
# This deploys backend to Railway + frontend to Vercel

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  StockWise Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendDir = "$PSScriptRoot\apps\backend"
$frontendDir = "$PSScriptRoot\apps\frontend"

# ── Step 1: Deploy Backend to Railway ──────────────────────────────

Write-Host "[1/2] Deploying Backend to Railway..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Openting Railway login in your browser..."
Write-Host "  (If you don't have an account, sign up at railway.app)" -ForegroundColor Gray
Write-Host ""

Push-Location $backendDir

# Login to Railway (opens browser)
npx @railway/cli login

# Create new project
npx @railway/cli init --name stockwise-backend

# Deploy
npx @railway/cli up --detach

Pop-Location

Write-Host ""
Write-Host "  ✅ Backend deployed!" -ForegroundColor Green
Write-Host "  Get the URL: railway.app → your project → Settings → Domains" -ForegroundColor Gray
Write-Host ""

$backendUrl = Read-Host "  Paste your Railway backend URL (e.g., https://stockwise-backend.up.railway.app)"

# ── Step 2: Deploy Frontend to Vercel ───────────────────────────────

Write-Host ""
Write-Host "[2/2] Deploying Frontend to Vercel..." -ForegroundColor Yellow
Write-Host ""

Push-Location $frontendDir

# Set the backend URL as env var
$env:NEXT_PUBLIC_API_URL = $backendUrl

# Deploy to Vercel (opens browser for login)
npx vercel login
npx vercel --prod --env NEXT_PUBLIC_API_URL=$backendUrl

Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend: Check Vercel output above for URL" -ForegroundColor Cyan
Write-Host "  Backend:  $backendUrl" -ForegroundColor Cyan
Write-Host ""
