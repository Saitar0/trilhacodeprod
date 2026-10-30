FROM python:3.11-slim@sha256:e88e9763f943ec1834f992a4b51e0f24500486803e8bc534e5767af9ea65f6ce

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/repo/backend
WORKDIR /repo/backend

COPY ops/beta8-3-security/requirements.lock /tmp/beta8-3-requirements.lock
RUN python -m pip install --no-cache-dir --only-binary=:all: \
    -r /tmp/beta8-3-requirements.lock \
    && rm /tmp/beta8-3-requirements.lock \
    && useradd --uid 10083 --no-create-home --shell /usr/sbin/nologin beta8_3

ARG BETA8_3_RUN_ID
LABEL io.trilhacode.phase="beta8-3" \
      io.trilhacode.run="${BETA8_3_RUN_ID}" \
      io.trilhacode.role="process-image"

COPY backend/ /repo/backend/

USER 10083:10083
CMD ["python", "-m", "pytest", "-p", "no:cacheprovider", "-q", "/repo/backend/unit_tests/test_beta8_3_internal_protocol.py", "/repo/backend/unit_tests/test_beta8_2_writer_containment.py", "/repo/backend/unit_tests/test_beta8_security_contracts.py", "/repo/backend/unit_tests/test_beta8_1_runtime_security.py", "/repo/backend/unit_tests/test_beta_staging_contract.py"]
