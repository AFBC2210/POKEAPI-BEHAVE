import pytest
import requests

def test_sample():
    assert 1 + 1 == 2

def test_pikachu_api_response():
    url = "https://pokeapi.co/api/v2/pokemon/pikachu"
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "pikachu"
    assert "abilities" in data
