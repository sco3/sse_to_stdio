
import asyncio
import io
import sys
import threading
from unittest.mock import patch

from pywrapper.stdin_reader import stdin_thread_worker, input_queue


import pytest


@pytest.mark.anyio
async def test_stdin_reader():
    # Mock stdin with some lines
    mock_stdin = io.StringIO("line 1\nline 2\n")
    with patch.object(sys, "stdin", mock_stdin):
        # Run the stdin_thread_worker in a separate thread
        loop = asyncio.get_event_loop()
        worker_thread = threading.Thread(
            target=stdin_thread_worker, args=(loop,), daemon=True
        )
        worker_thread.start()

        # Read from the queue and check the lines
        line1 = await input_queue.get()
        assert line1 == "line 1\n"
        input_queue.task_done()

        line2 = await input_queue.get()
        assert line2 == "line 2\n"
        input_queue.task_done()

        # Check for EOF
        eof = await input_queue.get()
        assert eof is None
        input_queue.task_done()

        # The queue should be empty now
        assert input_queue.empty()

        # Wait for the worker thread to finish
        worker_thread.join(timeout=1)
        assert not worker_thread.is_alive()

