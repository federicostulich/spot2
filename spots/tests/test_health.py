from rest_framework.test import APITestCase, APIClient

class HealthTest(APITestCase):
    def test_health_ok(self):
        client = APIClient()
        resp = client.get("/api/health/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})
