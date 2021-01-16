import pytest


class TestHome:
    def test_append_google_analytics_key(self, settings, client):
        settings.GOOGLE_ANALYTICS_KEY = "UA-000000000-1"
        response = client.get("/")
        assert "UA-000000000-1" in str(response.content)


@pytest.mark.django_db
class TestAdmin:
    def test_append_google_analytics_key(self, settings, admin_client):
        settings.GOOGLE_ANALYTICS_KEY = "UA-000000000-1"
        response = admin_client.get("/admin/")
        assert "UA-000000000-1" in str(response.content)


@pytest.mark.django_db
class TestPanel:
    def test_append_google_analytics_key(self, settings, client):
        settings.GOOGLE_ANALYTICS_KEY = "UA-000000000-1"
        response = client.get("/painel/")
        assert "UA-000000000-1" in str(response.content)
