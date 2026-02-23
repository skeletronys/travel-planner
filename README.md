# Travel Planner API

REST API for managing travel projects and places. Uses the [Art Institute of Chicago API](https://api.artic.edu/docs/) to validate and fetch artwork data.

## Stack

- Python 3.12, Django 6, Django REST Framework
- SQLite
- JWT authentication

## Setup

```bash
git clone <repo-url>
cd travel-planner

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.sample .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Docker

```bash
cp .env.sample .env
docker-compose -f docker/docker-compose.yml up --build
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | insecure default | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Allowed hosts |
| `AIC_CACHE_TIMEOUT` | `300` | AIC API cache timeout in seconds |

## Authentication

JWT — all endpoints are protected.

```http
POST /trips/auth/token/
{ "username": "...", "password": "..." }
```

Use the returned `access` token:
```
Authorization: Bearer <access_token>
```

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/trips/auth/token/` | Get token |
| POST | `/trips/auth/token/refresh/` | Refresh token |
| GET | `/trips/projects/` | List projects |
| POST | `/trips/projects/` | Create project |
| GET | `/trips/projects/{id}/` | Get project |
| PATCH | `/trips/projects/{id}/` | Update project |
| DELETE | `/trips/projects/{id}/` | Delete project |
| GET | `/trips/projects/{id}/places/` | List places |
| POST | `/trips/projects/{id}/places/` | Add place |
| GET | `/trips/projects/{id}/places/{place_id}/` | Get place |
| PATCH | `/trips/projects/{id}/places/{place_id}/` | Update place |

## API Docs

Swagger UI available at `http://localhost:8000/trips/docs/`
