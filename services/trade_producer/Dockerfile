FROM python:3.11-slim-buster

# stream output to console
ENV PYTHONUNBUFFERED=1

RUN pip install poetry==1.8.3

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install --only main

COPY . /app

CMD ["poetry", "run", "python", "src/main.py"]