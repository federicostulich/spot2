from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from spots.models import Spot, State, Municipality, Settlement

class AveragePriceBySectorTests(APITestCase):
    def setUp(self):
        st = State.objects.create(name="Ciudad de México")
        muni_ao = Municipality.objects.create(name="Álvaro Obregón", state=st)
        setl_ao = Settlement.objects.create(name="Col. A", municipality=muni_ao)

        Spot.objects.create(
            spot_id="S-IND-1",
            title="Ind 1",
            sector_id=9, type_id=1, modality="rent",
            location=Point(-99.2, 19.4, srid=4326),
            settlement=setl_ao,
            price_total_rent_mxn=1000,
        )
        Spot.objects.create(
            spot_id="S-IND-2",
            title="Ind 2",
            sector_id=9, type_id=2, modality="rent",
            location=Point(-99.21, 19.41, srid=4326),
            settlement=setl_ao,
            price_total_rent_mxn=3000,
        )
        Spot.objects.create(
            spot_id="S-IND-NULL",
            title="Ind null",
            sector_id=9, type_id=1, modality="rent",
            location=Point(-99.205, 19.405, srid=4326),
            settlement=setl_ao,
            price_total_rent_mxn=None,
        )

        Spot.objects.create(
            spot_id="S-RET-1",
            title="Retail 1",
            sector_id=12, type_id=1, modality="rent",
            location=Point(-99.22, 19.39, srid=4326),
            settlement=setl_ao,
            price_total_rent_mxn=500,
        )

    def test_average_price_by_sector(self):
        r = self.client.get("/api/spots/average-price-by-sector/")
        assert r.status_code == 200
        data = r.json()
        by_sector = {row["sector_id"]: row for row in data}

        assert 9 in by_sector
        avg_9 = float(by_sector[9]["average_price_total_rent_mxn"])
        assert abs(avg_9 - 2000.0) < 1e-6

        assert 12 in by_sector
        avg_12 = float(by_sector[12]["average_price_total_rent_mxn"])
        assert abs(avg_12 - 500.0) < 1e-6

    def test_respects_filters_if_present(self):
        r = self.client.get("/api/spots/average-price-by-sector/?municipality=Álvaro Obregón")
        assert r.status_code == 200
        data = r.json()
        by_sector = {row["sector_id"]: row for row in data}
        assert 9 in by_sector and 12 in by_sector
