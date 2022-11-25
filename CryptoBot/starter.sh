#!/bin/bash

# turn on bash's job control
set -m

# API
uvicorn HomeAPI.app:app --host 0.0.0.0 --port 81 &

# BOT
python3 main.py
