ARG BASE_IMAGE=python:3.10-slim-bookworm
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y make

RUN mkdir /api-currency-converter
COPY . /api-currency-converter
WORKDIR /api-currency-converter

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
