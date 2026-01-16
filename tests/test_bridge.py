
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from pywrapper.bridge import bridge


@pytest.mark.anyio
async def test_bridge():
    with patch("pywrapper.bridge.stdin_thread_worker"), \
         patch("pywrapper.bridge.input_queue") as mock_input_queue, \
         patch("pywrapper.bridge.read_sse") as mock_read_sse, \
         patch("pywrapper.bridge.httpx.AsyncClient") as mock_async_client:

        # --- Setup Mocks ---
        mock_client_instance = mock_async_client.return_value
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_stream = mock_client_instance.stream.return_value
        mock_stream.__aenter__.return_value = MagicMock() # Mock response object

        # Let read_sse discover the post_url immediately
        async def set_post_url(*args, **kwargs):
            post_url_event = args[2]
            state = args[3]
            state['post_url'] = "http://localhost:8080/post"
            post_url_event.set()

        mock_read_sse.side_effect = set_post_url

        # Simulate stdin input
        mock_input_queue.get = AsyncMock(side_effect=["test line\n", None])

        # --- Run Bridge ---
        await bridge("http://localhost:8080/sse")

        # --- Asserts ---
        mock_async_client.assert_called_once_with(timeout=None)
        mock_client_instance.stream.assert_called_once_with("GET", "http://localhost:8080/sse")
        mock_read_sse.assert_called_once()
        mock_client_instance.post.assert_called_once_with(
            "http://localhost:8080/post",
            content="test line",
            headers={"Content-Type": "application/json"},
        )
