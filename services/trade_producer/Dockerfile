FROM python:3.11-slim-buster

RUN pip install poetry

WORKDIR /app

COPY . /app

RUN poetry install --no-dev

CMD ["poetry", "run", "python", "src/main.py"]