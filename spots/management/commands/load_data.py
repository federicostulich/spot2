import csv
from pathlib import Path


from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.db import transaction

from spots.models import (
    Spot, State, Municipality, Settlement, Region, Corridor
)
from spots.management.commands.utils import norm, to_float, to_dec, to_int, parse_date, map_modality


class Command(BaseCommand):
    help = "Carga datos iniciales normalizados desde un CSV. Ej: python manage.py load_data --csv data/LK_SPOTS.csv"

    def add_arguments(self, parser):
        parser.add_argument("--csv", default="data/LK_SPOTS.csv")

    @transaction.atomic
    def handle(self, *args, **opts):
        path = Path(opts["csv"])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f"No existe el archivo CSV: {path}"))
            return

        state_cache = {}
        muni_cache = {}
        settlement_cache = {}
        region_cache = {}
        corridor_cache = {}

        def get_state(name):
            key = norm(name).lower()
            if not key:
                return None
            if key in state_cache:
                return state_cache[key]
            obj, _ = State.objects.get_or_create(name=norm(name))
            state_cache[key] = obj
            return obj

        def get_muni(name, state_obj):
            nkey = norm(name).lower()
            if not nkey or not state_obj:
                return None
            key = (nkey, state_obj.id)
            if key in muni_cache:
                return muni_cache[key]
            obj, _ = Municipality.objects.get_or_create(name=norm(name), state=state_obj)
            muni_cache[key] = obj
            return obj

        def get_settlement(name, muni_obj):
            nkey = norm(name).lower()
            if not nkey or not muni_obj:
                return None
            key = (nkey, muni_obj.id)
            if key in settlement_cache:
                return settlement_cache[key]
            obj, _ = Settlement.objects.get_or_create(name=norm(name), municipality=muni_obj)
            settlement_cache[key] = obj
            return obj

        def get_region(name):
            key = norm(name).lower()
            if not key:
                return None
            if key in region_cache:
                return region_cache[key]
            obj, _ = Region.objects.get_or_create(name=norm(name))
            region_cache[key] = obj
            return obj

        def get_corridor(name):
            key = norm(name).lower()
            if not key:
                return None
            if key in corridor_cache:
                return corridor_cache[key]
            obj, _ = Corridor.objects.get_or_create(name=norm(name))
            corridor_cache[key] = obj
            return obj

        count = 0
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            required = [
                "spot_id", "spot_latitude", "spot_longitude",
                "spot_municipality", "spot_state", "spot_settlement",
            ]
            missing = [c for c in required if c not in reader.fieldnames]
            if missing:
                self.stderr.write(self.style.WARNING(
                    f"Cuidado: faltan columnas esperadas: {missing}. "
                    "Asegurate de usar encabezados snake_case como en el ejemplo."
                ))

            for row in reader:
                spot_id = norm(row.get("spot_id"))
                lat = to_float(row.get("spot_latitude"))
                lng = to_float(row.get("spot_longitude"))

                if not spot_id or lat is None or lng is None:
                    continue

                state = get_state(row.get("spot_state"))
                municipality = get_muni(row.get("spot_municipality"), state)
                settlement = get_settlement(row.get("spot_settlement"), municipality)

                region = get_region(row.get("spot_region"))
                corridor = get_corridor(row.get("spot_corridor"))

                modality = map_modality(row.get("spot_modality"))
                created = parse_date(row.get("spot_created_date"))

                defaults = dict(
                    title=norm(row.get("spot_title")),
                    description=norm(row.get("spot_description")),
                    address=norm(row.get("spot_address")),
                    sector_id=to_int(row.get("spot_sector_id")),
                    type_id=to_int(row.get("spot_type_id")),
                    modality=modality,
                    area_sqm=to_dec(row.get("spot_area_in_sqm")),
                    price_sqm_rent_mxn=to_dec(row.get("spot_price_sqm_mxn_rent")),
                    price_total_rent_mxn=to_dec(row.get("spot_price_total_mxn_rent")),
                    price_sqm_sale_mxn=to_dec(row.get("spot_price_sqm_mxn_sale")),
                    price_total_sale_mxn=to_dec(row.get("spot_price_total_mxn_sale")),
                    maintenance_cost_mxn=to_dec(row.get("spot_maintenance_cost_mxn")),
                    user_id=norm(row.get("uuiid") or row.get("user_id")),
                    created_date=created,
                    location=Point(lng, lat, srid=4326),

                    settlement=settlement,
                    region=region,
                    corridor=corridor,
                )

                Spot.objects.update_or_create(spot_id=spot_id, defaults=defaults)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Cargados/actualizados {count} spots."))
