"""
Integration Tests - End-to-End Workflow Testing
Tests complete user workflows combining multiple operations
"""
import pytest


def test_complete_crud_workflow(client, monkeypatch):
    """Test complete Create -> Read -> Update -> Delete workflow"""
    
    async def mock_fetch(owner: str, repo: str):
        return {
            "name": "workflow-test",
            "owner": {"login": "testuser"},
            "stargazers_count": 50,
            "html_url": "https://github.com/testuser/workflow-test"
        }
    
    monkeypatch.setattr("main.fetch_github_repo", mock_fetch)
    

    create_response = client.post(
        "/repos",
        json={"owner": "testuser", "repo_name": "workflow-test"}
    )
    assert create_response.status_code == 201
    repo_id = create_response.json()["id"]
    assert create_response.json()["stars"] == 50
    
 
    get_response = client.get(f"/repos/{repo_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "workflow-test"
    assert get_response.json()["stars"] == 50
    
   
    update_response = client.put(f"/repos/{repo_id}?stars=150")
    assert update_response.status_code == 200
    
   
    verify_response = client.get(f"/repos/{repo_id}")
    assert verify_response.json()["stars"] == 150

    delete_response = client.delete(f"/repos/{repo_id}")
    assert delete_response.status_code == 204
    
   
    final_check = client.get(f"/repos/{repo_id}")
    assert final_check.status_code == 404


def test_multiple_repositories_workflow(client, monkeypatch):
    """Test creating and managing multiple repositories"""
    
    def create_mock_response(name, owner, stars):
        return {
            "name": name,
            "owner": {"login": owner},
            "stargazers_count": stars,
            "html_url": f"https://github.com/{owner}/{name}"
        }
    
    async def mock_fetch(owner: str, repo: str):
     
        if repo == "repo1":
            return create_mock_response("repo1", owner, 100)
        elif repo == "repo2":
            return create_mock_response("repo2", owner, 200)
        else:
            return create_mock_response("repo3", owner, 300)
    
    monkeypatch.setattr("main.fetch_github_repo", mock_fetch)
    
  
    repo_ids = []
    for i in range(1, 4):
        response = client.post(
            "/repos",
            json={"owner": "testuser", "repo_name": f"repo{i}"}
        )
        assert response.status_code == 201
        repo_ids.append(response.json()["id"])
   
    for repo_id in repo_ids:
        response = client.get(f"/repos/{repo_id}")
        assert response.status_code == 200
    
  
    delete_response = client.delete(f"/repos/{repo_ids[0]}")
    assert delete_response.status_code == 204
    
  
    assert client.get(f"/repos/{repo_ids[0]}").status_code == 404
    assert client.get(f"/repos/{repo_ids[1]}").status_code == 200
    assert client.get(f"/repos/{repo_ids[2]}").status_code == 200


def test_update_same_repo_multiple_times(client, monkeypatch):
    """Test updating the same repository multiple times"""
    
    async def mock_fetch(owner: str, repo: str):
        return {
            "name": "update-test",
            "owner": {"login": "testuser"},
            "stargazers_count": 10,
            "html_url": "https://github.com/testuser/update-test"
        }
    
    monkeypatch.setattr("main.fetch_github_repo", mock_fetch)
    
   
    create_response = client.post(
        "/repos",
        json={"owner": "testuser", "repo_name": "update-test"}
    )
    repo_id = create_response.json()["id"]
    
    
    star_counts = [50, 100, 250, 500, 1000]
    for stars in star_counts:
        update_response = client.put(f"/repos/{repo_id}?stars={stars}")
        assert update_response.status_code == 200
        
       
        get_response = client.get(f"/repos/{repo_id}")
        assert get_response.json()["stars"] == stars


def test_error_recovery_workflow(client, monkeypatch):
    """Test system behavior with errors in the middle of workflow"""
    
    async def mock_fetch(owner: str, repo: str):
        return {
            "name": "error-test",
            "owner": {"login": owner},
            "stargazers_count": 100,
            "html_url": f"https://github.com/{owner}/error-test"
        }
    
    monkeypatch.setattr("main.fetch_github_repo", mock_fetch)
    

    response = client.post(
        "/repos",
        json={"owner": "testuser", "repo_name": "error-test"}
    )
    assert response.status_code == 201
    repo_id = response.json()["id"]
    
   
    response = client.put("/repos/99999?stars=100")
    assert response.status_code == 404
    
    
    response = client.get(f"/repos/{repo_id}")
    assert response.status_code == 200
    
    
    response = client.put(f"/repos/{repo_id}?stars=500")
    assert response.status_code == 200
    
    
    response = client.delete("/repos/99999")
    assert response.status_code == 404
    
 
    response = client.get(f"/repos/{repo_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_concurrent_operations(client, monkeypatch):
    """Test handling of operations that might occur concurrently"""
    
    async def mock_fetch(owner: str, repo: str):
        return {
            "name": "concurrent-test",
            "owner": {"login": owner},
            "stargazers_count": 75,
            "html_url": f"https://github.com/{owner}/concurrent-test"
        }
    
    monkeypatch.setattr("main.fetch_github_repo", mock_fetch)
 
    response = client.post(
        "/repos",
        json={"owner": "user1", "repo_name": "concurrent-test"}
    )
    repo_id = response.json()["id"]
  
    for _ in range(5):
        response = client.get(f"/repos/{repo_id}")
        assert response.status_code == 200
    

    for i in range(100, 600, 100):
        response = client.put(f"/repos/{repo_id}?stars={i}")
        assert response.status_code == 200
    

    response = client.get(f"/repos/{repo_id}")
    assert response.json()["stars"] == 500
