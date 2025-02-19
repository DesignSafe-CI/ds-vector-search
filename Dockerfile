FROM python:3.13-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV VIRTUAL_ENV=/opt/venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# Install dependencies:
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Run the application:
COPY scripts/ /opt/scripts/