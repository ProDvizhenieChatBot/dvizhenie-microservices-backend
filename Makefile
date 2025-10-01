DOCKER_REGISTRY_ID = $(word 2,$(MAKECMDGOALS))

# Предотвращаем выполнение аргумента как цели
$(DOCKER_REGISTRY_ID):
	@:

BACKEND_VERSION = 0.1
BACKEND_API_DOCKER_IMAGE := cr.yandex/$(DOCKER_REGISTRY_ID)/backend-api:$(BACKEND_VERSION)
BACKEND_BOT_DOCKER_IMAGE := cr.yandex/$(DOCKER_REGISTRY_ID)/backend-bot:$(BACKEND_VERSION)
BACKEND_STORAGE_DOCKER_IMAGE := cr.yandex/$(DOCKER_REGISTRY_ID)/backend-storage:$(BACKEND_VERSION)

CURRENT_DIR := $(CURDIR)

image:
	@echo 'Собираем докер-образ с бекендом и грузим его в registry'
	@cd $(CURRENT_DIR)/services/api_service && \
	docker buildx build --platform linux/amd64 --no-cache -t ${BACKEND_API_DOCKER_IMAGE} .
	@docker push ${BACKEND_API_DOCKER_IMAGE}

	@cd $(CURRENT_DIR)/services/bot_service && \
	docker buildx build --platform linux/amd64 --no-cache -t ${BACKEND_BOT_DOCKER_IMAGE} .
	@docker push ${BACKEND_BOT_DOCKER_IMAGE}

	@cd $(CURRENT_DIR)/services/file_storage_service && \
	@docker buildx build --platform linux/amd64 --no-cache -t ${BACKEND_STORAGE_DOCKER_IMAGE} .
	@docker push ${BACKEND_STORAGE_DOCKER_IMAGE}
