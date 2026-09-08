# Берём готовый образ с Python 3.11.
# alpine — облегчённая версия Linux, поэтому образ получается небольшим.
FROM python:3.11-alpine


# Настройки Python и pip внутри контейнера.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# PYTHONDONTWRITEBYTECODE=1
# Не создаёт служебные файлы Python __pycache__ и .pyc.

# PYTHONUNBUFFERED=1
# Выводит print и логи сразу в консоль, без задержки.
# Это удобно при просмотре логов Docker и pytest.

# PIP_DISABLE_PIP_VERSION_CHECK=1
# Отключает сообщение pip о наличии новой версии.


# Устанавливаем необходимые системные пакеты Alpine.
RUN apk add --no-cache \
    tzdata \
    ca-certificates \
    bash \
&& update-ca-certificates

# tzdata
# Добавляет информацию о часовых поясах.

# ca-certificates
# Добавляет SSL-сертификаты, необходимые для HTTPS-запросов.
# Для API-тестов это особенно важно.

# bash
# Устанавливает bash внутри контейнера.

# --no-cache
# Не сохраняет кэш apk, чтобы Docker-образ занимал меньше места.

# update-ca-certificates
# Обновляет список доверенных SSL-сертификатов.


# Создаём рабочую директорию внутри контейнера.
# Все следующие команды будут выполняться относительно неё.
WORKDIR /usr/workspace


# Копируем requirements.txt с компьютера внутрь контейнера.
COPY requirements.txt .


# Обновляем pip и устанавливаем Python-зависимости проекта.
RUN pip install --no-cache-dir --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt

# --no-cache-dir
# Не сохраняет кэш скачанных Python-пакетов,
# благодаря чему Docker-образ получается меньше.


# Копируем весь проект в рабочую директорию контейнера.
COPY . .


# Создаём директории для логов pytest и результатов Allure.
# Флаг -p не выдаст ошибку, если директории уже существуют.
RUN mkdir -p logs allure-results


# Команда, которая запускается при старте контейнера.
CMD ["sh", "-c", "pytest -n ${PYTEST_WORKERS:-2} --alluredir=allure-results --clean-alluredir"]

# sh -c
# Позволяет выполнить команду через shell.
# Здесь это нужно в том числе для использования переменной ${PYTEST_WORKERS}.

# pytest
# Запускает тесты.

# -n ${PYTEST_WORKERS:-2}
# Запускает тесты параллельно.
# Количество потоков берётся из переменной PYTEST_WORKERS.
# Если переменная не задана, используется 2 потока.
#
# Например:
# PYTEST_WORKERS=4 -> pytest запустится с -n 4
# переменная не задана -> pytest запустится с -n 2
#
# Для параметра -n нужен pytest-xdist.

# --alluredir=allure-results
# Сохраняет результаты тестов для Allure в папку allure-results.

# --clean-alluredir
# Перед новым запуском очищает старые результаты Allure.