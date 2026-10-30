FROM python:3.11-slim@sha256:e88e9763f943ec1834f992a4b51e0f24500486803e8bc534e5767af9ea65f6ce

ARG BETA8_RUN_ID
LABEL io.trilhacode.phase="beta8-1" \
      io.trilhacode.run="${BETA8_RUN_ID}" \
      io.trilhacode.role="harness"

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/repo/backend
WORKDIR /repo/backend

COPY ops/beta8-1-security/requirements.lock /tmp/beta8-1-requirements.lock
RUN python -m pip install --no-cache-dir --only-binary=:all: \
    -r /tmp/beta8-1-requirements.lock \
    && rm /tmp/beta8-1-requirements.lock \
    && useradd --uid 10081 --no-create-home --shell /usr/sbin/nologin beta8_1

COPY backend/ /repo/backend/

USER 10081:10081
CMD ["sh", "-ec", "python -m pytest -p no:cacheprovider -q /repo/backend/unit_tests/test_beta8_1_runtime_security.py && python /repo/backend/integration_tests/beta8_1_runtime_security.py"]