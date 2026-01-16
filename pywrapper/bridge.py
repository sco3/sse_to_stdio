import asyncio
import logging
import threading
from typing import Dict, Optional

import httpx

from pywrapper.sse_client import read_sse
from pywrapper.stdin_reader import stdin_thread_worker, input_queue


async def bridge(sse_url: str) -> None:
    state: Dict[str, Optional[str]] = {'post_url': None}
    post_url_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    # Start the stdin worker thread
    threading.Thread(target=stdin_thread_worker, args=(loop,), daemon=True).start()

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("GET", sse_url) as response:
                # Background task for SSE -> Stdout
                sse_task: asyncio.Task[None] = asyncio.create_task(
                    read_sse(response, sse_url, post_url_event, state)
                )

                # Main loop for Stdin -> SSE POST
                while True:
                    line: Optional[str] = await input_queue.get()
                    if line is None:  # EOF reached
                        break

                    # Wait for the POST URL if it's not yet available
                    await post_url_event.wait()

                    if state['post_url'] is None:
                        logging.warning("post_url is not set, skipping POST request")
                        continue

                    try:
                        # Forward JSON-RPC request from stdin to the MCP server
                        await client.post(
                            state['post_url'],
                            content=line.strip(),
                            headers={"Content-Type": "application/json"},
                        )
                    except Exception as e:
                        logging.error(f"Failed to POST to MCP: {e}")

                sse_task.cancel()
        except Exception as e:
            logging.error(f"Bridge connection error: {e}")
