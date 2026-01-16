import asyncio
import logging
import sys
import threading
from urllib.parse import urlparse
import httpx

# Thread-safe queue for stdin lines
input_queue = asyncio.Queue()

def stdin_thread_worker(loop):
    """
    Standard synchronous reading in a dedicated thread.
    This is the only 100% reliable way to read stdin line-by-line 
    without blocking the event loop or losing data.
    """
    while True:
        line = sys.stdin.readline()
        if not line:
            # Signal EOF to the main loop
            loop.call_soon_threadsafe(input_queue.put_nowait, None)
            break
        # Put the line into the async queue
        loop.call_soon_threadsafe(input_queue.put_nowait, line)

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

async def bridge(sse_url: str):
    state = {'post_url': None}
    post_url_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    # Start the stdin worker thread
    threading.Thread(target=stdin_thread_worker, args=(loop,), daemon=True).start()

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("GET", sse_url) as response:
                # Background task for SSE -> Stdout
                sse_task = asyncio.create_task(
                    read_sse(response, sse_url, post_url_event, state)
                )

                # Main loop for Stdin -> SSE POST
                while True:
                    line = await input_queue.get()
                    if line is None:  # EOF reached
                        break
                    
                    # Wait for the POST URL if it's not yet available
                    await post_url_event.wait()
                    
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

if __name__ == "__main__":
    # Log to stderr only! Stdout is reserved for JSON-RPC
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(message)s')
    
    if len(sys.argv) < 2:
        logging.error("Usage: python bridge.py <sse_url>")
        sys.exit(1)

    try:
        asyncio.run(bridge(sys.argv[1]))
    except KeyboardInterrupt:
        pass