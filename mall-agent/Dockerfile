FROM s390x/python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential pkg-config libssl-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    CARGO_BUILD_JOBS=1 \
    GRPC_PYTHON_BUILD_EXT_COMPILER_JOBS=1 \
    GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1 \
    GRPC_PYTHON_CFLAGS="-O0 -g0 -std=c++17 -fvisibility=hidden -fno-wrapv -fno-exceptions" \
    GRPC_BUILD_WITH_BORING_SSL_ASM=0
ENV PATH=${CARGO_HOME}/bin:${PATH}

# Current PyPI releases of orjson/tiktoken need a recent Rust toolchain on s390x.
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
    | sh -s -- -y --profile minimal --default-toolchain stable

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
COPY knowledge ./knowledge
# Install only the SQLite checkpoint modules; sqlite-vec is used by LangGraph's
# vector store and is not needed by this application.
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir . \
    && python -m pip install --no-cache-dir --no-deps \
       "langgraph-checkpoint-sqlite==3.1.1" "aiosqlite>=0.20.0"

EXPOSE 18082
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "18082"]
