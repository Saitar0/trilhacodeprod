FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /repo/backend

RUN python -m pip install --no-cache-dir pymongo==4.18.2
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin harness

COPY backend/services/editorial_generations_poc.py /repo/backend/services/editorial_generations_poc.py
COPY backend/unit_tests/test_editorial_generations_poc.py /repo/backend/unit_tests/test_editorial_generations_poc.py
COPY backend/integration_tests/__init__.py /repo/backend/integration_tests/__init__.py
COPY backend/integration_tests/test_editorial_generations_mongodb.py /repo/backend/integration_tests/test_editorial_generations_mongodb.py
COPY ops/editorial-generations/run_homologation.py /repo/ops/editorial-generations/run_homologation.py

USER 10001:10001
CMD ["python", "/repo/ops/editorial-generations/run_homologation.py"]
