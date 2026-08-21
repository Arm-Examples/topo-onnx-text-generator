FROM astral/uv:python3.12-bookworm-slim AS model-downloader

WORKDIR /downloader

COPY uv.lock pyproject.toml .python-version ./
RUN uv sync --locked --no-install-project --only-group downloader

ARG HF_REPO_ID
RUN --mount=type=secret,id=hf_token,env=HF_TOKEN uv run --no-sync hf download "$HF_REPO_ID" --local-dir model

FROM astral/uv:python3.12-bookworm-slim AS runtime

WORKDIR /runtime

COPY uv.lock pyproject.toml .python-version ./
RUN uv sync --locked --no-install-project --only-group runtime

COPY --from=model-downloader /downloader/model model
COPY app app

CMD ["uv", "run", "--no-sync", "app/server.py"]
