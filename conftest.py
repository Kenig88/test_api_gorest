import logging
import os
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from services.user.api_user import ApiUser
from services.user.user_endpoints import UserEndpoints
from services.user.user_payloads import UserPayloads

from services.post.api_post import ApiPost
from services.post.post_endpoints import PostEndpoints
from services.post.post_payload import PostPayloads

from services.comment.api_comment import ApiComment
from services.comment.comment_endpoints import CommentEndpoints
from services.comment.comment_payload import CommentPayload

from services.todo.api_todo import ApiTodo
from services.todo.todo_endpoints import TodoEndpoints
from services.todo.todo_payload import TodoPayloads

# Загружаем переменные из файла .env
# Например: BASE_URL и API_TOKEN
load_dotenv()

# Корневая папка проекта
PROJECT_ROOT = Path(__file__).resolve().parent

# Папка, куда будут сохраняться логи тестов
LOGS_DIR = PROJECT_ROOT / "logs"

# Стандартный timeout для API-запросов
DEFAULT_TIMEOUT = 30

# Количество повторных попыток для безопасных HTTP-методов
SAFE_METHOD_RETRIES = 1

# Логгер для тестов
logger = logging.getLogger("tests")


# Выполняется один раз при запуске Pytest
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # Создаём папку logs, если её ещё нет
    LOGS_DIR.mkdir(exist_ok=True)

    # При параллельном запуске через pytest-xdist
    # каждый worker получит своё имя.
    # При обычном запуске используется "main".
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")

    # Для каждого worker создаём отдельный log-файл
    config.option.log_file = str(
        LOGS_DIR / f"api-tests-{worker}.log"
    )

    # Не записываем лишние INFO/DEBUG логи
    # от сторонних библиотек
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("faker").setLevel(logging.WARNING)


# Получаем результат выполнения каждого теста
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Передаём управление Pytest и ждём результат
    outcome = yield

    # Получаем отчёт о выполнении теста
    report = outcome.get_result()

    # Если тест упал
    if report.failed:
        # FAILED — ошибка непосредственно внутри теста
        # ERROR — ошибка во время setup или teardown
        item._test_outcome = (
            "FAILED"
            if report.when == "call"
            else "ERROR"
        )

    # Если тест был пропущен
    elif report.skipped and not hasattr(item, "_test_outcome"):
        item._test_outcome = "SKIPPED"

    # Если основная часть теста успешно выполнилась
    elif report.when == "call":
        item._test_outcome = "PASSED"

    # После полного завершения теста записываем результат в лог
    if report.when == "teardown":
        worker = os.environ.get(
            "PYTEST_XDIST_WORKER",
            "main"
        )

        # Получаем сохранённый результат теста
        result = getattr(
            item,
            "_test_outcome",
            "FINISHED"
        )

        # Например:
        # [main] END TEST: tests/test_user.py::test_create_user -> PASSED
        logger.info(
            "[%s] END TEST: %s -> %s",
            worker,
            item.nodeid,
            result
        )


# Эта fixture автоматически запускается перед каждым тестом
@pytest.fixture(autouse=True)
def log_test_start(request):
    worker = os.environ.get(
        "PYTEST_XDIST_WORKER",
        "main"
    )

    # Записываем начало теста в лог
    logger.info(
        "[%s] START TEST: %s",
        worker,
        request.node.nodeid
    )

    # Здесь запускается сам тест
    yield


# Получает обязательную переменную из окружения или .env
def _get_env(name: str) -> str:
    value = os.getenv(name)

    # Если переменная не найдена — сразу показываем понятную ошибку
    assert value, (
        f"Переменная {name} не задана в окружении или .env"
    )

    return value


# Получаем BASE_URL из файла .env
# scope="session" — fixture создаётся один раз за весь запуск тестов
@pytest.fixture(scope="session")
def base_url() -> str:
    return _get_env("BASE_URL")


# Получаем API_TOKEN из файла .env
@pytest.fixture(scope="session")
def api_token() -> str:
    return _get_env("API_TOKEN")


