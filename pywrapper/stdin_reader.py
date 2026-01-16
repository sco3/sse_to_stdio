import asyncio
import sys

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
