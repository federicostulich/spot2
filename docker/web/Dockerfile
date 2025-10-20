FROM python:3.12-bookworm

ARG DEBIAN_FRONTEND=noninteractive

RUN printf 'Acquire::Retries "3";\n' > /etc/apt/apt.conf.d/80retries \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      gdal-bin libgdal-dev \
      proj-bin libproj-dev \
      gcc g++ build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

ENV PROJ_LIB=/usr/share/proj \
    GDAL_DATA=/usr/share/gdal \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

COPY . .
