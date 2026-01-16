import asyncio
import logging
import sys
from typing import Dict, Optional
from urllib.parse import urlparse

import httpx


async def read_sse(
    response: httpx.Response,
    sse_url: str,
    post_url_event: asyncio.Event,
    state: Dict[str, Optional[str]],
) -> None:
    """Processes SSE events and sends them to stdout immediately."""
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            data: str = line[6:].strip()
            if data.startswith("/"):
                # Discovery of the POST endpoint
                parsed = urlparse(sse_url)
                state['post_url'] = f"{parsed.scheme}://{parsed.netloc}{data}"
                post_url_event.set()
                logging.info(f"Connected to MCP SSE. POST endpoint discovered.")
            else:
                # Direct output to stdout with immediate flush
                sys.stdout.write(data + "\n")
                sys.stdout.flush()
