from decimal import Decimal, InvalidOperation
from datetime import datetime

from spots.models import (
    Spot
)

def norm(s):
    return (s or "").strip()

def to_float(v):
    s = str(v).strip().replace(",", ".") if v is not None else ""
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None

def to_dec(v):
    s = str(v).strip().replace(",", "") if v is not None else ""
    if not s:
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None

def to_int(v):
    try:
        return int(str(v).strip())
    except Exception:
        return None

def parse_date(v):
    """
    Soporta formatos como:
    - 29/2/2024 (dd/mm/yyyy)
    - 4/7/2024  (dd/mm/yyyy)
    - 2024-02-29
    - ISO-8601
    Devuelve datetime o None.
    """
    s = norm(v)
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None

def map_modality(raw):
    s = norm(raw).lower()
    if s in ("rent & sale", "rent_sale", "rentandsale", "both", "rent and sale"):
        return Spot.Modality.RENT_SALE
    if s in ("sale", "venta"):
        return Spot.Modality.SALE
    return Spot.Modality.RENT