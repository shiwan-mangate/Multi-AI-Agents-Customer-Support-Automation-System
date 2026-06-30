#!/bin/sh
set -e

echo "========================================"
echo "Starting Multi-Agent Customer Support"
echo "APP_SERVICE=${APP_SERVICE}"
echo "========================================"

case "${APP_SERVICE}" in

  api)
    echo "Starting FastAPI..."
    exec uvicorn api.main:app \
      --host 0.0.0.0 \
      --port 7860
    ;;

  crm)
    echo "Starting CRM Worker..."
  
    python3 -m http.server 7860 &
    exec python platform_orchestration/scripts/run_worker.py
    ;;

  proactive)
    echo "Starting Proactive Worker..."
  
    python3 -m http.server 7860 &
    exec python platform_orchestration/scripts/run_proactive.py
    ;;

  *)
    echo "ERROR: Unknown APP_SERVICE='${APP_SERVICE}'"
    echo "Valid values: api, crm, proactive"
    exit 1
    ;;

esac