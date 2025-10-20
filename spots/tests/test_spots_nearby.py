from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from spots.models import Spot

REF_LAT, REF_LNG = 19.4326, -99.1332 


class SpotsNearbyTests(APITestCase):
    def setUp(self):
        Spot.objects.create(
            spot_id="S1",
            title="Exact",
            location=Point(REF_LNG, REF_LAT, srid=4326),
            sector_id=9, type_id=1, modality="rent",
        )
        Spot.objects.create(
            spot_id="S2",
            title="Near ~1.1km",
            location=Point(REF_LNG, REF_LAT + 0.01, srid=4326),
            sector_id=9, type_id=1, modality="rent",
        )
        Spot.objects.create(
            spot_id="S3",
            title="Far ~11km",
            location=Point(REF_LNG, REF_LAT + 0.1, srid=4326),
            sector_id=9, type_id=1, modality="rent",
        )

    def test_nearby_within_2km(self):
        resp = self.client.get(f"/api/spots/nearby/?lat={REF_LAT}&lng={REF_LNG}&radius=2000")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"count", "next", "previous", "results"}
        assert data["count"] == 2 
        ids = [item["spot_id"] for item in data["results"]]
        assert ids[0] == "S1"
        assert "S3" not in ids

    def test_nearby_missing_params(self):
        resp = self.client.get("/api/spots/nearby/?lat=19.4")
        assert resp.status_code == 400

    def test_nearby_very_small_radius(self):
        resp = self.client.get(f"/api/spots/nearby/?lat={REF_LAT}&lng={REF_LNG}&radius=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["spot_id"] == "S1"
