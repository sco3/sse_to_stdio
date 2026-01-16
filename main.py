import asyncio
import logging
import sys

from pywrapper.bridge import bridge

def main(sse_url: str) -> None:
    """ main function starts the utility """
    # Log to stderr only! Stdout is reserved for JSON-RPC
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(message)s')

    try:
        asyncio.run(bridge(sse_url))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: python main.py <sse_url>")
        sys.exit(1)

    main(sys.argv[1])
