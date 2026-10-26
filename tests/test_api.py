def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_ready"] is True

def test_country_prediction(client):
    response = client.get("/predict", params={"country": "India", "horizon": 5})
    assert response.status_code == 200
    body = response.json()
    assert body["scope"] == "country"
    assert body["country"] == "India"
    assert len(body["predictions"]) == 5

def test_all_country_prediction(client):
    response = client.get("/predict", params={"horizon": 3})
    assert response.status_code == 200
    assert response.json()["scope"] == "all_countries"
    assert len(response.json()["predictions"]) == 3

def test_unknown_country_returns_404(client):
    assert client.get("/predict", params={"country": "Atlantis"}).status_code == 404

def test_metrics_endpoint(client):
    client.get("/predict", params={"country": "India"})
    metrics = client.get("/metrics").json()
    assert metrics["request_count"] == 1
    assert metrics["latency_samples"] == 1
