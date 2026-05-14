import pytest
from fastapi.testclient import TestClient
import os
from pathlib import Path

# Override data dir for testing
test_data_dir = Path(__file__).parent / "test_data"
test_data_dir.mkdir(exist_ok=True)
os.environ["DATA_DIR"] = str(test_data_dir)

from main import app
client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_and_get_entity():
    # Create entity
    response = client.post("/api/entities", json={
        "name": "Test Runner",
        "entity_type": "character",
        "description": "A character used for testing"
    })
    assert response.status_code == 200
    entity_id = response.json()["id"]

    # Get entity
    response = client.get(f"/api/entities/{entity_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Runner"

import random

def test_create_chapter():
    response = client.post("/api/chapters", json={
        "number": random.randint(1000, 9999),
        "title": "Test Chapter",
        "content": "This is a test chapter. It has some text for semantic search."
    })
    assert response.status_code == 200

def test_memory_search():
    response = client.get("/api/memory/search?q=test&n=1")
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
