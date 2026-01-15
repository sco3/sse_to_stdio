# /// script
# dependencies = [
#   "httpx",
#   "mcp",
# ]
# ///

import asyncio
import json
import logging
import sys
from urllib.parse import urlparse

import httpx


async def read_sse(response: httpx.Response, sse_url: str, post_url_ref: list):
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            data = line[6:].strip()
            if data.startswith("/"):
                # Use the origin of the sse_url + the path provided
                parsed = urlparse(sse_url)
                post_url = f"{parsed.scheme}://{parsed.netloc}{data}"
                post_url_ref[0] = post_url
                logging.info(f"Detected POST endpoint: {post_url}")
            else:
                print(data, flush=True)


async def bridge(sse_url: str):
    async with httpx.AsyncClient() as client:
        # 1. Connect to the SSE endpoint to get the message relay URL
        async with client.stream("GET", sse_url) as response:
            # Most MCP SSE servers send the endpoint URL in a specific header
            # or as the first 'endpoint' event.
            post_url_ref = [None]

            # Start a background task to read from SSE and print to stdout
            sse_task = asyncio.create_task(read_sse(response, sse_url, post_url_ref))

            # 2. Read from stdin and POST to the SSE server
            while True:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                # Wait until we have the POST URL from the SSE stream
                while not post_url_ref[0]:
                    await asyncio.sleep(0.1)

                post_url = post_url_ref[0]
                try:
                    # Forward the JSON-RPC message
                    await client.post(
                        post_url,
                        content=line.strip(),
                        headers={"Content-Type": "application/json"},
                    )
                except Exception as e:
                    logging.error(f"Error forwarding to SSE: {e}")

            sse_task.cancel()


if __name__ == "__main__":
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(message)s')
    if len(sys.argv) < 2:
        logging.error("Usage: uv run mcp-bridge.py <sse_url>")
        sys.exit(1)

    try:
        asyncio.run(bridge(sys.argv[1]))
    except KeyboardInterrupt:
        pass