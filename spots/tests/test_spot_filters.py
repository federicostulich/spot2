from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from spots.models import Spot, State, Municipality, Settlement


class SpotsFilterTests(APITestCase):
    def setUp(self):
        st = State.objects.create(name="Ciudad de México")
        muni_ao = Municipality.objects.create(name="Álvaro Obregón", state=st)
        setl_ao = Settlement.objects.create(name="Col. A", municipality=muni_ao)

        muni_co = Municipality.objects.create(name="Coyoacán", state=st)
        setl_co = Settlement.objects.create(name="Col. C", municipality=muni_co)

        Spot.objects.create(
            spot_id=25001,
            title="AO retail single",
            sector_id=12,
            type_id=1,
            modality="rent",
            settlement=setl_ao,
            location=Point(-99.2, 19.4, srid=4326),
        )
        Spot.objects.create(
            spot_id=25502,
            title="AO industrial complex",
            sector_id=9,
            type_id=2,
            modality="rent",
            settlement=setl_ao,
            location=Point(-99.21, 19.41, srid=4326),
        )
        Spot.objects.create(
            spot_id=25503,
            title="AO industrial single",
            sector_id=9,
            type_id=1,
            modality="rent",
            settlement=setl_ao,
            location=Point(-99.205, 19.405, srid=4326),
        )
        Spot.objects.create(
            spot_id=25504,
            title="CO industrial single",
            sector_id=9,
            type_id=1,
            modality="rent",
            settlement=setl_co,
            location=Point(-99.14, 19.33, srid=4326),
        )

    def test_filter_by_sector_and_type_and_municipality(self):
        url = "/api/spots/?sector=9&type=1&municipality=Álvaro Obregón"
        r = self.client.get(url)
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 1
        ids = [x["spot_id"] for x in data["results"]]
        assert ids == [25503]

    def test_filter_by_municipality_case_insensitive(self):
        url = "/api/spots/?municipality=álVaro obReGón"
        r = self.client.get(url)
        assert r.status_code == 200
        data = r.json()
        ids = sorted(x["spot_id"] for x in data["results"])
        assert set(ids) == {25001, 25502, 25503}

    def test_filter_by_sector_only(self):
        url = "/api/spots/?sector=12"
        r = self.client.get(url)
        assert r.status_code == 200
        data = r.json()
        ids = [x["spot_id"] for x in data["results"]]
        assert ids == [25001]

    def test_filter_by_type_only(self):
        url = "/api/spots/?type=2"
        r = self.client.get(url)
        assert r.status_code == 200
        data = r.json()
        ids = [x["spot_id"] for x in data["results"]]
        assert ids == [25502]
