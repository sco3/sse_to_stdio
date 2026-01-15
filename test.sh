#!/usr/bin/env -S bash



# update exe to required executable
EXE="uv --project /home/dz/prj/pywrapper run /home/dz/prj/pywrapper/main.py http://localhost:8080/mcp/sse"


#commands

INIT='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0"}}}'
NOTIFY='{"jsonrpc":"2.0","method":"notifications/initialized"}'
LIST='{"jsonrpc":"2.0","id":2,"method":"tools/list"}'


CALL='{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "calculateSum",
    "arguments": {
          "first": 15,
          "second": 27
   }}
}'

CALL1='{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "calculateSum",
    "arguments": {
          "first": 40,
          "second": 3
   }}
}'

#echo $CALL | yq -o json -M -I 0

(
  echo "$INIT"
  sleep 0.1
  echo "$NOTIFY"
  sleep 0.1
  echo "$LIST"
  sleep 0.1
  echo "$(echo $CALL | yq -o json -M -I 0 )"
  sleep 0.1
  echo "$(echo $CALL1 | yq -o json -M -I 0 )"
  sleep 0.1
) | $EXE
