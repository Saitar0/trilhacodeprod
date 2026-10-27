#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
COMPOSE_FILE="$SCRIPT_DIR/compose.yaml"
RUN_ID="$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
PROJECT="editorial-poc-$RUN_ID"
ROOT_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(36))')"
ROOT_USERNAME="pocroot"
RESOURCES_MAY_EXIST=0
COMPOSE_TIMEOUT_SECONDS="32m"

if [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
  printf '::add-mask::%s\n' "$ROOT_PASSWORD"
fi

export EDITORIAL_POC_DISPOSABLE=1
export EDITORIAL_POC_RUN_ID="$RUN_ID"
export EDITORIAL_POC_PROJECT="$PROJECT"
export EDITORIAL_POC_MONGO_HOST=mongo
export EDITORIAL_POC_MONGO_PORT=27017
export EDITORIAL_POC_ROOT_USERNAME="$ROOT_USERNAME"
export EDITORIAL_POC_ROOT_PASSWORD="$ROOT_PASSWORD"
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  printf 'run_id=%s\nproject=%s\ncleanup_needed=false\n' "$RUN_ID" "$PROJECT" >> "$GITHUB_OUTPUT"
fi

cleanup() {
  local status=$?
  trap - EXIT INT TERM
  if (( RESOURCES_MAY_EXIST )); then
    python3 "$SCRIPT_DIR/cleanup_compose.py" --compose-file "$COMPOSE_FILE" || {
      if (( status == 0 )); then status=3; fi
    }
  fi
  unset EDITORIAL_POC_ROOT_PASSWORD ROOT_PASSWORD
  exit "$status"
}
on_signal() {
  local status="$1"
  exit "$status"
}
trap cleanup EXIT
trap 'on_signal 130' INT
trap 'on_signal 143' TERM

if [[ -n "${MONGO_URL:-}${MONGO_URL_TEST:-}${DATABASE_URL:-}${EDITORIAL_POC_MONGO_URI:-}" ]]; then
  echo "Harness recusado: configuração MongoDB externa detectada." >&2
  exit 2
fi

python3 "$SCRIPT_DIR/test_docker_context.py"
python3 "$SCRIPT_DIR/verify_docker_context.py"
docker compose version >/dev/null
docker compose --project-name "$PROJECT" --file "$COMPOSE_FILE" config --format json \
  | python3 "$SCRIPT_DIR/validate_compose.py"

if [[ -n "$(docker ps --all --quiet --filter "label=com.docker.compose.project=$PROJECT")" \
   || -n "$(docker network ls --quiet --filter "label=com.docker.compose.project=$PROJECT")" \
   || -n "$(docker volume ls --quiet --filter "label=com.docker.compose.project=$PROJECT")" ]]; then
  echo "A identidade aleatória já possui recursos; execução recusada." >&2
  exit 2
fi

RESOURCES_MAY_EXIST=1
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  printf 'cleanup_needed=true\n' >> "$GITHUB_OUTPUT"
fi
set +e
timeout --signal=TERM --kill-after=20s "$COMPOSE_TIMEOUT_SECONDS" \
  docker compose --project-name "$PROJECT" --file "$COMPOSE_FILE" \
  up --build --abort-on-container-exit --exit-code-from harness harness
EXIT_CODE=$?
set -e
exit "$EXIT_CODE"
