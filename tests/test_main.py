from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agno_assist_agent.main import APIKeyError, handler


@pytest.mark.asyncio
async def test_handler_returns_response():
    """Test that handler accepts messages and returns a response."""
    messages = [{"role": "user", "content": "Hello, how are you?"}]

    # Mock the run_agent function to return a mock response
    mock_response = MagicMock()
    mock_response.run_id = "test-run-id"
    mock_response.status = "COMPLETED"

    # Mock _initialized to skip initialization and run_agent to return our mock
    with (
        patch("agno_assist_agent.main._initialized", True),
        patch("agno_assist_agent.main.run_agent", new_callable=AsyncMock, return_value=mock_response),
    ):
        result = await handler(messages)

    # Verify we get a result back
    assert result is not None
    assert result.run_id == "test-run-id"
    assert result.status == "COMPLETED"


@pytest.mark.asyncio
async def test_handler_with_multiple_messages():
    """Test that handler processes multiple messages correctly."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather?"},
    ]

    mock_response = MagicMock()
    mock_response.run_id = "test-run-id-2"

    with (
        patch("agno_assist_agent.main._initialized", True),
        patch("agno_assist_agent.main.run_agent", new_callable=AsyncMock, return_value=mock_response) as mock_run,
    ):
        result = await handler(messages)

    # Verify run_agent was called
    mock_run.assert_called_once_with(messages)
    assert result is not None
    assert result.run_id == "test-run-id-2"


@pytest.mark.asyncio
async def test_handler_initialization():
    """Test that handler initializes on first call."""
    messages = [{"role": "user", "content": "Test"}]

    mock_response = MagicMock()
    mock_response.run_id = "test-init-run-id"
    mock_response.status = "COMPLETED"

    # Start with _initialized as False to test initialization path
    with (
        patch("agno_assist_agent.main._initialized", False),
        patch("agno_assist_agent.main.initialize_agent", new_callable=AsyncMock) as mock_init,
        patch("agno_assist_agent.main.run_agent", new_callable=AsyncMock, return_value=mock_response) as mock_run,
        patch("agno_assist_agent.main._init_lock", new_callable=MagicMock()) as mock_lock,
    ):
        # Configure the lock to work as an async context manager
        mock_lock_instance = MagicMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=None)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance

        result = await handler(messages)

        # Verify initialization was called
        mock_init.assert_called_once()
        # Verify run_agent was called
        mock_run.assert_called_once_with(messages)
        # Verify we got a result
        assert result is not None
        assert result.run_id == "test-init-run-id"
        assert result.status == "COMPLETED"


@pytest.mark.asyncio
async def test_handler_race_condition_prevention():
    """Test that handler prevents race conditions with initialization lock."""
    messages = [{"role": "user", "content": "Test"}]

    mock_response = MagicMock()

    # Test with multiple concurrent calls
    with (
        patch("agno_assist_agent.main._initialized", False),
        patch("agno_assist_agent.main.initialize_agent", new_callable=AsyncMock) as mock_init,
        patch("agno_assist_agent.main.run_agent", new_callable=AsyncMock, return_value=mock_response),
        patch("agno_assist_agent.main._init_lock", new_callable=MagicMock()) as mock_lock,
    ):
        # Configure the lock to work as an async context manager
        mock_lock_instance = MagicMock()
        mock_lock_instance.__aenter__ = AsyncMock(return_value=None)
        mock_lock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_lock.return_value = mock_lock_instance

        # Call handler twice to ensure lock is used
        await handler(messages)
        await handler(messages)

        # Verify initialize_agent was called only once (due to lock)
        mock_init.assert_called_once()


@pytest.mark.asyncio
async def test_handler_with_agno_query():
    """Test that handler can process an Agno framework query."""
    messages = [
        {
            "role": "user",
            "content": "How do I create an agent with tools in Agno?",
        }
    ]

    mock_response = MagicMock()
    mock_response.run_id = "agno-run-id"
    mock_response.content = "Agno documentation answer generated successfully."

    with (
        patch("agno_assist_agent.main._initialized", True),
        patch("agno_assist_agent.main.run_agent", new_callable=AsyncMock, return_value=mock_response),
    ):
        result = await handler(messages)

    assert result is not None
    assert result.run_id == "agno-run-id"
    assert result.content == "Agno documentation answer generated successfully."


@pytest.mark.asyncio
async def test_handler_requires_api_key():
    """Test that handler raises error when no API key is provided."""
    messages = [{"role": "user", "content": "Test"}]

    # Configure the lock to work as an async context manager
    mock_lock_instance = MagicMock()
    mock_lock_instance.__aenter__ = AsyncMock(return_value=None)
    mock_lock_instance.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("agno_assist_agent.main._initialized", False),
        patch("agno_assist_agent.main.initialize_agent", side_effect=APIKeyError("No API key")),
        patch("agno_assist_agent.main._init_lock", return_value=mock_lock_instance),
        patch("agno_assist_agent.main.run_agent", new_callable=AsyncMock),
        pytest.raises(APIKeyError, match="No API key"),
    ):
        await handler(messages)


@pytest.mark.asyncio
async def test_handler_agent_not_initialized():
    """Test that handler raises error when agent is not initialized."""
    messages = [{"role": "user", "content": "Test"}]

    with (
        patch("agno_assist_agent.main._initialized", True),
        patch("agno_assist_agent.main.run_agent", side_effect=RuntimeError("Agent not initialized")),
        pytest.raises(RuntimeError, match="Agent not initialized"),
    ):
        await handler(messages)


@pytest.mark.asyncio
async def test_handler_with_mem0_api_key_missing():
    """Test that handler raises error when Mem0 API key is missing."""
    messages = [{"role": "user", "content": "Test"}]

    # Configure the lock to work as an async context manager
    mock_lock_instance = MagicMock()
    mock_lock_instance.__aenter__ = AsyncMock(return_value=None)
    mock_lock_instance.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("agno_assist_agent.main._initialized", False),
        patch("agno_assist_agent.main.initialize_agent", side_effect=APIKeyError("Mem0 API key required")),
        patch("agno_assist_agent.main._init_lock", return_value=mock_lock_instance),
        patch("agno_assist_agent.main.run_agent", new_callable=AsyncMock),
        pytest.raises(APIKeyError, match="Mem0 API key required"),
    ):
        await handler(messages)


@pytest.mark.asyncio
async def test_handler_with_documentation_query():
    """Test that handler can process a documentation recommendation query."""
    messages = [
        {
            "role": "user",
            "content": "What vector databases does Agno support?",
        }
    ]

    mock_response = MagicMock()
    mock_response.run_id = "docs-run-id"
    mock_response.content = "Documentation answer generated."

    with (
        patch("agno_assist_agent.main._initialized", True),
        patch("agno_assist_agent.main.run_agent", new_callable=AsyncMock, return_value=mock_response),
    ):
        result = await handler(messages)

    assert result is not None
    assert result.run_id == "docs-run-id"
    assert result.content == "Documentation answer generated."
