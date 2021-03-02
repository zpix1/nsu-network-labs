#!/bin/bash
set -e
PORT=9091
for req in request_*
do
    echo "=== REQUEST $req ==="
    cat $req
    echo "=== REPLY ==="
    cat $req | nc localhost $PORT | head -n 10
    echo
    echo "=== DONE $? ==="
done