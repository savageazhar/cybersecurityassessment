def test_api_info_page(client):
    response = client.get('/api')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "AI Gateway API"
    assert "endpoints" in data

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == "healthy"

def test_models_list(client):
    response = client.get('/models')
    assert response.status_code == 200
    data = response.get_json()
    assert "models" in data
    assert "gpt-4o" in data['models']['openai']
