import asyncio
import logging
import sys
from urllib.parse import urlparse

async def read_sse(response, sse_url, post_url_event, state):
    """Processes SSE events and sends them to stdout immediately."""
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            data = line[6:].strip()
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
