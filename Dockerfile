FROM ghcr.io/astral-sh/uv:python3.14-alpine
LABEL maintainer="Charles Weiss"

ENV PYTHONBUFFERED=1

COPY uv.lock /uv.lock
COPY pyproject.toml /pyproject.toml
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    uv sync --locked --no-dev && \
    if [ $DEV = "true" ]; \
        then uv sync --locked --dev ; \
    fi  && \
    rm -rf /tmp && \
    rm /uv.lock && \
    rm /pyproject.toml && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        django-user && \
    mkdir -p /home/django-user && \
    chown -R django-user:django-user /home/django-user

ENV PATH="/app/.venv/bin:$PATH"

USER django-user