# Test API GoRest

API test automation framework для публичного REST API [GoRest](https://gorest.co.in/).

Проект покрывает `User`, `Post`, `Comment` и `Todo` и включает smoke, regression и negative тесты, параллельный запуск,
Docker, Allure и GitHub Actions.

## Стек

- Python 3.11+
- Pytest, Requests, Pydantic, Faker
- Pytest-xdist
- Allure Pytest
- Docker / Docker Compose
- GitHub Actions / GitHub Pages

## Особенности проекта

- API-клиенты разделены по сущностям `User`, `Post`, `Comment` и `Todo`;
- контракты ответов проверяются через Pydantic-модели;
- тестовые данные генерируются через Faker;
- fixtures создают необходимые сущности и автоматически выполняют cleanup;
- поддерживается параллельный запуск тестов через pytest-xdist;
- запросы, ответы и ошибки прикрепляются к Allure, чувствительные данные маскируются.

## Покрытие

- CRUD для пользователей, постов и задач;
- создание, получение списков и удаление комментариев;
- связанные ресурсы пользователей и постов;
- проверка пагинации через `X-Pagination-*` headers;
- smoke-сценарии жизненного цикла сущностей;
- ошибки авторизации, валидации и несуществующих ресурсов;
- валидация API-ответов через Pydantic.

Маркеры:

- `smoke` — основные end-to-end сценарии;
- `regression` — позитивные функциональные проверки;
- `negative` — проверки ошибок API.

## Структура проекта

```text
test_api_gorest/
├── tests/
│   ├── user/
│   ├── post/
│   ├── comment/
│   └── todo/
├── services/
│   ├── api_base.py
│   ├── error_models.py
│   ├── user/
│   ├── post/
│   ├── comment/
│   └── todo/
├── config/base_test.py
├── utils/helper.py
├── .github/workflows/test-api-gorest.yml
├── conftest.py
├── pytest.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yaml
└── .env.example
```

`ApiBase` содержит общую работу с HTTP, status codes, ошибками и пагинацией. API-клиенты разделены по сущностям,
fixtures создают тестовые данные и выполняют cleanup, а запросы и ответы прикрепляются к Allure с маскированием
чувствительных данных.

## Локальный запуск

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активация Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
source .venv/bin/activate
```

Установите зависимости:

```bash
python -m pip install -r requirements.txt
```

Создайте `.env` на основе `.env.example`:

```env
BASE_URL=https://gorest.co.in/public/v2
API_TOKEN=your_gorest_token
```

Запуск тестов:

```bash
python -m pytest
python -m pytest -m smoke
python -m pytest -m regression
python -m pytest -m negative
```

Параллельный запуск:

```bash
python -m pytest -n 2
```

## Docker

```bash
docker compose build

docker compose run --rm all
docker compose run --rm smoke
docker compose run --rm regression
docker compose run --rm negative
```

По умолчанию используется 2 xdist-worker. Другое значение можно передать через `PYTEST_WORKERS`:

```bash
docker compose run --rm -e PYTEST_WORKERS=4 all
```

## Allure

```bash
python -m pytest --alluredir=allure-results --clean-alluredir
allure serve allure-results
```

## GitHub Actions

Workflow `.github/workflows/test-api-gorest.yml` запускается вручную и позволяет выбрать набор тестов и количество
xdist-worker.

Для запуска необходимо добавить Repository Secrets:

```text
BASE_URL
API_TOKEN
```

Тесты выполняются в Docker. Логи и результаты сохраняются как artifacts, а Allure-отчёт публикуется через GitHub Pages с
историей предыдущих запусков.

## Логи и cleanup

Логи сохраняются в `logs/`. При запуске через xdist каждый worker получает отдельный файл, например `api-tests-gw0.log`
и `api-tests-gw1.log`.

Созданные через fixtures `User`, `Post`, `Comment` и `Todo` автоматически удаляются после тестов.
