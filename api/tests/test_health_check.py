def test_return_success_when_accessing_health_check(api_client):
    response = api_client.get("/api/", format="json")
    assert response.status_code == 200
    assert list(response.json().keys()) == ["status", "time"]
    assert response.json().get("status") == "available"
