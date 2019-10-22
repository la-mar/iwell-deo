FROM python:3.7 as base

ARG FLASK_ENV

ENV FLASK_ENV=${FLASK_ENV} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=0.12.11

ENV PYTHONPATH=/app/iwell


# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config settings.virtualenvs.create false \
    && poetry install $(test "$FLASK_ENV" == production && echo "--no-dev") --no-interaction --no-ansi


RUN mkdir /app/iwell && touch /app/iwell/__init__.py
RUN poetry install --no-interaction

# Copy project files
COPY . /app

