ARG BASE_IMAGE=python:3.10-slim-buster
FROM ${BASE_IMAGE}

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "80"]