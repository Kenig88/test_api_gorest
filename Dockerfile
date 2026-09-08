FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apk add --no-cache \
    tzdata \
    ca-certificates \
    bash \
&& update-ca-certificates

WORKDIR /usr/workspace

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs allure-results

CMD ["sh", "-c", "pytest -n ${PYTEST_WORKERS:-2} --alluredir=allure-results --clean-alluredir"]