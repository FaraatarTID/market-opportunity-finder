@echo off
echo Starting Market Opportunity Finder...

echo Starting Backend...
start "Backend" cmd /k "cd backend && python -m uvicorn main:app --reload"

echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo App started!
