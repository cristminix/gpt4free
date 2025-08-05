#!/bin/bash

export PYTHONPATH=$(pwd)
ARGS="$@"

 
./examples/cli.sh client \
    --conversation-file conversation.txt \
    -O conversation.txt \
    -p Blackbox -m gpt-4 $ARGS