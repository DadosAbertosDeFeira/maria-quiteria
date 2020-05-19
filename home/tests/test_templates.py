from django.test import TestCase


class HomeTest(TestCase):
    def test_append_google_analytics_key(self):
        with self.settings(GOOGLE_ANALYTICS_KEY="UA-000000000-1"):
            response = self.client.get("/")
            self.assertContains(response, "ga('create', 'UA-000000000-1', 'auto')")
