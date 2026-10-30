FROM python:3.11-slim@sha256:e88e9763f943ec1834f992a4b51e0f24500486803e8bc534e5767af9ea65f6ce

ARG BETA8_RUN_ID
LABEL io.trilhacode.phase="beta8" \
      io.trilhacode.run="${BETA8_RUN_ID}" \
      io.trilhacode.role="harness"

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/repo/backend
WORKDIR /repo/backend

COPY ops/beta8-security/requirements.lock /tmp/beta8-requirements.lock
RUN python -m pip install --no-cache-dir --only-binary=:all: \
    -r /tmp/beta8-requirements.lock \
    && rm /tmp/beta8-requirements.lock \
    && useradd --uid 10008 --no-create-home --shell /usr/sbin/nologin beta8

COPY backend/curriculum_contract/ /repo/backend/curriculum_contract/
COPY backend/services/__init__.py /repo/backend/services/__init__.py
COPY backend/services/beta8_editorial_enforcement.py /repo/backend/services/beta8_editorial_enforcement.py
COPY backend/services/beta8_curriculum_promotion.py /repo/backend/services/beta8_curriculum_promotion.py
COPY backend/integration_tests/beta8_security_persistence.py /repo/backend/integration_tests/beta8_security_persistence.py

USER 10008:10008
CMD ["python", "/repo/backend/integration_tests/beta8_security_persistence.py"]
