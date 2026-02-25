# |---------------------------------------------------------|
# |                                                         |
# |                 Give Feedback / Get Help                |
# | https://github.com/getbindu/Bindu/issues/new/choose    |
# |                                                         |
# |---------------------------------------------------------|
#
#  Thank you users! We ❤️ you! - 🌻

"""agno-assist-agent - A Bindu Agent for Agno documentation assistance."""

import argparse
import asyncio
import json
import os
from pathlib import Path
from textwrap import dedent
from typing import Any

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.models.openrouter import OpenRouter
from agno.tools.mem0 import Mem0Tools
from agno.vectordb.lancedb import LanceDb, SearchType
from bindu.penguin.bindufy import bindufy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global instances
agent: Agent | None = None
knowledge: Knowledge | None = None
model_name: str | None = None
mem0_api_key: str | None = None
_initialized: bool = False
_init_lock = asyncio.Lock()


class APIKeyError(ValueError):
    """Exception raised when an API key is missing."""


class LocalEmbedder:
    """Local embedder compatible with Agno's Knowledge class.

    This embedder creates simple frequency-based embeddings without requiring
    any external API keys. It produces 1536-dimensional vectors to match
    OpenAI's embedding dimensions.
    """

    def __init__(self, dimensions: int = 1536) -> None:
        """Initialize the local embedder with specified dimensions.

        Args:
            dimensions: The output dimension of the embeddings (default: 1536)
        """
        self.dimensions = dimensions
        self.enable_batch = True
        print(f"🔧 Using local embedder (no API key required) - {dimensions} dims")

    def _simple_embed(self, text: str) -> list[float]:
        """Create a simple but deterministic embedding based on character frequencies.

        Args:
            text: The input text to embed

        Returns:
            A normalized vector of floats with length self.dimensions
        """
        if not text or not isinstance(text, str):
            return [0.0] * self.dimensions

        text = text.lower()
        embedding = []
        # Expanded character set for better distribution
        chars = "abcdefghijklmnopqrstuvwxyz0123456789 .,!?-:;\"'()[]{}<>@#$%^&*+=/\\|~`"
        for char in chars:
            embedding.append(text.count(char) / max(1, len(text)))

        # Repeat pattern to reach required dimensions if needed
        if len(embedding) < self.dimensions:
            # Repeat the pattern to fill to required dimensions
            repeats = (self.dimensions // len(embedding)) + 1
            embedding = (embedding * repeats)[: self.dimensions]
        else:
            embedding = embedding[: self.dimensions]

        # Normalize the embedding
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    def get_embedding(self, text: str) -> list[float]:
        """Get embedding for a single text (synchronous).

        Args:
            text: The input text to embed

        Returns:
            A vector embedding of the text
        """
        return self._simple_embed(text)

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for multiple texts (synchronous).

        Args:
            texts: List of input texts to embed

        Returns:
            List of vector embeddings
        """
        return [self._simple_embed(text) for text in texts]

    async def aget_embedding(self, text: str) -> list[float]:
        """Get embedding for a single text (asynchronous).

        Args:
            text: The input text to embed

        Returns:
            A vector embedding of the text
        """
        return self.get_embedding(text)

    async def aget_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for multiple texts (asynchronous).

        Args:
            texts: List of input texts to embed

        Returns:
            List of vector embeddings
        """
        return self.get_embeddings(texts)

    async def async_get_embedding_and_usage(self, text: str) -> tuple[list[float], dict]:
        """Get embedding and usage info (required by Agno).

        Args:
            text: The input text to embed

        Returns:
            A tuple containing the embedding vector and usage metadata
        """
        embedding = await self.aget_embedding(text)
        return embedding, {"prompt_tokens": 0, "total_tokens": 0}


def load_config() -> dict:
    """Load agent configuration from project root.

    Returns:
        Dictionary containing agent configuration
    """
    possible_paths = [
        Path(__file__).parent.parent / "agent_config.json",
        Path(__file__).parent / "agent_config.json",
        Path.cwd() / "agent_config.json",
    ]

    for config_path in possible_paths:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error reading {config_path}: {e}")
                continue

    return {
        "name": "agno-assist-agent",
        "description": "AI assistant for Agno framework documentation using retrieval-augmented generation (RAG)",
        "version": "1.0.0",
        "deployment": {
            "url": "http://127.0.0.1:3773",
            "expose": True,
            "protocol_version": "1.0.0",
            "proxy_urls": ["127.0.0.1"],
            "cors_origins": ["*"],
        },
        "environment_variables": [
            {
                "key": "OPENROUTER_API_KEY",
                "description": "OpenRouter API key for LLM calls (required)",
                "required": True,
            },
            {
                "key": "MODEL_NAME",
                "description": "Model ID for OpenRouter (default: openai/gpt-4o)",
                "required": False,
            },
            {
                "key": "MEM0_API_KEY",
                "description": "Mem0 API key for conversation memory (required)",
                "required": True,
            },
            {
                "key": "ENABLE_VECTOR_DB",
                "description": "Enable LanceDB vector database for documentation (default: true)",
                "required": False,
            },
            {
                "key": "VECTOR_DB_PATH",
                "description": "Custom path for LanceDB (default: tmp/lancedb)",
                "required": False,
            },
        ],
    }


def _get_api_keys() -> tuple[str | None, str | None, str]:
    """Get API keys and configuration from environment.

    Returns:
        Tuple of (openrouter_api_key, mem0_api_key, model_name)
    """
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    mem0_api_key = os.getenv("MEM0_API_KEY")
    model_name = os.getenv("MODEL_NAME", "openai/gpt-4o")
    return openrouter_api_key, mem0_api_key, model_name


def _create_llm_model(openrouter_api_key: str, model_name: str) -> OpenRouter:
    """Create and return the OpenRouter model.

    Args:
        openrouter_api_key: The OpenRouter API key
        model_name: The model identifier

    Returns:
        Configured OpenRouter model instance

    Raises:
        APIKeyError: If openrouter_api_key is missing
    """
    if not openrouter_api_key:
        error_msg = (
            "OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.\n"
            "Get an API key from: https://openrouter.ai/keys"
        )
        raise APIKeyError(error_msg)

    return OpenRouter(
        id=model_name,
        api_key=openrouter_api_key,
    )


async def _setup_knowledge_base() -> Knowledge | None:
    """Set up the vector database knowledge base for documentation.

    Returns:
        Knowledge instance if successful, None otherwise
    """
    enable_vector_db = os.getenv("ENABLE_VECTOR_DB", "true").lower() in ("true", "1", "yes")

    if not enable_vector_db:
        print("⚠️  Vector database disabled. Agent will answer without document retrieval.")
        return None

    vector_db_path = os.getenv("VECTOR_DB_PATH", "tmp/lancedb")

    try:
        # Create knowledge base with hybrid search using local embeddings
        knowledge_instance = Knowledge(
            vector_db=LanceDb(
                uri=vector_db_path,
                table_name="agno_assist_knowledge",
                search_type=SearchType.hybrid,
                embedder=LocalEmbedder(),  # type: ignore[arg-type]
            ),
        )

        print("📚 Loading Agno documentation into vector database...")
        await knowledge_instance.add_content_async(name="Agno Documentation", url="https://docs.agno.com/llms-full.txt")

    except Exception as e:
        print(f"⚠️  Failed to initialize vector database: {e}")
        print("⚠️  Agent will answer questions without document retrieval.")
        return None

    else:
        print("✅ Documentation loaded successfully")
        return knowledge_instance


def _setup_tools(mem0_api_key: str) -> list:
    """Set up all tools for the Agno Assist agent.

    Args:
        mem0_api_key: The Mem0 API key

    Returns:
        List of initialized tools

    Raises:
        APIKeyError: If mem0_api_key is missing
    """
    tools = []

    if not mem0_api_key:
        error_msg = (
            "Mem0 API key is required. Set MEM0_API_KEY environment variable.\n"
            "Get an API key from: https://app.mem0.ai/dashboard/api-keys"
        )
        raise APIKeyError(error_msg)

    try:
        mem0_tools = Mem0Tools(api_key=mem0_api_key)
        tools.append(mem0_tools)
        print("🧠 Mem0 memory system enabled for conversation context")
    except Exception as e:
        print(f"❌ Failed to initialize Mem0Tools: {e}")
        raise

    return tools


async def initialize_agent() -> None:
    """Initialize the Agno Assist agent.

    Sets up the knowledge base, LLM model, and tools, then creates the agent.

    Raises:
        APIKeyError: If required API keys are missing
    """
    global agent, knowledge

    openrouter_api_key, mem0_api_key, model_name = _get_api_keys()

    if not openrouter_api_key:
        error_msg = (
            "OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.\n"
            "Get an API key from: https://openrouter.ai/keys"
        )
        raise APIKeyError(error_msg)

    if not mem0_api_key:
        error_msg = (
            "Mem0 API key is required. Set MEM0_API_KEY environment variable.\n"
            "Get an API key from: https://app.mem0.ai/dashboard/api-keys"
        )
        raise APIKeyError(error_msg)

    knowledge = await _setup_knowledge_base()

    model = _create_llm_model(openrouter_api_key, model_name)
    tools = _setup_tools(mem0_api_key)

    agent = Agent(
        name="Agno Documentation Assistant",
        model=model,
        tools=tools,
        knowledge=knowledge,
        description=dedent("""\
            You are Agno Assist, a helpful AI assistant specialized in the Agno framework documentation.

            You help developers understand and use the Agno framework by providing accurate,
            documentation-grounded answers to their questions.
        """),
        instructions=dedent("""\
            RESPONSE PROCESS:

            1. SEARCH PHASE 🔍
               - If vector database is available, search for relevant documentation chunks
               - Use hybrid search (semantic + keyword) to find the most relevant information
               - Prioritize official Agno documentation from docs.agno.com

            2. ANSWER GENERATION 💡
               - Provide clear, concise answers based on the documentation
               - Include code examples when relevant
               - Explain concepts in simple terms
               - If documentation doesn't cover a topic, acknowledge limitations

            3. CONVERSATION CONTEXT 🧠
               - Use conversation history from Mem0 to understand context
               - Maintain coherent dialogue across multiple interactions
               - Ask clarifying questions when requests are ambiguous

            4. FORMATTING REQUIREMENTS ✨
               - Use markdown for better readability
               - Format code blocks with proper syntax highlighting
               - Use bullet points for lists
               - Include links to official documentation when available

            5. QUALITY STANDARDS ✅
               - Always be honest about what you know and don't know
               - Never hallucinate information
               - Cite documentation sources when possible
               - Keep answers focused and relevant
        """),
        add_datetime_to_context=True,
        markdown=True,
    )

    print(f"✅ Agno Assist agent initialized using {model_name}")
    if knowledge:
        print("📚 Vector database enabled for documentation search (using local embeddings)")
    print("🧠 Conversation memory enabled via Mem0")


async def run_agent(messages: list[dict[str, str]]) -> Any:
    """Run the agent with the given messages.

    Args:
        messages: List of message dictionaries with 'role' and 'content'

    Returns:
        Agent response

    Raises:
        RuntimeError: If agent is not initialized
    """
    global agent

    if not agent:
        error_msg = "Agent not initialized"
        raise RuntimeError(error_msg)

    result = await agent.arun(messages)  # type: ignore[arg-type]
    return result


async def handler(messages: list[dict[str, str]]) -> Any:
    """Handle incoming agent messages with lazy initialization.

    Args:
        messages: List of message dictionaries from the client

    Returns:
        Agent response
    """
    global _initialized

    async with _init_lock:
        if not _initialized:
            print("🔧 Initializing Agno Assist Agent...")
            await initialize_agent()
            _initialized = True

    return await run_agent(messages)


async def cleanup() -> None:
    """Clean up any resources."""
    print("🧹 Cleaning up Agno Assist Agent resources...")
    # LanceDB and SQLite connections are file-based and will close automatically


def _setup_environment_variables(args: argparse.Namespace) -> None:
    """Set environment variables from command line arguments.

    Args:
        args: Parsed command line arguments
    """
    if args.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = args.openrouter_api_key
    if args.mem0_api_key:
        os.environ["MEM0_API_KEY"] = args.mem0_api_key
    if args.model:
        os.environ["MODEL_NAME"] = args.model
    if args.enable_vector_db is not None:
        os.environ["ENABLE_VECTOR_DB"] = str(args.enable_vector_db)
    if args.vector_db_path:
        os.environ["VECTOR_DB_PATH"] = args.vector_db_path


def _display_configuration_info() -> None:
    """Display configuration information to the user."""
    print("=" * 60)
    print("🤖 AGNO DOCUMENTATION ASSISTANT")
    print("=" * 60)
    print("📚 Purpose: Answer questions about Agno framework documentation")
    print("🔍 Powered by: Retrieval-Augmented Generation (RAG)")

    config_info = []
    if os.getenv("OPENROUTER_API_KEY"):
        model = os.getenv("MODEL_NAME", "openai/gpt-4o")
        config_info.append(f"🤖 Model: {model}")
    if os.getenv("MEM0_API_KEY"):
        config_info.append("🧠 Memory: Conversation context enabled")
    if os.getenv("ENABLE_VECTOR_DB", "true").lower() in ("true", "1", "yes"):
        config_info.append("📚 Vector DB: Documentation search enabled (local embeddings)")
    else:
        config_info.append("📚 Vector DB: Disabled")

    for info in config_info:
        print(info)

    print("=" * 60)
    print("Example queries:")
    print("• 'What is Agno and how do I get started?'")
    print("• 'How do I create an agent with tools?'")
    print("• 'What vector databases does Agno support?'")
    print("• 'Show me an example of a knowledge base implementation'")
    print("=" * 60)


def main() -> None:
    """Run the main entry point for the Agno Assist Agent."""
    parser = argparse.ArgumentParser(description="Agno Assist Agent - Documentation assistant using RAG")
    parser.add_argument(
        "--openrouter-api-key",
        type=str,
        default=os.getenv("OPENROUTER_API_KEY"),
        help="OpenRouter API key (env: OPENROUTER_API_KEY)",
    )
    parser.add_argument(
        "--mem0-api-key",
        type=str,
        default=os.getenv("MEM0_API_KEY"),
        help="Mem0 API key for conversation memory (required)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("MODEL_NAME", "openai/gpt-4o"),
        help="Model ID for OpenRouter (env: MODEL_NAME)",
    )
    parser.add_argument(
        "--enable-vector-db",
        type=lambda x: x.lower() in ("true", "1", "yes"),
        default=os.getenv("ENABLE_VECTOR_DB", "true"),
        help="Enable LanceDB vector database (default: true)",
    )
    parser.add_argument(
        "--vector-db-path",
        type=str,
        default=os.getenv("VECTOR_DB_PATH", "tmp/lancedb"),
        help="Custom path for LanceDB (env: VECTOR_DB_PATH)",
    )

    args = parser.parse_args()

    _setup_environment_variables(args)
    _display_configuration_info()

    config = load_config()

    try:
        print("\n🚀 Starting Agno Assist Agent server...")
        print(f"🌐 Access at: {config.get('deployment', {}).get('url', 'http://127.0.0.1:3773')}")
        bindufy(config, handler)
    except KeyboardInterrupt:
        print("\n🛑 Agno Assist Agent stopped")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        import traceback

        traceback.print_exc()
        import sys

        sys.exit(1)
    finally:
        asyncio.run(cleanup())


if __name__ == "__main__":
    main()
