from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from spots.models import Spot, State, Municipality, Settlement


class SpotsWithinPolygonTests(APITestCase):
    def setUp(self):
        st = State.objects.create(name="Ciudad de México")
        muni_ao = Municipality.objects.create(name="Álvaro Obregón", state=st)
        setl_ao = Settlement.objects.create(name="Col. A", municipality=muni_ao)

        muni_co = Municipality.objects.create(name="Coyoacán", state=st)
        setl_co = Settlement.objects.create(name="Col. C", municipality=muni_co)

        self.s1 = Spot.objects.create(
            spot_id=25501, title="AO 1",
            location=Point(-99.21, 19.37, srid=4326),
            sector_id=9, type_id=1, modality="rent", settlement=setl_ao
        )
        self.s2 = Spot.objects.create(
            spot_id=25502, title="AO 2",
            location=Point(-99.22, 19.39, srid=4326),
            sector_id=12, type_id=2, modality="rent", settlement=setl_ao
        )
        self.s3 = Spot.objects.create(
            spot_id=25503, title="CO 1",
            location=Point(-99.14, 19.33, srid=4326),
            sector_id=9, type_id=1, modality="rent", settlement=setl_co
        )

    def test_within_polygon_returns_only_inside(self):
        poly = {
            "type": "Polygon",
            "coordinates": [[
                [-99.25, 19.35],
                [-99.25, 19.41],
                [-99.18, 19.41],
                [-99.18, 19.35]
            ]]
        }
        r = self.client.post("/api/spots/within/", {"polygon": poly}, format="json")
        assert r.status_code == 200
        data = r.json()
        assert set(data.keys()) == {"count", "next", "previous", "results"}
        ids = {x["spot_id"] for x in data["results"]}
        assert ids == {25501, 25502}
        assert data["count"] == 2

    def test_within_polygon_requires_payload(self):
        r = self.client.post("/api/spots/within/", {}, format="json")
        assert r.status_code == 400

    def test_within_polygon_wrong_type(self):
        bad = {"type": "Point", "coordinates": [-99.2, 19.4]}
        r = self.client.post("/api/spots/within/", {"polygon": bad}, format="json")
        assert r.status_code == 400

    def test_within_polygon_invalid_coords(self):
        bad = {"type": "Polygon", "coordinates": []}
        r = self.client.post("/api/spots/within/", {"polygon": bad}, format="json")
        assert r.status_code == 400
