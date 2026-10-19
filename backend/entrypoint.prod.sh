#!/bin/sh
set -eu

exec uvicorn server:app \
  --proxy-headers \
  --forwarded-allow-ips "${TRUSTED_PROXY_IPS}" \
  --host 0.0.0.0 \
  --port "${PORT}" \
  --workers "${WEB_CONCURRENCY}"
