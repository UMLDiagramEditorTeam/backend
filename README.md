# Визуальный конструктор UML-диаграмм

Веб-приложение, которое автоматически превращает UML-схемы в готовый код на Python или Java и обратно. Это избавляет разработчиков от рутинного написания шаблонного кода  и гарантирует, что архитектура проекта всегда соответствует актуальной диаграмме.


## Состав команды (Backend)

- @vockagolordy

- @Ryhsjs

## Переменные среды

Перед запуском необходимо указать переменные среды

Шаблон файла переменных среды - `.env.example`

Переменные среды указать в файле `.env`

| Title                          | Description                         | Type   | Default            |
|--------------------------------|-------------------------------------|--------|--------------------|
| DB__DRIVER                     | DB driver                           | string | postgresql+asyncpg |
| DB__HOST                       | DB host                             | string | localhost          |
| DB__PORT                       | DB port                             | number | 5432               |
| DB__USER                       | DB user                             | string | postgres           |
| DB__PASSWORD                   | DB password                         | string | password           |
| DB__NAME                       | DB name                             | string | postgres           |
| AUTH__JWT_PRIVATE_KEY          | Secrete key used to sign JWT tokens | string |                    |
| AUTH__JWT_ALGORITHM            | JWT signing algorithm               | string | HS256              |
| AUTH__JWT_ACCESS_TOKEN_EXPIRE  | Access token lifetime in seconds    | number | 3600               |
| AUTH__JWT_REFRESH_TOKEN_EXPIRE | Refresh token lifetime in seconds   | number | 604800             |
| AUTH__ACCOUNT_CONFIRMATION_TOKEN_EXPIRE | Account confirmation code lifetime in seconds | number | 86400 |
| AUTH__PASSWORD_RESET_TOKEN_EXPIRE | Password reset code lifetime in seconds | number | 3600 |
| RBAC__ADMIN_EMAIL              | Default admin user email            | string | admin@example.com  |
| RBAC__ADMIN_PASSWORD           | Default admin user password         | string | admin123456        |
| SMTP__USERNAME                 | SMTP service username/email         | string |                    |
| SMTP__PASSWORD                 | SMTP service app password           | string |                    |
| SMTP__HOST                     | SMTP server host                    | string | smtp.example.com   |
| SMTP__PORT                     | SMTP server port                    | number | 587                |
| SMTP__USE_CREDENTIALS          | Use credentials for SMTP connection | boolean | true              |
| SMTP__STARTTLS                 | Enable STARTTLS for SMTP connection | boolean | true              |
| SMTP__SSL_TLS                  | Enable SSL/TLS for SMTP connection  | boolean | false             |
| SMTP__VALIDATE_CERTS           | Validate SMTP TLS certificates      | boolean | true              |
| EMAIL__FROM_EMAIL              | Sender email address                | string | noreply@example.com |
| EMAIL__FROM_NAME               | Sender display name                 | string | UML Diagram Editor |
| EMAIL__TEMPLATE_FOLDER         | Email templates folder              | string | app/templates/email |
| EMAIL__ACCOUNT_CONFIRMATION_SUBJECT | Account confirmation email subject | string | Account confirmation |
| EMAIL__PASSWORD_RESET_SUBJECT  | Password reset email subject        | string | Password reset confirmation |
| EMAIL__ACCOUNT_CONFIRMATION_URL | Frontend account confirmation URL  | string | http://localhost:3000/auth/confirm |
| EMAIL__PASSWORD_RESET_URL      | Frontend password reset URL         | string | http://localhost:3000/auth/password/change |

Для генерации JWT_PRIVATE_KEY можно использовать openssl

```bash
openssl rand -hex 32
```
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
