# agent/app.py
import asyncio
import os
import logging
from typing import Dict, Any, List
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRequest(BaseModel):
    agent_name: str
    message: str
    tools: List[str] = []

class AgentResponse(BaseModel):
    agent_name: str
    response: str
    tools_used: List[str]
    model_used: str

class AIAgentService:
    def __init__(self):
        self.mcp_gateway_url = os.getenv("MCPGATEWAY_URL", "http://mcp-gateway:8811")
        self.model_runner_url = os.getenv("MODEL_RUNNER_URL", "http://model-runner:8080")
        self.agents_config = self.load_agents_config()
        self.session = httpx.AsyncClient(timeout=30.0)
    
    def load_agents_config(self) -> Dict[str, Any]:
        """Load agent configurations from agents.yaml"""
        try:
            with open("/agents.yaml", "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("agents.yaml not found, using default configuration")
            return {
                "agents": {
                    "default": {
                        "name": "Default Agent",
                        "model": "qwen3-small",
                        "tools": ["brave_web_search"],
                        "system_prompt": "You are a helpful AI assistant."
                    }
                }
            }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool through the gateway"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self.session.post(
                f"{self.mcp_gateway_url}/mcp",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def call_model(self, model_name: str, prompt: str, context: str = "") -> str:
        """Call the AI model for inference"""
        payload = {
            "model": model_name,
            "prompt": f"{context}\n\nUser: {prompt}\nAssistant:",
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        try:
            response = await self.session.post(
                f"{self.model_runner_url}/v1/completions",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Error calling model {model_name}: {e}")
            return f"Error generating response: {str(e)}"
    
    async def process_agent_request(self, request: AgentRequest) -> AgentResponse:
        """Process a request using the specified agent"""
        agent_config = self.agents_config["agents"].get(request.agent_name)
        if not agent_config:
            raise HTTPException(404, f"Agent {request.agent_name} not found")
        
        # Determine which tools to use
        available_tools = agent_config.get("tools", [])
        tools_to_use = request.tools if request.tools else available_tools
        
        # Gather context from tools
        tool_context = ""
        tools_used = []
        
        for tool in tools_to_use:
            if tool == "brave_web_search":
                result = await self.call_mcp_tool("brave_web_search", {
                    "query": request.message,
                    "count": 5
                })
                if "error" not in result:
                    tool_context += f"\nWeb Search Results: {result}\n"
                    tools_used.append(tool)
            
            elif tool == "list_issues" and "github" in request.message.lower():
                # Extract repo info from message (simplified)
                result = await self.call_mcp_tool("list_issues", {
                    "owner": "docker",
                    "repo": "mcp-gateway", 
                    "state": "open"
                })
                if "error" not in result:
                    tool_context += f"\nGitHub Issues: {result}\n"
                    tools_used.append(tool)
        
        # Generate response using model
        system_prompt = agent_config.get("system_prompt", "")
        model_name = agent_config.get("model", "qwen3-small")
        
        full_context = f"{system_prompt}\n{tool_context}"
        response_text = await self.call_model(model_name, request.message, full_context)
        
        return AgentResponse(
            agent_name=request.agent_name,
            response=response_text,
            tools_used=tools_used,
            model_used=model_name
        )

# Initialize FastAPI app
app = FastAPI(title="AI Agent Service", version="1.0.0")
agent_service = AIAgentService()
templates = Jinja2Templates(directory="templates")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-agent-service"}

@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentRequest):
    """Chat with a specific agent"""
    return await agent_service.process_agent_request(request)

@app.get("/agents")
async def list_agents():
    """List all available agents"""
    return {"agents": list(agent_service.agents_config["agents"].keys())}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Simple web interface"""
    agents = list(agent_service.agents_config["agents"].keys())
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "agents": agents
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7777)
