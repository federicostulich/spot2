from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from spots.models import Spot, State, Municipality, Settlement

class TopRentRankingTests(APITestCase):
    def setUp(self):
        st = State.objects.create(name="Ciudad de México")
        muni_ao = Municipality.objects.create(name="Álvaro Obregón", state=st)
        muni_co = Municipality.objects.create(name="Coyoacán", state=st)
        setl_ao = Settlement.objects.create(name="Col. A", municipality=muni_ao)
        setl_co = Settlement.objects.create(name="Col. C", municipality=muni_co)

        Spot.objects.create(
            spot_id=101, title="A-5000", sector_id=9, type_id=1, modality="rent",
            settlement=setl_ao, location=Point(-99.2, 19.4, srid=4326),
            price_total_rent_mxn=5000,
        )
        Spot.objects.create(
            spot_id=102, title="B-2000", sector_id=9, type_id=1, modality="rent",
            settlement=setl_ao, location=Point(-99.21, 19.41, srid=4326),
            price_total_rent_mxn=2000,
        )
        Spot.objects.create(
            spot_id=103, title="C-8000", sector_id=12, type_id=2, modality="rent",
            settlement=setl_co, location=Point(-99.22, 19.39, srid=4326),
            price_total_rent_mxn=8000,
        )
        Spot.objects.create(
            spot_id=104, title="D-NULL", sector_id=12, type_id=2, modality="rent",
            settlement=setl_co, location=Point(-99.23, 19.395, srid=4326),
            price_total_rent_mxn=None,
        )
        Spot.objects.create(
            spot_id=105, title="E-7000", sector_id=12, type_id=1, modality="rent",
            settlement=setl_ao, location=Point(-99.19, 19.41, srid=4326),
            price_total_rent_mxn=7000,
        )

    def test_top_rent_default_limit(self):
        r = self.client.get("/api/spots/top-rent/")
        assert r.status_code == 200
        data = r.json()
        titles = [x["title"] for x in data]
        assert titles[:4] == ["C-8000", "E-7000", "A-5000", "B-2000"]

    def test_top_rent_with_limit(self):
        r = self.client.get("/api/spots/top-rent/?limit=3")
        assert r.status_code == 200
        data = r.json()
        titles = [x["title"] for x in data]
        assert titles == ["C-8000", "E-7000", "A-5000"]
        assert len(data) == 3

    def test_top_rent_ignores_invalid_limit(self):
        r = self.client.get("/api/spots/top-rent/?limit=notanumber")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 4

    def test_top_rent_respects_filters(self):
        r = self.client.get("/api/spots/top-rent/?municipality=Álvaro Obregón&limit=5")
        assert r.status_code == 200
        data = r.json()
        titles = [x["title"] for x in data]
        assert titles == ["E-7000", "A-5000", "B-2000"]
