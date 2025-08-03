# Currency Exchange API

A high-performance, scalable RESTful API for real-time currency exchange rates and conversion, built with FastAPI and async SQLAlchemy.  
Features robust JWT authentication, session management, and integration with Coinlore for up-to-date currency data.

---

## Features

- **User Authentication & Authorization**: Secure JWT-based login, session control, and role-based access.
- **Currency Data**: Real-time rates and conversion via Coinlore.
- **Async Architecture**: FastAPI + async SQLAlchemy for high concurrency.
- **Modular Design**: Clean separation of API, services, repositories, and database layers.
- **Database Migrations**: Alembic for versioned schema changes.
- **Interactive API Docs**: Swagger UI and ReDoc out of the box.
- **Security Headers**: Requires `X-Device-ID` for device identification and `X-CSRF-Token` for protection against CSRF in modifying requests.

---

## 🛠️ Used Technologies and Dependencies

The project is built on **FastAPI** and uses the following libraries:

### 🚀 Main Stack

| Library                | Purpose                                                |
|------------------------|--------------------------------------------------------|
| `fastapi`              | Main web framework                                     |
| `sqlalchemy`           | Python SQL Toolkit and Object Relational Mapper        |
| `asyncpg`              | Database interface library designed for PostgreSQL     |
| `uvicorn`              | ASGI server for running FastAPI applications           |
| `starlette`            | Web framework underlying FastAPI                       |
| `pydantic`             | Data validation and serialization                      |
| `pydantic-settings`    | Configuration management via `.env`                    |
| `alembic`              | Lightweight database migration tool with SQLAlchemy    |
| `python-dotenv`        | Loads environment variables from `.env` file           |
| `passlib`              | Password hashing                                       |
| `PyJWT`                | JWT token handling                                     |

### 🌐 HTTP and External API Integration

| Library                | Purpose                                                |
|------------------------|--------------------------------------------------------|
| `httpx`                | Alternative HTTP client (optional dependencies)        |

### ✅ Testing

| Library                | Purpose                                                |
|------------------------|--------------------------------------------------------|
| `pytest`               | Main testing framework                                 |
| `pytest-asyncio`       | Async test support                                     |
| `pytest-mock`          | Convenient mocking utilities                           |


---

## Quick Start (for Developers)

### Prerequisites

- Python 3.10+
- Make
- PostgreSQL (for production DB)
- (Optional) Docker (for test DB)

### 1. Clone the repository and enter the project directory

```sh
git clone https://github.com/maked0n1an/api-currency-converter.git
cd api-currency-converter
```

### 2. Create and activate a virtual environment

```sh
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 3. Install dependencies and prepare environment

```sh
pip install -r requirements.txt
```

### 4. Fill in your `.env` file

Copy `example.env` to `.env` using next command:

```sh
make prepare-env
```

and fill in all required variables.

### 5. Set the database preparation mode

Set the environment variable in your `.env`:

```
PREPARE_DB=PROD
```

### 6. Apply database migrations

```sh
make up-infra
```
- After this command, the script creates the database with the specified name in .env and applies Alembic migrations to the local database.

### 7. Launch the application

```sh
python main.py
```

The API will be available at [http://localhost:8000](http://localhost:8000).

---

## Test Database (Optional)

- For testing, you can spin up a PostgreSQL container and run Alembic migrations for it.
- Set `PREPARE_DB=TEST` in your `.env` and use the appropriate `make` command:

```sh
make up-test-infra
```
- After this command, Alembic migrations will be applied to the Docker database.

---

## API Documentation

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## External API Integration

This project uses [Coinlore API](https://www.coinlore.com/cryptocurrency-data-api) for real-time currency and cryptocurrency rates.  
No API key is required for Coinlore.

---
