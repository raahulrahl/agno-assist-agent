<p align="center">
  <img src="https://raw.githubusercontent.com/getbindu/create-bindu-agent/refs/heads/main/assets/light.svg" alt="bindu Logo" width="200">
</p>

<h1 align="center">Agno Documentation Assistant</h1>
<h3 align="center">AI-Powered Agno Framework Documentation Assistant with RAG</h3>

<p align="center">
  <strong>Provides accurate, documentation-grounded answers about the Agno framework using retrieval-augmented generation (RAG). Searches vector databases with hybrid semantic + keyword search to deliver precise, context-aware responses.</strong><br/>
  Get expert answers about Agno framework, implementation guidance, and code examples from official documentation.
</p>

<p align="center">
  <a href="https://github.com/Paraschamoli/agno-assist-agent/actions/workflows/build-and-push.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/Paraschamoli/agno-assist-agent/build-and-push.yml?branch=main" alt="Build status">
  </a>
  <a href="https://img.shields.io/github/license/Paraschamoli/agno-assist-agent">
    <img src="https://img.shields.io/github/license/Paraschamoli/agno-assist-agent" alt="License">
  </a>
  <a href="https://img.shields.io/badge/python-3.12-blue">
    <img src="https://img.shields.io/badge/python-3.12-blue" alt="Python 3.12">
  </a>
</p>

---

## 🎯 What is Agno Documentation Assistant?

An AI-powered assistant that provides expert guidance on the Agno framework by searching official documentation using retrieval-augmented generation (RAG). Think of it as your personal Agno expert that can answer questions about framework features, implementation patterns, and best practices with documentation-grounded accuracy.

### Key Features
*   **📚 Documentation-Grounded Answers** - Responses based on official Agno documentation, not hallucinations
*   **🔍 Hybrid Search** - Combines semantic and keyword search for precise retrieval
*   **🧠 Conversation Memory** - Maintains context across sessions using Mem0
*   **💻 Code Examples** - Includes relevant code snippets from documentation
*   **⚡ Vector Database** - LanceDB with optional persistence for fast searches
*   **🌐 Up-to-Date Information** - Indexes latest Agno documentation from docs.agno.com
*   **🔧 Developer-Focused** - Answers tailored for developers and technical users

### Built-in Tools
*   **LanceDB** - Vector database for document storage and retrieval
*   **Mem0Tools** - Conversation memory and context management
*   **OpenRouter** - LLM capabilities with various model options
*   **ExaTools** - Optional enhanced search capabilities

### How It Works
1.  **Query Analysis** - Understand your Agno framework question
2.  **Document Search** - Search vector database using hybrid semantic + keyword matching
3.  **Relevant Retrieval** - Get most relevant documentation chunks
4.  **Context Integration** - Combine with conversation history from Mem0
5.  **Answer Generation** - LLM creates accurate answer based on retrieved docs

---

