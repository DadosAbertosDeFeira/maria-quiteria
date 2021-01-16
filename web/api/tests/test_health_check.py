import pytest
from django.urls import reverse


class TestHealthCheck:
    def test_return_success_when_accessing_health_check(self, api_client, url):
        response = api_client.get(url, format="json")
        assert response.status_code == 200
        assert list(response.json().keys()) == ["status", "time"]
        assert response.json().get("status") == "available"

    def test_return_forbidden_when_trying_to_anonymously_access_a_restricted_route(
        self, api_client
    ):
        url = reverse("gazettes-list")
        response = api_client.get(url)
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_return_success_when_accessing_a_restricted_route_with_credentials(
        self, api_client_authenticated
    ):
        url = reverse("gazettes-list")
        response = api_client_authenticated.get(url)
        assert response.status_code == 200
