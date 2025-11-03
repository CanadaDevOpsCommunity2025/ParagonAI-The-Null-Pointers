# ParagonAI Backend

FastAPI backend for AI agent deployment and management.

## Features

- **3 Agent Templates**: Customer Support, Content Writer, Data Analyst
- **Prompt Engineering**: Advanced GenAI-powered code generation
- **AWS EKS Deployment**: Automated deployment to Kubernetes
- **Metrics Tracking**: Performance monitoring and KPIs
- **REST API**: Full RESTful API for agent management

## Quick Start

### Using Docker Compose (Recommended)

```bash
# From back-end directory
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MongoDB:**
   ```bash
   # Ensure MongoDB is running
   # macOS: brew services start mongodb-community
   # Linux: sudo systemctl start mongod
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (at minimum: OPENAI_API_KEY)
   ```

4. **Run the server:**
   ```bash
   python main.py
   # Or
   uvicorn main:app --reload
   ```

## API Endpoints

### Health
- `GET /api/v1/health` - Health check

### Agents
- `GET /api/v1/agents` - List available agent templates

### Generation
- `POST /api/v1/generate` - Generate agent code from prompt

### Deployments
- `POST /api/v1/deploy` - Deploy an agent
- `GET /api/v1/deployments` - List all deployments
- `GET /api/v1/deployments/{id}/status` - Get deployment status
- `GET /api/v1/deployments/{id}/logs` - Get deployment logs
- `DELETE /api/v1/deployments/{id}` - Delete deployment

### Metrics
- `GET /api/v1/metrics/{deployment_id}` - Get metrics history
- `GET /api/v1/metrics/{deployment_id}/kpis` - Get KPIs
- `GET /api/v1/deployments/{deployment_id}/code` - Get project code
- `GET /api/v1/deployments/{deployment_id}/code/diff` - Get code differences

## Project Structure

```
back-end/
├── app/
│   ├── models.py          # Database models (MongoDB/Beanie)
│   ├── schemas.py         # Pydantic schemas
│   ├── config.py          # Configuration
│   ├── database.py        # Database setup
│   ├── templates.py       # Agent templates
│   ├── routers/           # API routes
│   │   ├── health.py
│   │   ├── agents.py
│   │   ├── generate.py
│   │   ├── deployments.py
│   │   └── metrics.py
│   ├── services/          # Business logic
│   │   ├── prompt_engineer.py
│   │   ├── deployment_service.py
│   │   ├── docker_service.py
│   │   ├── ecr_service.py
│   │   ├── health_checker.py
│   │   └── metrics_service.py
│   ├── tasks/             # Background tasks
│   │   └── metrics_collector.py
│   └── utils/
│       └── genagent_core.py
├── main.py                # Application entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Environment Variables

Required in `.env`:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=paragonai

# OpenAI (required for code generation)
OPENAI_API_KEY=your-openai-api-key-here

# AWS (optional, for EKS deployment)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_EKS_CLUSTER_NAME=paragonai-cluster

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

## Database Schema (MongoDB)

Collections:
- **deployments**: Stores deployment configurations and status
- **metrics**: Stores performance metrics and KPIs

Documents are automatically created using Beanie ODM.

## Development

```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# View API docs
# Open http://localhost:8000/docs
```

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
