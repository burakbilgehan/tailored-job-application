# tailored-job-application

Upload a CV (.tex or .md) and a job listing → get a tailored cover letter, CV improvement suggestions, and a revised CV.

## Setup

### Backend

```bash
cd backend
cp .env.example .env          # add your ANTHROPIC_API_KEY
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Stack

- **Backend:** Python, FastAPI, Anthropic SDK (`claude-opus-4-6`)
- **Frontend:** React + TypeScript, Vite
