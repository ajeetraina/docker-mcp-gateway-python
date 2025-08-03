# Docker MCP Gateway: Production AI Agent Stack

A complete, production-ready AI agent system using Docker MCP Gateway with multi-agent orchestration, intelligent interceptors, and enterprise security.

## Quick Start

### Prerequisites
- Docker Desktop 4.43+ or Docker Engine with Compose
- GPU support (recommended) or Docker Offload access
- API keys for services you want to use

### 1. Clone and Setup
```bash
git clone https://github.com/your-username/docker-mcp-gateway-production
cd docker-mcp-gateway-production

# Copy and configure secrets
cp .mcp.env.example .mcp.env
```

### 2. Add Your API Keys
Edit `.mcp.env` with your credentials:
```bash
# Required for GitHub analysis
GITHUB_TOKEN=ghp_your_github_personal_access_token

# Required for web search
BRAVE_API_KEY=your_brave_search_api_key

# Optional: For OpenAI models instead of local
OPENAI_API_KEY=sk-your_openai_api_key
```

### 3. Start the Stack
```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 4. Test the Agents
Access the web UI at **http://localhost:3000** or use the API:

```bash
# List available agents
curl http://localhost:7777/agents

# Chat with GitHub analyst
curl -X POST http://localhost:7777/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "github-analyst",
    "message": "Analyze the Docker MCP Gateway repository",
    "tools": ["list_issues", "brave_web_search"]
  }'

# Chat with research assistant
curl -X POST http://localhost:7777/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "research-assistant", 
    "message": "Research the latest trends in AI agent development"
  }'
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   Agent API     │    │  MCP Gateway    │
│   (Port 3000)   │───▶│   (Port 7777)   │───▶│   (Port 8811)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                              ┌─────────▼─────────┐
                                              │ Docker API Socket │
                                              │ Dynamic MCP       │
                                              │ Server Management │
                                              └───────────────────┘
                                                        │
                                    ┌───────────────────┼───────────────────┐
                                    ▼                   ▼                   ▼
                            ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                            │   GitHub    │    │    Brave    │    │  Wikipedia  │
                            │ MCP Server  │    │ MCP Server  │    │ MCP Server  │
                            └─────────────┘    └─────────────┘    └─────────────┘
```

## Available Agents

### GitHub Analyst
- **Model**: qwen3-medium
- **Tools**: GitHub API, web search
- **Purpose**: Repository analysis, issue tracking, strategic insights

### Research Assistant  
- **Model**: qwen3-small
- **Tools**: Web search, Wikipedia, GitHub
- **Purpose**: Comprehensive research across multiple sources

### Content Creator
- **Model**: qwen3-small
- **Tools**: Web search, Wikipedia, file operations
- **Purpose**: Research-based content creation and documentation

## Configuration

### Models
Configure AI models in `docker-compose.yaml`:
```yaml
models:
  qwen3-small:
    model: ai/qwen3:8B-Q4_0    # 4.44 GB
    context_size: 15000        # 7 GB VRAM
  qwen3-medium:
    model: ai/qwen3:14B-Q6_K   # 11.28 GB
    context_size: 15000        # 15 GB VRAM
```

### Agents
Customize agent behaviors in `agents.yaml`:
```yaml
agents:
  your-custom-agent:
    name: "Your Custom Agent"
    model: qwen3-small
    tools:
      - brave_web_search
      - list_issues
    system_prompt: |
      Your custom instructions here...
```

### MCP Servers
Add or remove MCP servers in `docker-compose.yml`:
```yaml
command:
  - --servers=github-official,brave,wikipedia-mcp,your-custom-server
```

## Key Features

### 🔐 Security
- **Docker secrets** for credential management
- **Container isolation** for each MCP server
- **No plaintext secrets** in configuration files

### 🔧 Intelligent Interceptors
- **CSV formatting** for GitHub issues
- **Data transformation** with jq processing
- **Response optimization** for AI consumption




