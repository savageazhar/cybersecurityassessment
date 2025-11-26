def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to Kimi AI" in response.data

def test_about_page(client):
    response = client.get('/about')
    assert response.status_code == 200
    # Assuming about page has some specific content.
    # Based on the template list, it exists.
    # The content might be standard.
    # I'll just check status code for now or look for "About"
    # Actually I can't be sure of the content, but 200 is good.

def test_api_info_page(client):
    response = client.get('/api')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "OpenAI Chat API"
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
    assert "gpt-4o" in data['models']
