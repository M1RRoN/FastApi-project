# Указываем базовый образ
FROM python:3.8-alpine

# Установка рабочей директории внутри контейнера
WORKDIR /code

# Устанавливаем зависимости
COPY . /code
COPY ./requirements.txt /requirements.txt
RUN apk add --no-cache python3-dev \
    && pip install --upgrade pip
RUN apk update && \
    apk add --no-cache sqlite
RUN pip install --no-cache-dir -r /requirements.txt


# Открытие порта, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]