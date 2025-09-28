# Makefile

# Platform detection and command definitions

include .env

ifdef OS
    # Windows
    SLEEP = timeout /T 2 /NOBREAK > NUL
    ENV_COPY = if not exist .env copy .env.example .env >nul 2>&1
else
    ifeq ($(shell uname), Linux)
        # Linux
        SLEEP = sleep 2
        ENV_COPY = if [ ! -f .env ]; then cp .env.example .env; fi
    endif
endif

.PHONY: prepare-env up-infra up-test-infra down up-remote down-remote

prepare-env:
	@echo Creating .env config
	@$(ENV_COPY)

up-infra:
	@echo Creating database ${DB_NAME}...
	@psql -h localhost -U postgres -c "CREATE DATABASE ${DB_NAME};" || echo ""
	@echo Waiting 2 secs for Postgres to be ready...
	@$(SLEEP)
	@alembic upgrade head

up-test-infra:
	@echo Creating test database ${DB_NAME}...
	@docker compose -f docker-compose.yaml up -d
	@echo Waiting 2 secs for Postgres to be ready...
	@$(SLEEP)
	@alembic upgrade head

down:
	@docker compose -f docker-compose.yaml down && docker network prune --force

up-remote:
	@docker compose -f docker-compose-ci.yaml up -d

down-remote:
	@docker compose -f docker-compose-ci.yaml down && docker network prune --force
