# 🗺️ GeoSpots API

API REST desarrollada con **Django 5 + GeoDjango + PostgreSQL/PostGIS + Docker**, capaz de exponer datos geoespaciales y realizar consultas espaciales eficientes.

---

## 🚀 Objetivo del Challenge

Evaluar habilidades en el desarrollo de una API geoespacial que permita:
- Cargar un dataset inicial en la base de datos mediante un *management command* de Django.
- Exponer endpoints REST con filtros, búsquedas espaciales y agregaciones.
- Ejecutarse dentro de un entorno reproducible con **Docker Compose**.

---

## 🧹 Tecnologías utilizadas

- **Python 3.12**
- **Django 5**
- **Django REST Framework**
- **GeoDjango**
- **PostgreSQL + PostGIS**
- **Docker / docker-compose**
- **pytest / APITestCase** (para tests)

---

## ⚙️ Instrucciones de ejecución

### 1️⃣ Clonar el proyecto
```bash
git clone https://github.com/usuario/geospots.git
cd geospots
```

### 2️⃣ Construir y levantar los contenedores
```bash
docker compose build
docker compose up -d
```

Esto levanta dos servicios:
- `web`: aplicación Django
- `db`: PostgreSQL con extensión PostGIS habilitada

### 3️⃣ Aplicar migraciones
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### 4️⃣ (Opcional) Crear un superusuario
```bash
docker compose exec web python manage.py createsuperuser
```

