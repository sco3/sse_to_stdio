### MCP Stdio wrapper arount MCP SSE server



This utility serves as a transport adapter for the Model Context Protocol (MCP). 
It allows MCP clients that only support Stdio (standard input/output) to communicate with 
MCP servers that use SSE (Server-Sent Events) over HTTP.

## Mechanism

The bridge operates by mapping two different communication protocols:

    * Inbound: It reads JSON-RPC messages from stdin and forwards them to the remote server via HTTP POST requests.

    * Outbound: It listens to the remote SSE stream and writes the incoming data events directly to stdout.

The script uses a background thread to monitor stdin and an asynchronous loop for the HTTP traffic. 
It automatically extracts the required POST endpoint from the initial SSE handshake as defined in the MCP specification.

## Collaboration Diagram

```mermaid
graph TD
    A[main.py] --> B(pywrapper/bridge.py);
    B --> C(pywrapper/sse_client.py);
    B --> D(pywrapper/stdin_reader.py);
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant MainThread
    participant StdinThread
    participant SSEClient
    participant MCPServer

    MainThread->>StdinThread: start
    activate StdinThread
    StdinThread-->>MainThread: started

    par "Read Stdin"
        StdinThread->>sys.stdin: readline()
        sys.stdin-->>StdinThread: line
        StdinThread->>MainThread: input_queue.put(line)
    and "Process SSE"
        MainThread->>MCPServer: GET /sse
        activate MCPServer
        MCPServer-->>MainThread: SSE Events
        MainThread->>sys.stdout: write(event)
    and "Process Stdin"
        MainThread->>MainThread: input_queue.get()
        MainThread->>MCPServer: POST /rpc
        MCPServer-->>MainThread: 
    end
```
