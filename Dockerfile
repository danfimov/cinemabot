FROM python:3.10-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base AS builder-base

# System apt packages
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \

    # removed all unnecessary packages after installation
    && rm -rf /var/lib/apt/lists/*

# Update pip and related packages first
RUN pip install --upgrade pip==22.3

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
 RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.1.14

WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-dev --no-root

FROM python-base AS bot

# Copying poetry and venv into image
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH

COPY . .

RUN poetry install

CMD ["poetry", "run", "python3" , "cinemabot/__main__.py"]
