FROM ghcr.io/astral-sh/uv:python3.14-alpine
LABEL maintainer="Charles Weiss"

ENV PYTHONBUFFERED=1

COPY uv.lock /uv.lock
COPY pyproject.toml /pyproject.toml
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    uv sync --locked --no-dev && \
    if [ $DEV = "true" ]; \
        then uv sync --locked --dev ; \
    fi  && \
    rm /uv.lock && \
    rm /pyproject.toml && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

ENV PATH="/.venv/bin:$PATH"

USER django-user