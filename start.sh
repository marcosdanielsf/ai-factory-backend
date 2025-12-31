#!/bin/bash
# Railway start script - detects PORT automatically

# Railway injeta PORT como variável de ambiente
if [ -z "$PORT" ]; then
    PORT=8000
fi

echo "🚀 Starting server on port $PORT..."
uvicorn server:app --host 0.0.0.0 --port $PORT
