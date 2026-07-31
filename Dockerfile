FROM ghcr.io/astral-sh/uv:alpine3.23 AS model-downloader

WORKDIR /downloader

COPY uv.lock pyproject.toml .python-version ./
RUN uv sync --locked --no-install-project --only-group downloader

ARG MODEL
RUN --mount=type=secret,id=hf_token,env=HF_TOKEN uv run --no-sync hf download "$MODEL" --local-dir model

FROM ghcr.io/astral-sh/uv:trixie-slim AS runtime

WORKDIR /runtime

COPY uv.lock pyproject.toml .python-version ./
RUN uv sync --locked --no-install-project --only-group runtime

COPY app app
COPY --from=model-downloader /downloader/model model

CMD ["uv", "run", "--no-sync", "app/server.py"]
