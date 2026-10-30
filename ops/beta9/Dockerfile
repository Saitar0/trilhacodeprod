FROM python:3.11-slim@sha256:e88e9763f943ec1834f992a4b51e0f24500486803e8bc534e5767af9ea65f6ce

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/repo/backend \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright CI=true
WORKDIR /repo/backend

COPY ops/beta9/requirements.lock /tmp/beta9-requirements.lock
RUN python -m pip install --no-cache-dir --only-binary=:all: \
    -r /tmp/beta9-requirements.lock \
    && rm /tmp/beta9-requirements.lock \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10083 --no-create-home --shell /usr/sbin/nologin beta9

WORKDIR /repo/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci \
    && mkdir -p /ms-playwright \
    && npx playwright install --with-deps chromium

ARG BETA8_3_RUN_ID
LABEL io.trilhacode.phase="beta9" \
      io.trilhacode.run="${BETA8_3_RUN_ID}" \
      io.trilhacode.role="process-image"

COPY backend/ /repo/backend/
COPY frontend/ /repo/frontend/

USER 10083:10083
WORKDIR /repo/backend
CMD ["/bin/sh", "-ec", "cd /repo/frontend && npm run typecheck && npm run lint && npm test && npx vite build --outDir /tmp/beta9-frontend-dist && cd /repo/backend && python -m pytest -p no:cacheprovider -q /repo/backend/unit_tests/test_beta8_1_runtime_security.py && python -m pytest -p no:cacheprovider -q /repo/backend/unit_tests/test_beta8_3_internal_protocol.py /repo/backend/unit_tests/test_beta8_4_authority_consistency.py /repo/backend/unit_tests/test_beta8_2_writer_containment.py /repo/backend/unit_tests/test_beta8_security_contracts.py /repo/backend/unit_tests/test_beta_staging_contract.py /repo/backend/unit_tests/test_editorial_iam_authority.py /repo/backend/unit_tests/test_editorial_revision_protocol.py /repo/backend/unit_tests/test_beta6_learning_security_contracts.py /repo/backend/unit_tests/test_progress_fail_closed.py /repo/backend/unit_tests/test_sessions.py /repo/backend/unit_tests/test_beta6_test_database_policy.py /repo/backend/unit_tests/test_beta7_1_preview_contract.py /repo/backend/unit_tests/test_beta7_2_runtime_isolation.py"]
