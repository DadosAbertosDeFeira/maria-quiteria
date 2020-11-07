from rest_framework.test import APITestCase


class HealthCheckTests(APITestCase):
    def setUp(self):
        self.response = self.client.get("/web-api/", HTTP_HOST="localhost:8000")
        self.content = self.response.json()

    def test_status_code_health_check(self):
        self.assertEquals(self.response.status_code, 200)

    def test_content_health_check(self):
        self.assertEquals(["status", "time"], list(self.content.keys()))
        self.assertEquals(self.content.get("status"), "available")
