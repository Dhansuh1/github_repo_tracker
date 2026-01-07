import pytest
from unittest.mock import AsyncMock, patch


def mock_github_response():
    """Mock GitHub API response"""
    return {
        "name": "fastapi",
        "owner": {"login": "tiangolo"},
        "stargazers_count": 100,
        "html_url": "https://github.com/tiangolo/fastapi"
    }


@pytest.mark.asyncio
async def test_create_repo(client, monkeypatch):
    """Test creating a repository"""
    
    async def mock_fetch(owner: str, repo: str):
        return mock_github_response()

    monkeypatch.setattr(
        "main.fetch_github_repo",
        mock_fetch
    )

    response = client.post(
        "/repos",
        json={"owner": "tiangolo", "repo_name": "fastapi"}
    )

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "fastapi"
    assert data["owner"] == "tiangolo"
    assert data["stars"] == 100
    assert data["url"] == "https://github.com/tiangolo/fastapi"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_repo_github_api_failure(client, monkeypatch):
    """Test creating repository when GitHub API fails"""
    
    async def mock_fetch_error(owner: str, repo: str):
        raise Exception("GitHub API error")

    monkeypatch.setattr(
        "main.fetch_github_repo",
        mock_fetch_error
    )

    response = client.post(
        "/repos",
        json={"owner": "invalid", "repo_name": "invalid"}
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "GitHub API failed"


def test_get_repo_success(client, monkeypatch):
    """Test getting an existing repository"""

    async def mock_fetch(owner: str, repo: str):
        return mock_github_response()

    monkeypatch.setattr("main.fetch_github_repo", mock_fetch)
    
    create_response = client.post(
        "/repos",
        json={"owner": "tiangolo", "repo_name": "fastapi"}
    )
    repo_id = create_response.json()["id"]
    

    response = client.get(f"/repos/{repo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "fastapi"
    assert data["owner"] == "tiangolo"


def test_get_repo_not_found(client):
    """Test getting a non-existent repository"""
    response = client.get("/repos/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found"


def test_update_repo_success(client, monkeypatch):
    """Test updating repository stars"""

    async def mock_fetch(owner: str, repo: str):
        return mock_github_response()

    monkeypatch.setattr("main.fetch_github_repo", mock_fetch)
    
    create_response = client.post(
        "/repos",
        json={"owner": "tiangolo", "repo_name": "fastapi"}
    )
    repo_id = create_response.json()["id"]
 
    response = client.put(f"/repos/{repo_id}?stars=200")
    assert response.status_code == 200
    assert response.json()["message"] == "Stars updated"
    

    get_response = client.get(f"/repos/{repo_id}")
    assert get_response.json()["stars"] == 200


def test_update_repo_not_found(client):
    """Test updating a non-existent repository"""
    response = client.put("/repos/99999?stars=200")
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found"


def test_delete_repo_success(client, monkeypatch):
    """Test deleting a repository"""

    async def mock_fetch(owner: str, repo: str):
        return mock_github_response()

    monkeypatch.setattr("main.fetch_github_repo", mock_fetch)
    
    create_response = client.post(
        "/repos",
        json={"owner": "tiangolo", "repo_name": "fastapi"}
    )
    repo_id = create_response.json()["id"]
    

    response = client.delete(f"/repos/{repo_id}")
    assert response.status_code == 204
    
 
    get_response = client.get(f"/repos/{repo_id}")
    assert get_response.status_code == 404


def test_delete_repo_not_found(client):
    """Test deleting a non-existent repository"""
    response = client.delete("/repos/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found"
