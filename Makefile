ENV:=production
COMMIT_HASH    := $$(git log -1 --pretty=%h)
DATE := $$(date +"%Y-%m-%d")
CTX:=.

redis-start:
	docker run -d --name redis -p 6379:6379 redis

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
	celery -E -A iwell.celery_queue.worker:celery worker --loglevel=INFO --purge

celery-beat:
	celery -A iwell.celery_queue.worker:celery beat --loglevel=DEBUG

celery-flower:
	celery -A iwell.celery_queue.worker:celery flower --loglevel=DEBUG --purge

app-start:
	poetry run iwell ipython

kubectl-proxy:
	kubectl proxy --port=8080

build:
	@echo "Building docker image: ${IMAGE_NAME}"
	docker build ${CTX} -t ${IMAGE_NAME}
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${ENV}
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${COMMIT_HASH}
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${DATE}

push:
	${eval LATEST=${IMAGE_NAME}:latest}
	${eval GCR_LATEST=${GCR}/${LATEST}}
	${eval GCR_ENV=${GCR}/${IMAGE_NAME}:$${ENV}}
	${eval GCR_HASH=${GCR}/${IMAGE_NAME}:$${COMMIT_HASH}}
	${eval GCR_DATE=${GCR}/${IMAGE_NAME}:$${DATE}}

	docker tag ${LATEST} ${GCR_LATEST}
	docker tag ${LATEST} ${GCR_ENV}
	docker tag ${LATEST} ${GCR_HASH}
	docker tag ${LATEST} ${GCR_DATE}

	docker push ${GCR_LATEST}
	docker push ${GCR_ENV}
	docker push ${GCR_HASH}
	docker push ${GCR_DATE}