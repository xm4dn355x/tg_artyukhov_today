# tg_artyukhov_today
Телеграм-бот канала "Артюхов Today"

## Dependencies
- Python 3.8
- PostgreSQL 10+
- Docker

## How to build and run
```bash
# Сборка контейнера
docker build -t artyuhov_today .

# Запуск контейнера
docker run --network host artyuhov_today
```