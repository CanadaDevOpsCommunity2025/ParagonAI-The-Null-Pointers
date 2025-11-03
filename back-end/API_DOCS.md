# ParagonAI Agent Deployment Platform - API Documentation

This document provides detailed information about the available API endpoints for managing AI agents in the ParagonAI Agent Deployment Platform.

## Base URL
All API endpoints are prefixed with the base URL: `http://localhost:8000`

## Authentication
*Note: Authentication is not currently implemented in this version.*

## Endpoints

### Test Endpoint

#### Test Agent Router
```
GET /agents/test
```

Verifies that the agents router is functioning correctly.

**Response:**
```json
{
  "message": "Agents router is working!"
}
```

### Agent Templates

#### List All Agent Templates
```
GET /agents/templates
```

Retrieves a list of all available agent templates.

**Response:**
```json
[
  {
    "id": "customer-support-v1",
    "name": "Customer Support Agent",
    "description": "AI agent for handling customer inquiries...",
    "agent_type": "customer_support",
    "framework": "LangChain",
    "use_cases": ["Answer frequently asked questions", ...],
    "default_config": {
      "model": "mixtral-8x7b-32768",
      "temperature": 0.1,
      "max_tokens": 4096,
      "system_prompt": "You are a helpful customer support agent..."
    }
  },
  ...
]
```

#### Get Agent Template by ID
```
GET /agents/templates/{template_id}
```

Retrieves details of a specific agent template by its ID.

**Path Parameters:**
- `template_id` (string, required): The ID of the template to retrieve

**Response:**
```json
{
  "id": "customer-support-v1",
  "name": "Customer Support Agent",
  "description": "AI agent for handling customer inquiries...",
  "agent_type": "customer_support",
  "framework": "LangChain",
  "use_cases": ["Answer frequently asked questions", ...],
  "default_config": {
    "model": "mixtral-8x7b-32768",
    "temperature": 0.1,
    "max_tokens": 4096,
    "system_prompt": "You are a helpful customer support agent..."
  }
}
```

**Error Responses:**
- `404 Not Found`: If no template exists with the specified ID

#### Create New Agent Template
```
POST /agents/templates
```

Creates a new agent template.

**Request Body:**
```json
{
  "id": "new-agent-v1",
  "name": "New Agent",
  "description": "Description of the new agent",
  "agent_type": "customer_support",
  "framework": "LangChain",
  "use_cases": ["Use case 1", "Use case 2"],
  "default_config": {
    "model": "mixtral-8x7b-32768",
    "temperature": 0.1,
    "max_tokens": 4096,
    "system_prompt": "You are a helpful AI assistant."
  }
}
```

**Response:**
Returns the updated list of all agent templates, including the newly created one.

### Agent Configuration

#### Update Agent System Prompt
```
POST /agents/update-template
```

Updates the system prompt for one or all agent templates.

**Request Body:**
```json
{
  "agent_id": "customer-support-v1",
  "system_prompt": "Updated system prompt goes here..."
}
```

**Parameters:**
- `agent_id` (string, optional): ID of the agent to update. If not provided, updates all agents.
- `system_prompt` (string, required): The new system prompt to use.

**Response:**
```json
{
  "status": "success",
  "updated_agents": 1
}
```

**Error Responses:**
- `404 Not Found`: If the specified agent_id doesn't exist
- `500 Internal Server Error`: If there's an error updating the prompt

### Agent Metrics

#### Get Agent Metrics
```
GET /agents/metrics/{deployment_id}
```

Retrieves metrics for a deployed agent.

**Path Parameters:**
- `deployment_id` (string, required): The ID of the deployment to get metrics for

**Response:**
```json
{
  "deployment_id": "deployment-123",
  "request_count": 100,
  "error_count": 5,
  "avg_response_time": 0.5,
  "uptime_percentage": 99.9,
  "last_updated": "2023-01-01T12:00:00Z"
}
```

## Error Handling

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

- `200 OK`: The request was successful
- `201 Created`: Resource was successfully created
- `400 Bad Request`: Invalid request format or parameters
- `404 Not Found`: The requested resource was not found
- `500 Internal Server Error`: An unexpected error occurred on the server

## Rate Limiting
*Note: Rate limiting is not currently implemented in this version.*
