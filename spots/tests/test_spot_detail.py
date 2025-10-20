from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase
from spots.models import Spot, State, Municipality, Settlement

class SpotDetailTests(APITestCase):
    def setUp(self):
        st = State.objects.create(name="Ciudad de México")
        muni = Municipality.objects.create(name="Álvaro Obregón", state=st)
        setl = Settlement.objects.create(name="Col. A", municipality=muni)

        self.spot = Spot.objects.create(
            spot_id=25564,
            title="Num ID",
            sector_id=9,
            type_id=2,
            modality="rent",
            settlement=setl,
            location=Point(-99.1332, 19.4326, srid=4326),
            area_sqm=6800,
            price_total_rent_mxn=2720000,
        )

    def test_detail_by_numeric_spot_id(self):
        r = self.client.get("/api/spots/25564/")
        assert r.status_code == 200
        data = r.json()
        assert data["spot_id"] == 25564
        assert data["title"] == "Num ID"

    def test_non_numeric_spot_id_returns_404(self):
        r = self.client.get("/api/spots/ABC123/")
        assert r.status_code == 404

    def test_detail_not_found(self):
        r = self.client.get("/api/spots/999999/")
        assert r.status_code == 404
