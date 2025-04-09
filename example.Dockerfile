FROM registry.tochka-tech.com/oci_baseimage_python/python-debian:3.12 AS build

# Add uv
COPY --from=registry.tochka-tech.com/proxy_ghcr-io/astral-sh/uv:0.6.3 /uv /uvx /bin/

# - Silence uv complaining about not being able to use hard links,
# - tell uv to byte-compile packages for faster application startups,
# - prevent uv from accidentally downloading isolated Python builds,
# - pick a Python,
# - and finally declare `/project` as the target for `uv sync`.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT="/app/.venv"

USER root

COPY ./pyproject.toml ./uv.lock ./docker ./
RUN uv sync --no-dev --locked
RUN uv add vllm-0.8.2+cpu.cpu-cp312-cp312-macosx_15_0_arm64.whl --frozen

FROM registry.tochka-tech.com/oci_baseimage_python/python-debian:3.12 AS production

# Создаем необходимые директории и устанавливаем права
RUN install -d -m 0755 -o app /app/data

# Copy the application into the container.
COPY . /app

COPY --from=build app/.venv /app/.venv/
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

USER app

EXPOSE 8000 8001

ENTRYPOINT [ "docker/entrypoint.sh" ]
CMD [ "docker/start.sh" ]
