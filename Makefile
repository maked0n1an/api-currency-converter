# Makefile

# Include the prepare-env.mk file
# prepare-env.mk

.PHONY: prepare-dev

prepare-env-windows:
	@echo Creating .env config
	@if not exist .env copy .env.example .env >nul 2>&1

prepare-env-unix:
	@echo Creating .env config
	@ if [ ! -f .env ]; then cp .env.example .env; fi

up-local-windows:
	@docker compose -f docker-compose.yaml up -d
	@echo Waiting 2 secs for Postgres to be ready...
	@timeout /T 2 /NOBREAK > NUL
	@alembic upgrade head

up-local-unix:
	@docker compose -f docker-compose.yaml up -docker
	@echo Waiting 2 secs for Postgres to be ready...
	@sleep 2
	@alembic upgrade head

down-local:
	@docker compose -f docker-compose.yaml down && docker network prune --force

up-remote:
	@docker compose -f docker-compose-ci.yaml up -d

down-remote:
	@docker compose -f docker-compose-ci.yaml down && docker network prune --force
