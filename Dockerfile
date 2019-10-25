FROM python:3.7 as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=0.12.11

ENV PYTHONPATH=/app/iwell


# system deps
RUN pip install "poetry==$POETRY_VERSION"

# copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# project initialization
RUN poetry config settings.virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi


RUN mkdir /app/iwell && touch /app/iwell/__init__.py

# make project source symlinks
RUN poetry install --no-dev --no-interaction --no-ansi

# copy project files
COPY . /app
# CMD ["python", "iwell"]