# Создаём общую HTTP-сессию для всех API-тестов
@pytest.fixture(scope="session")
def http_session(api_token: str) -> requests.Session:
    # Session позволяет хранить общие headers
    # и настройки для всех запросов
    session = requests.Session()

    # Настраиваем автоматические повторные попытки запросов
    retry = Retry(
        # Общее количество повторных попыток
        total=SAFE_METHOD_RETRIES,

        # Повторять при ошибке подключения
        connect=SAFE_METHOD_RETRIES,

        # Повторять при ошибке чтения ответа
        read=SAFE_METHOD_RETRIES,

        # Повторять при определённых HTTP-кодах
        status=SAFE_METHOD_RETRIES,

        # Небольшая пауза перед повторной попыткой
        backoff_factor=0.5,

        # При этих ошибках сервера запрос можно повторить
        status_forcelist=(500, 502, 503, 504),

        # Повторяем только безопасные HTTP-методы
        # POST, PUT, PATCH и DELETE специально не повторяем
        allowed_methods=frozenset(
            {"GET", "HEAD", "OPTIONS"}
        ),

        # Учитываем header Retry-After, если сервер его вернул
        respect_retry_after_header=True,

        # Не выбрасываем отдельную ошибку только из-за HTTP status
        raise_on_status=False
    )

    # Создаём adapter с настройками retry
    adapter = HTTPAdapter(max_retries=retry)

    # Подключаем retry-настройки для HTTP
    session.mount("http://", adapter)

    # Подключаем retry-настройки для HTTPS
    session.mount("https://", adapter)

    # Эти headers будут автоматически добавляться
    # ко всем запросам через данную session
    session.headers.update(
        {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )

    # Передаём готовую session тестам
    yield session

    # После завершения всех тестов закрываем session
    session.close()


# ======================================================== USER ========================================================

# Создаём объект с URL/endpoints для User API
@pytest.fixture(scope="session")
def user_endpoints(base_url: str) -> UserEndpoints:
    return UserEndpoints(base_url)


# Создаём ApiUser, через который тесты работают с пользователями
@pytest.fixture(scope="session")
def api_user(
        http_session: requests.Session,
        user_endpoints: UserEndpoints
) -> ApiUser:
    return ApiUser(
        http_session=http_session,
        endpoints=user_endpoints,
        timeout=DEFAULT_TIMEOUT
    )


# Fixture-фабрика для создания тестовых пользователей
@pytest.fixture(scope="session")
def created_user(api_user: ApiUser):
    # Сюда сохраняем ID всех созданных пользователей,
    # чтобы после тестов их удалить
    created_user_ids: list[int] = []

    # Эта функция создаёт нового пользователя
    def create_user(overrides: dict | None = None):
        # Получаем стандартный payload пользователя
        payload = UserPayloads.create_user_payload()

        # Если тест передал свои данные,
        # заменяем ими нужные поля стандартного payload
        if overrides:
            payload.update(overrides)

        # Создаём пользователя через API
        user = api_user.create_user(payload)

        # Сохраняем ID для последующего удаления
        created_user_ids.append(user.id)

        # Возвращаем созданного пользователя тесту
        return user

    # Передаём тестам саму функцию create_user
    # Теперь в тесте можно писать: created_user()
    yield create_user

    # После завершения тестов удаляем
    # всех пользователей, созданных через эту fixture
    for user_id in reversed(created_user_ids):
        api_user.delete_user(
            user_id,
            allow_not_found=True
        )


# ======================================================== POST ========================================================

# Создаём объект с URL/endpoints для Post API
@pytest.fixture(scope="session")
def post_endpoints(base_url: str) -> PostEndpoints:
    return PostEndpoints(base_url)


# Создаём ApiPost, через который тесты работают с постами
@pytest.fixture(scope="session")
def api_post(
        http_session: requests.Session,
        post_endpoints: PostEndpoints
) -> ApiPost:
    return ApiPost(
        http_session=http_session,
        endpoints=post_endpoints,
        timeout=DEFAULT_TIMEOUT
    )


# Fixture-фабрика для создания тестовых постов
@pytest.fixture(scope="session")
def created_post(api_post: ApiPost, created_user):
    # Сохраняем ID созданных постов для последующего удаления
    created_post_ids: list[int] = []

    # Эта функция создаёт новый пост
    def create_post(
            user_id: int | None = None,
            overrides: dict | None = None
    ):
        # Если user_id не передали,
        # автоматически создаём нового пользователя
        if user_id is None:
            user_id = created_user().id

        # Получаем стандартный payload поста
        payload = PostPayloads.create_post_payload()

        # При необходимости заменяем отдельные поля
        if overrides:
            payload.update(overrides)

        # Создаём пост для указанного пользователя
        post = api_post.create_post(
            user_id=user_id,
            payload=payload
        )

        # Сохраняем ID поста для последующего удаления
        created_post_ids.append(post.id)

        return post

    # Передаём тестам функцию create_post
    yield create_post

    # После завершения тестов удаляем созданные посты
    for post_id in reversed(created_post_ids):
        api_post.delete_post(
            post_id,
            allow_not_found=True
        )


# ====================================================== COMMENT =======================================================

# Создаём объект с URL/endpoints для Comment API
@pytest.fixture(scope="session")
def comment_endpoints(base_url: str) -> CommentEndpoints:
    return CommentEndpoints(base_url)


# Создаём ApiComment для работы с комментариями
@pytest.fixture(scope="session")
def api_comment(
        http_session: requests.Session,
        comment_endpoints: CommentEndpoints
) -> ApiComment:
    return ApiComment(
        http_session=http_session,
        endpoints=comment_endpoints,
        timeout=DEFAULT_TIMEOUT
    )


# Fixture-фабрика для создания тестовых комментариев
@pytest.fixture(scope="session")
def created_comment(api_comment: ApiComment, created_post):
    # Сохраняем ID комментариев для последующего удаления
    created_comment_ids: list[int] = []

    # Эта функция создаёт новый комментарий
    def create_comment(
            post_id: int | None = None,
            overrides: dict | None = None
    ):
        # Если post_id не передали,
        # автоматически создаём новый пост
        if post_id is None:
            post_id = created_post().id

        # Получаем стандартный payload комментария
        payload = CommentPayload.create_comment_payload()

        # При необходимости заменяем отдельные поля
        if overrides:
            payload.update(overrides)

        # Создаём комментарий для указанного поста
        comment = api_comment.create_comment(
            post_id=post_id,
            payload=payload
        )

        # Сохраняем ID комментария для удаления
        created_comment_ids.append(comment.id)

        return comment

    # Передаём тестам функцию create_comment
    yield create_comment

    # После завершения тестов удаляем созданные комментарии
    for comment_id in reversed(created_comment_ids):
        api_comment.delete_comment(
            comment_id,
            allow_not_found=True
        )


# ======================================================== TODOS =======================================================

# Создаём объект с URL/endpoints для Todo API
@pytest.fixture(scope="session")
def todo_endpoints(base_url: str) -> TodoEndpoints:
    return TodoEndpoints(base_url)


# Создаём ApiTodo для работы с задачами Todo
@pytest.fixture(scope="session")
def api_todo(
        http_session: requests.Session,
        todo_endpoints: TodoEndpoints
) -> ApiTodo:
    return ApiTodo(
        http_session=http_session,
        endpoints=todo_endpoints,
        timeout=DEFAULT_TIMEOUT
    )


# Fixture-фабрика для создания тестовых Todo
@pytest.fixture(scope="session")
def created_todo(api_todo: ApiTodo, created_user):
    # Сохраняем ID созданных Todo для последующего удаления
    created_todo_ids: list[int] = []

    # Эта функция создаёт новую Todo
    def create_todo(
            user_id: int | None = None,
            overrides: dict | None = None
    ):
        # Если user_id не передали,
        # автоматически создаём нового пользователя
        if user_id is None:
            user_id = created_user().id

        # Получаем стандартный payload Todo
        payload = TodoPayloads.create_todo_payload()

        # При необходимости заменяем отдельные поля
        if overrides:
            payload.update(overrides)

        # Создаём Todo для указанного пользователя
        todo = api_todo.create_todo(
            user_id=user_id,
            payload=payload
        )

        # Сохраняем ID Todo для последующего удаления
        created_todo_ids.append(todo.id)

        return todo

    # Передаём тестам функцию create_todo
    yield create_todo

    # После завершения тестов удаляем созданные Todo
    for todo_id in reversed(created_todo_ids):
        api_todo.delete_todo(
            todo_id,
            allow_not_found=True
        )
