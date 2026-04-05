# Визуальный конструктор UML-диаграмм

Веб-приложение, которое автоматически превращает UML-схемы в готовый код на Python или Java и обратно. Это избавляет разработчиков от рутинного написания шаблонного кода  и гарантирует, что архитектура проекта всегда соответствует актуальной диаграмме.


## Состав команды (Backend)

- @vockagolordy

- @Ryhsjs

## Переменные среды

Перед запуском необходимо указать переменные среды

Шаблон файла переменных среды - `.env.example`

Переменные среды указать в файле `.env`

| Title   | Description | Type   | Default   |
|---------|-------------|--------|-----------|
| DB_HOST | DB host     | string | localhost |
| DB_PORT | DB port     | number | 5432      |
| DB_USER | DB username | string | postgres  |
| DB_PASS | DB password | string | password  |
| DB_NAME | DB name     | string | postgres  |

## До запуска проекта

Клонирование репозитория
Для запуска проекта требуется менеджер зависимостей [uv](https://docs.astral.sh/uv/)

### Установка зависимостей
```bash
uv sync
```

### Применение миграций
```bash
uv run alembic upgrade head
```

## Запуск проекта
```bash
uv run fastapi dev
```

## Для разработчиков

### Установка зависимостей для разработчиков
```bash
uv sync --dev
```

### Миграции

#### Создать

```bash
uv run alembic revision --autogenerate -m "описание"
```

#### Применить
```bash
uv run alembic upgrade head
```

#### Откатить

```bash
uv run alembic downgrade -1
```

Перед выполнением команд убедитесь, что заполнен `.env` и запущен PostgreSQL.

## pre-commit

Установка pre-commit
```bash
uv run pre-commit install
```
