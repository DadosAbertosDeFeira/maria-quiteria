import json
from unittest import mock

import pytest
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory, force_authenticate

from web.api.views import HealthCheckView


class TestHealthCheck:
    def get_restrict_permissions(self):
        return [IsAuthenticated()]

    @pytest.fixture
    def mocked_get_permissions(self):
        return mock.patch("web.api.views.HealthCheckView.get_permissions")

    @pytest.fixture
    def authenticated_request(self, url, user):
        factory = APIRequestFactory()
        request = factory.get(url)
        request.user = user
        force_authenticate(request, user)
        return request

    def test_return_success_when_accessing_health_check(self, api_client, url):
        response = api_client.get(url, format="json")
        assert response.status_code == 200
        assert list(response.json().keys()) == ["status", "time"]
        assert response.json().get("status") == "available"

    # TODO Ajustar este teste quando houver uma rota restrita
    def test_return_forbidden_when_trying_to_anonymously_access_a_restricted_route(
        self, api_client, mocked_get_permissions
    ):
        with mocked_get_permissions as mocked_view:
            mocked_view.side_effect = self.get_restrict_permissions
            response = api_client.get("/api/", format="json")
            assert response.status_code == 403

    # TODO Ajustar este teste quando houver uma rota restrita
    def test_return_success_when_accessing_a_restricted_route_with_credentials(
        self, authenticated_request, mocked_get_permissions
    ):
        with mocked_get_permissions as mocked_view:
            mocked_view.side_effect = self.get_restrict_permissions
            view = HealthCheckView.as_view()
            response = view(authenticated_request)
            json_response = json.loads(response.rendered_content)
            assert response.status_code == 200
            assert list(json_response.keys()) == ["status", "time"]
            assert json_response.get("status") == "available"
