SHELL := /bin/zsh
COMMIT_HASH    := $$(git log -1 --pretty=%h)
DATE := $$(date +"%Y-%m-%d")
CTX:=.
AWS_ACCOUNT_ID:=$$(aws-vault exec ${ENV} -- aws sts get-caller-identity | jq .Account -r)
IMAGE_NAME:=driftwood/iwell
DOCKERFILE:=Dockerfile
APP_VERSION=$$(grep -o '\([0-9]\+.[0-9]\+.[0-9]\+\)' pyproject.toml | head -n1)

test-appversion:
	@echo $$(pyappversion)

cc-expand:
	# show expanded configuration
	circleci config process .circleci/config.yml

cc-process:
	circleci config process .circleci/config.yml > process.yml

cc-run-local:
	JOBNAME?=build-image
	circleci local execute -c process.yml --job build-image -e DOCKER_LOGIN=${DOCKER_LOGIN} -e DOCKER_PASSWORD=${DOCKER_PASSWORD}

run-tests:
	export APP_SETTINGS=iwell.config.TestingConfig && pytest --cov=iwell tests/ --cov-report xml:./coverage/python/coverage.xml --log-cli-level debug

smoke-test:
	docker run --entrypoint iwell driftwood/iwell:${COMMIT_HASH} test smoke-test

cov:
	export APP_SETTINGS=iwell.config.TestingConfig && pytest --cov iwell --cov-report html:./coverage/coverage.html --log-level info --log-cli-level debug

view-cov:
	open -a "Google Chrome" ./coverage/coverage.html/index.html

release:
	poetry run python scripts/release.py

export-deps:
	poetry export -f requirements.txt > requirements.txt --without-hashes

init-db:
	poetry run iwell db init

migrate:
	# poetry run iwell db stamp head
	poetry run iwell db migrate

revision:
	poetry run iwell db revision

upgrade:
	poetry run iwell db upgrade

celery-worker:
	celery -E -A iwell.celery_queue.worker:celery worker --loglevel=INFO

celery-beat:
	celery -A iwell.celery_queue.worker:celery beat --loglevel=DEBUG

kubectl-proxy:
	kubectl proxy --port=8080


login:
	docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}

build:
	@echo "Building docker image: ${IMAGE_NAME}"
	docker build  -f Dockerfile . -t ${IMAGE_NAME}
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:dev
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:${COMMIT_HASH}
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:${APP_VERSION}
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:latest


build-with-chamber:
	@echo "Building docker image: ${IMAGE_NAME} (with chamber)"
	docker build  -f Dockerfile.chamber . -t ${IMAGE_NAME}
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:chamber-dev
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:chamber-${COMMIT_HASH}
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:chamber-${APP_VERSION}
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:chamber-latest

build-all: build-with-chamber build

push: login
	docker push ${IMAGE_NAME}:dev
	docker push ${IMAGE_NAME}:${COMMIT_HASH}
	docker push ${IMAGE_NAME}:latest

push-all: login push
	docker push ${IMAGE_NAME}:chamber-dev
	docker push ${IMAGE_NAME}:chamber-${COMMIT_HASH}
	docker push ${IMAGE_NAME}:chamber-latest

push-version:
	# docker push ${IMAGE_NAME}:latest
	@echo pushing: ${IMAGE_NAME}:${APP_VERSION}, ${IMAGE_NAME}:chamber-${APP_VERSION}
	docker push ${IMAGE_NAME}:${APP_VERSION}
	docker push ${IMAGE_NAME}:chamber-${APP_VERSION}

all:
	make build-all push-all

deploy:
	@echo ${AWS_ACCOUNT_ID}
	export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID} && aws-vault exec ${ENV} -- poetry run python scripts/deploy.py

redeploy:
	aws ecs update-service --cluster ${ECS_CLUSTER} --service ${SERVICE_NAME} --force-new-deployment --profile ${ENV}


ssm-export:
	# Export all SSM parameters associated with this service to json
	aws-vault exec ${ENV} -- chamber export ${SERVICE_NAME} | jq

ssm-export-dotenv:
	# Export all SSM parameters associated with this service to dotenv format
	aws-vault exec ${ENV} -- chamber export --format=dotenv ${SERVICE_NAME} | tee .env.ssm

env-to-json:
	# pipx install json-dotenv
	python3 -c 'import json, os, dotenv;print(json.dumps(dotenv.dotenv_values(".env.production")))' | jq

ssm-update:
	# Update SSM environment variables using a local dotenv file (.env.production by default)
	@echo "Updating parameters for ${AWS_ACCOUNT_ID}/${SERVICE_NAME}"
	python3 -c 'import json, os, dotenv; values={k.lower():v for k,v in dotenv.dotenv_values(".env.production").items()}; print(json.dumps(values))' | jq | aws-vault exec ${ENV} -- chamber import ${SERVICE_NAME} -

view-credentials:
	# print the current temporary credentials from aws-vault
	aws-vault exec ${ENV} -- env | grep AWS

compose:
	# run docker-compose using aws-vault session credentials
	aws-vault exec prod -- docker-compose up

secret-key:
	python3 -c 'import secrets; print(secrets.token_urlsafe(256));'