La aplicación estará disponible en [http://localhost:8000](http://localhost:8000).

---

## 📦 Carga inicial de datos

El proyecto incluye un *management command* llamado `load_data` para importar los datos del dataset `LK_SPOTS.csv`.

### ▶️ Ejecución
```bash
docker compose exec web python manage.py load_data --csv data/LK_SPOTS.csv
```

### 🗁️ Estructura esperada del archivo
El CSV debe contener las siguientes columnas mínimas:

```
spot_id, spot_sector_id, spot_type_id, spot_settlement, spot_municipality,
spot_state, spot_region, spot_corridor, spot_latitude, spot_longitude,
spot_area_in_sqm, spot_price_sqm_mxn_rent, spot_price_total_mxn_rent,
spot_price_sqm_mxn_sale, spot_price_total_mxn_sale, spot_modality,
uuiid, spot_created_date
```

Ejemplo:
```
25564,13,2,POBLADO COMPUERTAS,Mexicali,Baja California,North,,32.6534234,-115.3740755,6800,400,2720000,,,Rent,5,29/2/2024
28099,15,1,REAL DEL RIO,Mexicali,Baja California,North,,32.6478699,-115.5325106,3637,100,363700,10000,36370000,Rent & Sale,13934,4/7/2024
```

### 🧬 Qué hace el comando

- Crea jerarquías normalizadas:
  - `State` → `Municipality` → `Settlement`
  - `Region` y `Corridor`
- Inserta los `Spot` con su ubicación (`PointField`) y atributos numéricos.
- Mapea automáticamente la modalidad:
  - `"Rent"` → `rent`
  - `"Sale"` → `sale`
  - `"Rent & Sale"` → `rent_sale`
- Usa `update_or_create()` para que sea idempotente.
- Ejecuta todo en una transacción atómica.

---

## 🧱 Diseño del modelo de datos

### Entidades principales

| Modelo | Campos relevantes | Descripción |
|---------|------------------|--------------|
| **State** | `name`, `geom` *(MultiPolygonField)* | Estado o provincia |
| **Municipality** | `name`, `state`, `geom` | Municipalidad o alcaldía |
| **Settlement** | `name`, `municipality` | Colonia o barrio |
| **Region** | `name`, `geom` *(opcional)* | Segmentación comercial |
| **Corridor** | `name` | Corredor comercial |
| **Spot** | `location (PointField)`, `sector_id`, `type_id`, `modality`, precios, relaciones FK | Entidad principal con ubicación geográfica |

### Jerarquía

```
State → Municipality → Settlement → Spot
```

### Campos geoespaciales utilizados

| Modelo | Campo | Tipo geoespacial | SRID | Descripción |
|---------|--------|------------------|------|--------------|
| `Spot` | `location` | `PointField` | 4326 | Punto con coordenadas (latitud, longitud) que representa la ubicación exacta del spot. |
| `Municipality` | `geom` | `MultiPolygonField` *(opcional)* | 4326 | Polígono o conjunto de polígonos que representa los límites del municipio. |
| `State` | `geom` | `MultiPolygonField` *(opcional)* | 4326 | Polígonos que delimitan el estado o provincia. |

---

## 🌍 Endpoints implementados

### 1️⃣ Health Check
**GET** `/api/health/`

Endpoint simple para verificar el estado de la API.

**Ejemplo de respuesta:**
```json
{
  "status": "ok"
}
```

---

### 2️⃣ Listar todos los spots
**GET** `/api/spots/`

Devuelve la lista **paginada** de todos los spots cargados.

**Parámetros opcionales:**
- `page` → número de página (por defecto: 1)

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

### 3️⃣ Búsqueda geoespacial – spots cercanos
**GET** `/api/spots/nearby/?lat=19.4326&lng=-99.1332&radius=2000`

Permite buscar todos los spots dentro de un radio en metros desde una ubicación geográfica dada.

**Parámetros obligatorios:**
- `lat` → latitud (float)
- `lng` → longitud (float)

**Parámetro opcional:**
- `radius` → radio en **metros** (float, default: 1000)

**Ejemplo de request:**
```
GET /api/spots/nearby/?lat=19.4326&lng=-99.1332&radius=2000
```

**Ejemplo de respuesta:**
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
    {
      "spot_id": "S2",
      "title": "Near ~1.1km",
      "location": {"type":"Point","coordinates":[-99.1332,19.4426]},
      "sector_id": 9,
      "type_id": 1,
      "modality": "rent"
    }
  ]
}
```

**Validaciones:**
- Si falta `lat` o `lng`, retorna `400 Bad Request`.
- Si `radius` no es numérico, también retorna `400 Bad Request`.
- Los resultados se ordenan por **distancia ascendente**.

---

## 🔜 Próximos endpoints a implementar

| N° | Endpoint | Descripción |
|----|-----------|--------------|
| 4️⃣ | `POST /api/spots/within/` | Spots dentro de un polígono (consulta espacial) |
| 5️⃣ | `GET /api/spots/?sector=9&type=1&municipality=Álvaro Obregón` | Filtros por atributos |
| 6️⃣ | `GET /api/spots/average-price-by-sector/` | Promedio de precios por sector |
| 7️⃣ | `GET /api/spots/{spot_id}/` | Detalle de un spot |
| 8️⃣ | `GET /api/spots/top-rent/?limit=10` | Ranking por precio total de renta |

---

## 🤪 Tests

Ejecutar los tests desde el contenedor:

```bash
# Todos los tests
docker compose exec web python manage.py test

# Solo los de spots
docker compose exec web python manage.py test spots
```

O si usás pytest:

```bash
docker compose exec web pytest
```

---

## 🧠 Decisiones técnicas

- **Modelado jerárquico** para mantener integridad (State → Municipality → Settlement).
- **Uso de campos geoespaciales** (`PointField`, `MultiPolygonField`) respaldados por PostGIS para búsquedas eficientes.
- **Normalización** de entidades frecuentes (`Region`, `Corridor`) para evitar duplicados.
- **Management command** personalizado (`load_data`) para carga idempotente.
- **Docker Compose** garantiza un entorno reproducible sin dependencias locales.
- **Pruebas automáticas** con `APITestCase` / `pytest-django`.

---

## 🧾 Licencia

Proyecto de práctica técnica – uso académico y demostrativo.

---

**Autor:** [Federico Stulich](https://github.com/federicostulich)  
**Challenge:** GeoDjango + PostGIS API

