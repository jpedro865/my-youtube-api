run:
	docker compose -f docker-compose.dev.yml up

stop:
	docker compose -f docker-compose.dev.yml down

restart:
	docker compose -f docker-compose.dev.yml down
	docker compose -f docker-compose.dev.yml up -d

build:
	docker compose -f docker-compose.dev.yml build

stop-volumes:
	docker compose -f docker-compose.dev.yml down --volumes
