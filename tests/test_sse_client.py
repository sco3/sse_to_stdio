
import asyncio
import io
from unittest.mock import MagicMock, patch

import httpx
import pytest

from pywrapper.sse_client import read_sse


@pytest.mark.anyio
async def test_read_sse():
    # Mock response and its aiter_lines method
    mock_response = MagicMock(spec=httpx.Response)
    sse_events = [
        "data: /post/endpoint",
        "data: some data",
        "data: more data",
    ]

    async def mock_aiter_lines():
        for event in sse_events:
            yield event

    mock_response.aiter_lines.return_value = mock_aiter_lines()

    # Mock event and state
    post_url_event = asyncio.Event()
    state: dict[str, str | None] = {"post_url": None}

    # Mock stdout
    mock_stdout = io.StringIO()
    with patch("sys.stdout", mock_stdout):
        await read_sse(mock_response, "http://localhost:8080", post_url_event, state)

    # Asserts
    assert state["post_url"] == "http://localhost:8080/post/endpoint"
    assert post_url_event.is_set()
    assert mock_stdout.getvalue() == "some data\nmore data\n"