> **🌐 Join the Internet of Agents**
> Register your agent at [bindus.directory](https://bindus.directory) to make it discoverable worldwide and enable agent-to-agent collaboration. **It takes 2 minutes and unlocks the full potential of your agent.**

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Paraschamoli/agno-assist-agent.git
cd agno-assist-agent

# Set up virtual environment with uv
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# OPENROUTER_API_KEY=sk-...      # For OpenRouter LLM (required)
# MEM0_API_KEY=sk-...            # For conversation memory (required)
# EXA_API_KEY=sk-...             # Optional: Enhanced search capabilities
# MODEL_NAME=openai/gpt-4o       # Optional: Model ID for OpenRouter
# ENABLE_VECTOR_DB=true          # Optional: Enable/disable vector database
# VECTOR_DB_PATH=tmp/lancedb     # Optional: Custom path for LanceDB
```

### 3. Run Locally

```bash
# Start the Agno documentation assistant
python -m agno_assist_agent

# Or using uv
uv run python -m agno_assist_agent
```

### 4. Test with Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at: http://localhost:3773
```

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file:

```env
# Required APIs
OPENROUTER_API_KEY=sk-...           # Required for LLM calls
MEM0_API_KEY=sk-...                 # Required for conversation memory

# Optional features
MODEL_NAME=openai/gpt-4o            # Model ID for OpenRouter
EXA_API_KEY=sk-...                  # Optional: Enhanced search
ENABLE_VECTOR_DB=true               # Enable/disable vector database
VECTOR_DB_PATH=tmp/lancedb          # Custom path for LanceDB
```

### Port Configuration
Default port: `3773` (can be changed in `agent_config.json`)

---

## 💡 Usage Examples

### Via HTTP API

```bash
curl -X POST http://localhost:3773/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "How do I create an agent with tools in Agno?"
      }
    ]
  }'
```

### Sample Agno Framework Queries
*   "What is Agno and how do I get started?"
*   "How do I create an agent with tools in Agno?"
*   "What vector databases does Agno support?"
*   "Show me an example of a knowledge base implementation"
*   "How does retrieval-augmented generation work in Agno?"
*   "What are the key features of the Agno framework?"
*   "How do I use hybrid search with LanceDB?"
*   "Can you explain Agno's agent architecture?"
*   "What are the dependencies for an Agno project?"
*   "How do I deploy an Agno agent to production?"

### Expected Response Format

```markdown
# 🤖 Agno Framework Answer

## 🎯 Question: How do I create an agent with tools in Agno?

### 📚 Based on Agno Documentation

To create an agent with tools in Agno, you need to import the necessary classes and configure the agent with tools...

### 💻 Code Example

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    name="Research Assistant",
    model=OpenAIChat(id="gpt-4"),
    tools=[DuckDuckGoTools()],
    instructions="You are a research assistant...",
    markdown=True
)
```

**🔍 Key Points**
*   **Tool Integration:** Agno supports various tools like DuckDuckGo, Exa, and custom tools
*   **Configuration:** Tools are passed as a list to the agent constructor
*   **Flexibility:** You can mix and match different tool types
*   **Documentation:** Always refer to official Agno docs for latest patterns

**📖 Official Documentation Source**
*   Section: "Creating Agents with Tools"
*   Relevance: 92% match
*   Documentation Version: 2024-01-15

Answer provided by Agno Documentation Assistant 🤖
Powered by retrieval-augmented generation (RAG)
Last updated: {current_date}
```

---

## 🐳 Docker Deployment

### Quick Docker Setup

```bash
# Build the image
docker build -t agno-assist-agent .

# Run container
docker run -d \
  -p 3773:3773 \
  -e OPENROUTER_API_KEY=your_openrouter_key \
  -e MEM0_API_KEY=your_mem0_key \
  -e MODEL_NAME=openai/gpt-4o \
  -e ENABLE_VECTOR_DB=true \
  --name agno-assist-agent \
  agno-assist-agent

# Check logs
docker logs -f agno-assist-agent
```

### Docker Compose (Recommended)

`docker-compose.yml`:

```yaml
version: '3.8'
services:
  agno-assist-agent:
    build: .
    ports:
      - "3773:3773"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - MEM0_API_KEY=${MEM0_API_KEY}
      - MODEL_NAME=${MODEL_NAME:-openai/gpt-4o}
      - ENABLE_VECTOR_DB=${ENABLE_VECTOR_DB:-true}
      - VECTOR_DB_PATH=${VECTOR_DB_PATH:-/app/tmp/lancedb}
    volumes:
      - agno_data:/app/tmp
    restart: unless-stopped

volumes:
  agno_data:
```

### Run with Compose

```bash
# Start with compose
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## 📁 Project Structure

```text
agno-assist-agent/
├── agno_assist_agent/
│   ├── skills/
│   │   └── agno-assist/
│   │       ├── skill.yaml          # Skill configuration
│   │       └── __init__.py
│   ├── __init__.py
│   ├── main.py                     # Agent entry point
│   └── agent_config.json           # Agent configuration
├── agent_config.json               # Bindu agent configuration
├── pyproject.toml                  # Python dependencies
├── Dockerfile                      # Multi-stage Docker build
├── docker-compose.yml              # Docker Compose setup
├── README.md                       # This documentation
├── .env.example                    # Environment template
└── tests/                          # Test suite
```

---

## 🔌 API Reference

### Health Check

```bash
GET http://localhost:3773/health
```

**Response:**
```json
{"status": "healthy", "agent": "Agno Documentation Assistant"}
```

### Chat Endpoint

```bash
POST http://localhost:3773/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Your Agno framework question here"}
  ]
}
```

---

## 🧪 Testing

### Local Testing

```bash
# Install test dependencies
uv sync --group dev

# Run tests
pytest tests/

# Test with coverage
pytest --cov=agno_assist_agent tests/
```

### Integration Test

```bash
# Start agent
python -m agno_assist_agent &

# Test API endpoint
curl -X POST http://localhost:3773/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is Agno?"}]}'
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
| :--- | :--- |
| "OPENROUTER_API_KEY required" | Get your key from openrouter.ai/keys |
| "MEM0_API_KEY required" | Get your key from app.mem0.ai |
| "Port 3773 already in use" | Change port in `agent_config.json` or kill the process: `lsof -ti:3773 | xargs kill -9` |
| Docker build fails | Run `docker system prune -a` then `docker-compose build --no-cache` |
| Vector database initialization fails | Set `ENABLE_VECTOR_DB=false` to run without RAG |

---

## 📊 Dependencies

### Core Packages
*   **bindu** - Agent deployment framework
*   **agno** - AI agent framework
*   **lancedb** - Vector database for document storage
*   **openai** - OpenAI client for embeddings
*   **python-dotenv** - Environment management
*   **mem0ai** - Memory operations
*   **pandas** - Data handling for LanceDB

### Development Packages
*   **pytest** - Testing framework
*   **ruff** - Code formatting/linting
*   **pre-commit** - Git hooks

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1.  Fork the repository.
2.  Create a feature branch: `git checkout -b feature/improvement`.
3.  Make your changes following the code style.
4.  Add tests for new functionality.
5.  Commit with descriptive messages.
6.  Push to your fork.
7.  Open a Pull Request.

### Code Style
*   Follow PEP 8 conventions.
*   Use type hints where possible.
*   Add docstrings for public functions.
*   Keep functions focused and small.

---

## 📄 License
MIT License - see LICENSE file for details.

---

## 🙏 Credits & Acknowledgments
*   **Developer:** Paras Chamoli
*   **Framework:** Bindu - Agent deployment platform
*   **Agent Framework:** Agno - AI agent toolkit
*   **Vector Database:** LanceDB - Local vector storage
*   **Memory System:** Mem0 - Conversation memory API
*   **LLM Provider:** OpenRouter - Model access platform

---

## 🔗 Useful Links
*   🌐 [Bindu Directory](https://bindus.directory)
*   📚 [Bindu Docs](https://docs.getbindu.com)
*   🐙 [GitHub](https://github.com/ParasChamoli/agno-assist-agent)
*   📚 [Agno Framework](https://docs.agno.com)
*   💬 [Bindu Community](https://discord.gg/bindu)

<p align="center">
  <strong>Built with ❤️ by Paras Chamoli</strong><br/>
  <em>Helping developers master the Agno framework with AI-powered documentation assistance</em>
</p>

<p align="center">
  <a href="https://github.com/ParasChamoli/agno-assist-agent/stargazers">⭐ Star on GitHub</a> •
  <a href="https://bindus.directory">🌐 Register on Bindu</a> •
  <a href="https://github.com/ParasChamoli/agno-assist-agent/issues">🐛 Report Issues</a>
</p>

<p align="center">
  <em>Note: This agent provides documentation assistance for the Agno framework. It indexes content from docs.agno.com and provides answers based on that documentation. Always verify critical implementation details against official sources.</em>
</p>#   a g n o - a s s i s t - a g e n t  
 
