ARG PYTHON_VERSION=3.13.2
FROM python:${PYTHON_VERSION}-slim AS builder

# Copy only requirements to cache them in docker layer
WORKDIR /code

COPY poetry.lock pyproject.toml /code/

RUN python -m pip install --no-cache-dir poetry==2.1.1 \
    && poetry config virtualenvs.in-project true

RUN poetry install --no-interaction --no-ansi --no-root

FROM python:${PYTHON_VERSION}-slim

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Switch to the non-privileged user to run the application.
USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  PYTHONPATH=/code

WORKDIR /code

COPY --from=builder /code /code

# Creating folders, and files for a project:
COPY . /code

EXPOSE 8000

# Run the application.
ENTRYPOINT "./entrypoint.sh"
