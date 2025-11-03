"""
Agent templates for different agent types
"""

from app.models import AgentType


def get_agent_template(agent_type: AgentType | str) -> str:
    """Get base template code for agent type"""
    agent_type_str = agent_type.value if isinstance(agent_type, AgentType) else agent_type
    
    templates = {
        AgentType.CUSTOMER_SUPPORT.value: """from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional
import time
from datetime import datetime

app = FastAPI(title="Customer Support Agent API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

# Metrics tracking
metrics = {
    "request_count": 0,
    "success_count": 0,
    "error_count": 0,
    "response_times": []
}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    '''Process customer support messages'''
    start_time = time.time()
    metrics["request_count"] += 1
    
    try:
        # TODO: Integrate with LangChain customer support agent
        response_text = f"I understand you need help with: {request.message}. How can I assist you?"
        
        metrics["success_count"] += 1
        response_time = (time.time() - start_time) * 1000
        metrics["response_times"].append(response_time)
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id or "default",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        metrics["error_count"] += 1
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    '''Health check endpoint'''
    return {"status": "healthy", "service": "customer-support-agent"}

@app.get("/metrics")
async def get_metrics():
    '''Get service metrics'''
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0
    return {
        **metrics,
        "average_response_time_ms": avg_time
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""",
        
        AgentType.CONTENT_WRITER.value: """from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional
import time
from datetime import datetime

app = FastAPI(title="Content Writer Agent API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ContentRequest(BaseModel):
    prompt: str
    content_type: Optional[str] = "blog"
    length: Optional[int] = 500

class ContentResponse(BaseModel):
    content: str
    word_count: int
    timestamp: str

metrics = {
    "request_count": 0,
    "success_count": 0,
    "error_count": 0,
    "response_times": []
}

@app.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    '''Generate content based on prompt'''
    start_time = time.time()
    metrics["request_count"] += 1
    
    try:
        # TODO: Integrate with CrewAI content writer
        generated_content = f"Generated {request.content_type} content about: {request.prompt}"
        
        metrics["success_count"] += 1
        response_time = (time.time() - start_time) * 1000
        metrics["response_times"].append(response_time)
        
        return ContentResponse(
            content=generated_content,
            word_count=len(generated_content.split()),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        metrics["error_count"] += 1
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "content-writer-agent"}

@app.get("/metrics")
async def get_metrics():
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0
    return {
        **metrics,
        "average_response_time_ms": avg_time
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""",
        
        AgentType.DATA_ANALYST.value: """from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional, List, Dict, Any
import time
from datetime import datetime

app = FastAPI(title="Data Analyst Agent API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class AnalysisRequest(BaseModel):
    query: str
    data_source: Optional[str] = None
    analysis_type: Optional[str] = "summary"

class AnalysisResponse(BaseModel):
    insights: List[str]
    summary: str
    timestamp: str
    charts: Optional[List[Dict[str, Any]]] = None

metrics = {
    "request_count": 0,
    "success_count": 0,
    "error_count": 0,
    "response_times": []
}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest):
    '''Analyze data and provide insights'''
    start_time = time.time()
    metrics["request_count"] += 1
    
    try:
        # TODO: Integrate with AutoGen data analyst
        insights = [
            f"Analysis of: {request.query}",
            "Key trend identified",
            "Recommendation provided"
        ]
        
        metrics["success_count"] += 1
        response_time = (time.time() - start_time) * 1000
        metrics["response_times"].append(response_time)
        
        return AnalysisResponse(
            insights=insights,
            summary=f"Analysis complete for: {request.query}",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        metrics["error_count"] += 1
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "data-analyst-agent"}

@app.get("/metrics")
async def get_metrics():
    avg_time = sum(metrics["response_times"]) / len(metrics["response_times"]) if metrics["response_times"] else 0
    return {
        **metrics,
        "average_response_time_ms": avg_time
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    }
    
    return templates.get(agent_type_str, templates[AgentType.CUSTOMER_SUPPORT.value])


def get_requirements_template(agent_type: AgentType | str) -> str:
    """Get requirements.txt for agent type"""
    agent_type_str = agent_type.value if isinstance(agent_type, AgentType) else agent_type
    
    base_deps = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
redis==5.0.1
requests==2.31.0
"""
    
    agent_specific = {
        AgentType.CUSTOMER_SUPPORT.value: "langchain==0.1.0\nlangchain-openai==0.0.2\nopenai==1.3.5",
        AgentType.CONTENT_WRITER.value: "crewai==0.1.0\nlangchain==0.1.0\nopenai==1.3.5",
        AgentType.DATA_ANALYST.value: "pyautogen==0.2.0\npandas==2.1.3\nnumpy==1.26.2\nopenai==1.3.5"
    }
    
    return base_deps + agent_specific.get(agent_type_str, "openai==1.3.5")

