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

---

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


---

## Endpoints implementados
- 1 Health Check: **GET** `/api/health/`
- 2 Listar todos los spots (paginado): **GET** `/api/spots/`
- 3 Búsqueda geoespacial – spots cercanos: **GET** `/api/spots/nearby/?lat=19.4326&lng=-99.1332&radius=2000`
- 4 Búsqueda filtrada por atributos: **GET** `/api/spots/?sector=9&type=1&municipality=Álvaro Obregón`
- 5 Búsqueda geoespacial – spots dentro de un polígono: **POST** `/api/spots/within/`


---

### 1 Health Check

Endpoint simple para verificar el estado de la API.
**GET** `/api/health/`

**Ejemplo de respuesta:**
```json
{
  "status": "ok"
}
```

---

### 2 Listar todos los spots (paginado)
**GET** `/api/spots/`

Parámetros:
- `page` (int, opcional - default:1)

**Ejemplo de request:**
```
GET /api/spots/?page=2
```

**Ejemplo de respuesta:**
```json
{
  "count": 123,
  "next": "http://localhost:8000/api/spots/?page=3",
  "previous": "http://localhost:8000/api/spots/?page=1",
  "results": [
    {
      "id": 1,
      "spot_id": "25564",
      "title": "Industrial Warehouse",
      "sector_id": 9,
      "type_id": 2,
      "modality": "rent",
      "location": {
        "type": "Point",
        "coordinates": [-99.1332, 19.4326]
      },
      "area_sqm": 6800,
      "price_total_rent_mxn": 2720000
    }
  ]
}
```

> La paginación está configurada en `settings.py` con `PAGE_SIZE = 50`.

---

### 3 Búsqueda geoespacial – spots cercanos
**GET** `/api/spots/nearby/?lat=19.4326&lng=-99.1332&radius=2000`

Parámetros:
- `lat` (float, requerido)
- `lng` (float, requerido)
- `radius` (float, metros, opcional, default: 1000)

**Ejemplo de request:**
```
GET /api/spots/nearby/?lat=19.4326&lng=-99.1332&radius=2000
```

Respuesta (paginada):
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "spot_id": "S1",
      "title": "Exact",
      "location": {"type":"Point","coordinates":[-99.1332,19.4326]},
      "sector_id": 9,
      "type_id": 1,
      "modality": "rent"
    },
    ...
  ]
}
```

---

### 4 Búsqueda filtrada por atributos

**GET** `/api/spots/?sector=9&type=1&municipality=Álvaro Obregón`


Parámetros:

- `sector` (int, opcional, Sector id: [`9, 11, 12, 15`])
- `type` (int, opcional, Type id: [`1, 2, 3`])
- `municipality` (string, opcional, nombre del municipio)

**Ejemplo de request:**

```
GET /api/spots/?sector=9&type=1&municipality=Álvaro Obregón
```

**Ejemplo de respuesta (paginada):**

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "spot_id": "S-100",
      "sector_id": 9,
      "type_id": 1,
      "modality": "rent",
      "location": {"type":"Point","coordinates":[-99.2,19.4]},
      "settlement": 123,
      "area_sqm": 1200
    }
  ]
}
```

> El filtro `municipality` compara contra `Settlement → Municipality → name` y no distingue mayúsculas/minúsculas.

---


### 5 Búsqueda geoespacial – spots dentro de un polígono

**POST** `/api/spots/within/`

**Body (JSON):**
```json
{
  "polygon": {
    "type": "Polygon",
    "coordinates": [
      [
        [-99.25, 19.35],
        [-99.25, 19.41],
        [-99.18, 19.41],
        [-99.18, 19.35]
      ]
    ]
  }
}

**Ejemplo de respuesta (paginada):**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "spot_id": "AO-1",
      "title": "AO 1",
      "location": {"type": "Point", "coordinates": [-99.21, 19.37]},
      "sector_id": 9,
      "type_id": 1,
      "modality": "rent"
    },
    {
      "spot_id": "AO-2",
      "title": "AO 2",
      "location": {"type": "Point", "coordinates": [-99.22, 19.39]},
      "sector_id": 12,
      "type_id": 2,
      "modality": "rent"
    }
  ]
}

```