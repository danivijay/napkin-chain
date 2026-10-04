#!/bin/bash
# Lambda handler. The Lambda Web Adapter layer (AWS_LAMBDA_EXEC_WRAPPER=/opt/bootstrap)
# runs this, waits for /health to answer, then proxies each invocation to uvicorn
# as a plain HTTP request, so the FastAPI app runs exactly as it does in Docker.
exec python -m uvicorn app.main:app --host 127.0.0.1 --port "${AWS_LWA_PORT:-8000}"
