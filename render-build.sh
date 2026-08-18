#!/usr/bin/env bash
# Render build: compile the SPA, then install the API's dependencies.
set -euo pipefail

echo "--- building frontend"
cd frontend
npm ci
npm run build
cd ..

echo "--- installing backend dependencies"
pip install --no-cache-dir -r backend/requirements.txt

echo "--- build complete"
