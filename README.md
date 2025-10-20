# GeoSpots (Django + GeoDjango + PostGIS + Docker)

Base mínima para el challenge de spots geoespaciales.

## Requisitos
- Docker + Docker Compose (en Windows 10 Home: Docker Desktop con WSL2)
- (Opcional) archivo `.env` basado en `.env.example`

## Cómo levantar
```bash
docker compose up --build
docker compose exec web python manage.py migrate
