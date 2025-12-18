#!/bin/bash

# Navigate to app directory and run uvicorn
cd "$(dirname "$0")/app"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
