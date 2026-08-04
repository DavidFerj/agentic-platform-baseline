FROM python:3.12.13-slim-bookworm

ARG UV_VERSION=0.8.3

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN groupadd --system platform \
    && useradd --system --gid platform --create-home platform \
    && python -m pip install --no-cache-dir "uv==${UV_VERSION}"

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
COPY gcp/services/control-plane gcp/services/control-plane
RUN uv sync --frozen --package agentic-platform-control-plane --no-dev

ENV PATH="/workspace/.venv/bin:${PATH}" \
    PYTHONPATH="/workspace/gcp/services/control-plane/src"

USER platform
WORKDIR /workspace/gcp/services/control-plane

EXPOSE 8000

CMD ["uvicorn", "platform_api.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
