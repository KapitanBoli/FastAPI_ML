## Как запустить проект

Для запуска проекта вам потребуется установленный Docker и Docker Compose (для запуска с Docker) или Python и pip (для локального запуска).

1.  **Склонируйте репозиторий** (если еще не сделали это):

    ```bash
    git clone <URL_РЕПОЗИТОРИЯ>
    ```

2.  **Создайте файл `.env`**: Создайте файл с именем `.env` в корневой директории проекта  и скопируйте в него следующее содержимое:

    ```ini
    FASTAPI_CONFIG__DB__URL=postgresql+asyncpg://user:password@pg:5432/app
    
    FASTAPI_CONFIG__REDIS__URL=redis://redis:6379
    FASTAPI_CONFIG__REDIS__DB=0
    
    FASTAPI_CONFIG__VIDEO__MAX_SIZE=104857600
    FASTAPI_CONFIG__VIDEO__UPLOAD_DIR=uploads/videos
    
    POSTGRES_DB=app
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    
    PGADMIN_DEFAULT_EMAIL=user@mail.ru
    PGADMIN_DEFAULT_PASSWORD=password
    ```

3.  **Запустите приложение с Docker Compose**:

    ```bash
    # Сборка и запуск контейнеров
    docker compose up --build
    
    # Остановка контейнеров
    docker compose down
    
    # Применение миграций
    docker-compose run --rm web alembic upgrade head
    
    # Для создание новой миграции
    docker-compose run --rm web alembic revision --autogenerate -m "описание"
    ```

4.  **Доступ к API**: После запуска API будет доступно по адресу `http://localhost:8000`.
    Документация Swagger UI будет доступна по `http://localhost:8000/docs`.
    Документация ReDoc будет доступна по `http://localhost:8000/redoc`.
    pgAdmin 4 будет доступен по `http://localhost:15432/login`

## Управлению техническими средствами с помощью жестов
### Описание:
Нейронная сеть распознает динамические жесты руки, среди которых: движение пальца влево, вправо, вверх, вниз и ничего, если движения нет.
Жест должен выполняться в течение 1-2 секунды. 
По пути video/upload приложение принимает видеозапись размером максимум 100MB.
По пути video/result/{task_id} можно просмотреть статус и результат распознавания видеозаписи.
