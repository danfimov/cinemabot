FROM python:3.11.5 as python-base

# Turn of logs buffering for faster logging
# Do not write *.pyc in a container
# Turns off writing cache to keep smaller image size
# Faster building
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=200
ENV PIP_INDEX_URL=https://pypi.org/simple/
# force the use of system CA certificate bundle, not certifi
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

RUN wget https://crls.yandex.net/YandexInternalRootCA.crt -O /usr/local/share/ca-certificates/YandexInternalRootCA.crt && \
    update-ca-certificates

RUN python -m venv /opt/poetry
RUN /opt/poetry/bin/pip install --no-cache-dir poetry==1.7.0
RUN ln -svT /opt/poetry/bin/poetry /usr/local/bin/poetry
RUN poetry config virtualenvs.in-project true

FROM python-base AS builder-base

WORKDIR /app
RUN useradd appuser

RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --no-interaction --no-ansi --no-root --without dev \
    && rm -rf ~/.cache/pypoetry/{cache,artifacts}

COPY ./docker ./docker
COPY ./cinemabot ./cinemabot

ARG APP_VERSION="0.0.0+docker"
RUN poetry version $APP_VERSION
RUN poetry install --no-interaction --no-ansi --without dev

USER root

EXPOSE 8000/tcp

ENTRYPOINT ["docker/entrypoint"]
CMD ["poetry", "run", "python3" , "cinemabot/__main__.py"]
