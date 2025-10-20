from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from spots.models import Spot

class SpotsListTests(APITestCase):
    def setUp(self):
        base_lng, base_lat = -99.1332, 19.4326
        for i in range(55):
            Spot.objects.create(
                spot_id=i+25001,
                title=f"Spot {i+1}",
                location=Point(base_lng + i*0.0001, base_lat + i*0.0001, srid=4326),
                sector_id=9,
                type_id=1,
                modality="rent",
            )

    def test_list_first_page_paginated(self):
        resp = self.client.get("/api/spots/")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"count", "next", "previous", "results"}
        assert data["count"] == 55
        assert data["previous"] is None
        assert data["next"] is not None
        assert len(data["results"]) == 50 

    def test_list_second_page_paginated(self):
        resp = self.client.get("/api/spots/?page=2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 55
        assert len(data["results"]) == 5

    def test_list_empty(self):
        Spot.objects.all().delete()
        resp = self.client.get("/api/spots/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["results"] == []
