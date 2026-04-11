#!/bin/bash
# run-sim.sh — Start GitHub login simulation
set -euo pipefail

echo "🧪 Starting GitHub OAuth simulation for user: tom-sapletta-com"
echo ""

# Start mock GitHub server standalone (for dev without full docker-compose)
if command -v docker &>/dev/null; then
    echo "▶ Building mock-github..."
    docker build -t mock-github:latest ./mock-github/

    echo "▶ Starting mock-github on :4010..."
    docker run -d --rm --name mock-github \
        -p 4010:4010 \
        -e FRONTEND_URL=http://localhost:3000 \
        -e BACKEND_URL=http://localhost:8003 \
        mock-github:latest

    echo "▶ Waiting for mock-github..."
    for i in $(seq 1 10); do
        if curl -sf http://localhost:4010/health >/dev/null 2>&1; then
            echo "✅ Mock GitHub server ready at http://localhost:4010"
            break
        fi
        sleep 1
    done

    echo ""
    echo "📋 Test login page:  http://localhost:4010/login/oauth/authorize?client_id=test&state=test123"
    echo "📋 Health check:     http://localhost:4010/health"
    echo ""
    echo "To stop: docker stop mock-github"
else
    echo "▶ Running with uvicorn (no Docker)..."
    cd mock-github
    pip install -q -r requirements.txt
    uvicorn server:app --host 0.0.0.0 --port 4010 &
    echo "✅ Mock GitHub server on http://localhost:4010"
fi
