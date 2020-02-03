FROM segment/chamber:2.7.5 as build

FROM python:3.7 as base

LABEL "com.datadoghq.ad.logs"='[{"source": "python","service": "iwell"}]'


ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.0

ENV PYTHONPATH=/app/iwell

# Install Poetry & ensure it is in $PATH
RUN pip install "poetry==$POETRY_VERSION"
ENV PATH "/root/.poetry/bin:/opt/venv/bin:${PATH}"

# copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# project initialization
RUN poetry install --no-dev --no-interaction

RUN mkdir /app/iwell && touch /app/iwell/__init__.py

# make project source symlinks
RUN poetry install --no-dev --no-interaction

# copy project files
COPY . /app

# create unprivileged user
RUN groupadd -r celeryuser && useradd -r -m -g celeryuser celeryuser
RUN find /app ! -user celeryuser -exec chown celeryuser {} \;

COPY --from=build /chamber /chamber

ENTRYPOINT ["/chamber", "exec", "iwell", "datadog", "--"]