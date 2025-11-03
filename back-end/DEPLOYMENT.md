# Deployment Guide

## What's Included

This backend contains all functionality needed for AI agent deployment:

### Core Components
- FastAPI REST API server
- MongoDB database integration (Beanie ODM)
- 3 Agent templates (Customer Support, Content Writer, Data Analyst)
- Prompt engineering with OpenAI
- Docker image building
- AWS EKS deployment automation
- Metrics collection and monitoring

### API Endpoints (13 total)
All endpoints are RESTful and client-agnostic:
- Health checks
- Agent template listing
- Code generation from prompts
- Deployment management
- Status and logs
- Metrics and KPIs
- Project code retrieval

## File Structure

```
back-end/
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container build instructions
├── docker-compose.yml         # Local development stack
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── run.sh                    # Startup script
├── README.md                 # Main documentation
└── app/                      # Application code
    ├── config.py             # Settings
    ├── database.py           # MongoDB setup
    ├── models.py             # Database models
    ├── schemas.py            # API schemas
    ├── templates.py          # Agent templates
    ├── routers/              # API routes
    ├── services/             # Business logic
    ├── tasks/                # Background tasks
    └── utils/                # Utilities
```

## Deployment Options

### Option 1: Docker Compose
```bash
docker-compose up -d
```

### Option 2: Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Option 3: Docker Container
```bash
docker build -t paragonai-backend .
docker run -p 8000:8000 --env-file .env paragonai-backend
```

## Environment Setup

Required variables (in `.env`):
- `MONGODB_URL` - MongoDB connection string
- `OPENAI_API_KEY` - OpenAI API key for code generation

Optional variables:
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` - For AWS EKS deployment
- `REDIS_URL` - Redis connection (currently optional)

## Verification

After deployment:
1. Check health: `curl http://localhost:8000/api/v1/health`
2. View API docs: `http://localhost:8000/docs`
3. Test generation: `POST /api/v1/generate` with a prompt

