# GeoSpots (Django + GeoDjango + PostGIS + Docker)



## Cómo levantar contenedores de docker
```bash
docker compose build
docker compose up -d
```

### Aplicar migraciones en la base de datos
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### Cárgar los datos de LK_SPOTS.csv
```bash
docker compose exec web python manage.py load_data --csv data/LK_SPOTS.csv
```


## Cómo correr los tests desde el contenedor
```bash
docker compose exec web python manage.py test spots
```


## Modelo de datos

### Entidades principales

| Modelo | Campos relevantes | Descripción |
|---------|------------------|--------------|
| **State** | `name`, `geom` | Estado o provincia |
| **Municipality** | `name`, `state`, `geom` | Municipalidad o alcaldía |
| **Settlement** | `name`, `municipality` | Colonia o barrio |
| **Region** | `name`, `geom` | Segmentación comercial |
| **Corridor** | `name` | Corredor comercial |
| **Spot** | `location (PointField)`, `sector_id`, `type_id`, `modality`, precios, relaciones FK | Entidad principal con ubicación geográfica |


### Campos geoespaciales utilizados

| Modelo | Campo | Tipo geoespacial | SRID | Descripción |
|---------|--------|------------------|------|--------------|
| `Spot` | `location` | `PointField` | 4326 | Punto con coordenadas (latitud, longitud) que representa la ubicación exacta del spot. |
| `Municipality` | `geom` | `MultiPolygonField` | 4326 | Polígono o conjunto de polígonos que representa los límites del municipio. |
| `State` | `geom` | `MultiPolygonField` | 4326 | Polígonos que delimitan el estado o provincia. |
