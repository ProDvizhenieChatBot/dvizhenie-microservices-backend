DOCKER_REGISTRY_ID = $(word 2,$(MAKECMDGOALS))

# Предотвращаем выполнение аргумента как цели
$(DOCKER_REGISTRY_ID):
	@:

BACKEND_VERSION = 0.1
BACKEND_API_DOCKER_IMAGE := cr.yandex/$(DOCKER_REGISTRY_ID)/backend-api:$(BACKEND_VERSION)
BACKEND_BOT_DOCKER_IMAGE := cr.yandex/$(DOCKER_REGISTRY_ID)/backend-bot:$(BACKEND_VERSION)
BACKEND_STORAGE_DOCKER_IMAGE := cr.yandex/$(DOCKER_REGISTRY_ID)/backend-storage:$(BACKEND_VERSION)

image:
	@echo 'Собираем докер-образ с бекендом и грузим его в registry'
	@docker buildx build --platform linux/amd64 --no-cache -f services/api_service/Dockerfile -t ${BACKEND_API_DOCKER_IMAGE} .
	@docker push ${BACKEND_API_DOCKER_IMAGE}

	@docker buildx build --platform linux/amd64 --no-cache -f services/bot_service/Dockerfile -t ${BACKEND_BOT_DOCKER_IMAGE} .
	@docker push ${BACKEND_BOT_DOCKER_IMAGE}

	@docker buildx build --platform linux/amd64 --no-cache -f services/file_storage_service/Dockerfile -t ${BACKEND_STORAGE_DOCKER_IMAGE} .
	@docker push ${BACKEND_STORAGE_DOCKER_IMAGE}
