"""
Test Suite for Input Validation and Edge Cases
Tests the schemas.py and validates request/response data
"""
import pytest
from pydantic import ValidationError
from schemas import RepoCreate, RepoResponse


def test_repo_create_valid_data():
    """Test RepoCreate with valid data"""
    data = RepoCreate(owner="octocat", repo_name="Hello-World")
    
    assert data.owner == "octocat"
    assert data.repo_name == "Hello-World"


def test_repo_create_missing_owner():
    """Test RepoCreate fails without owner"""
    with pytest.raises(ValidationError) as exc_info:
        RepoCreate(repo_name="test-repo")
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("owner",) for error in errors)


def test_repo_create_missing_repo_name():
    """Test RepoCreate fails without repo_name"""
    with pytest.raises(ValidationError) as exc_info:
        RepoCreate(owner="octocat")
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("repo_name",) for error in errors)


def test_repo_create_empty_strings():
    """Test RepoCreate with empty strings"""
    # Pydantic allows empty strings by default
    data = RepoCreate(owner="", repo_name="")
    assert data.owner == ""
    assert data.repo_name == ""


def test_repo_response_valid_data():
    """Test RepoResponse with valid data"""
    data = RepoResponse(
        id=1,
        name="test-repo",
        owner="octocat",
        stars=100,
        url="https://github.com/octocat/test-repo"
    )
    
    assert data.id == 1
    assert data.name == "test-repo"
    assert data.owner == "octocat"
    assert data.stars == 100
    assert str(data.url) == "https://github.com/octocat/test-repo"


def test_repo_response_invalid_url():
    """Test RepoResponse fails with invalid URL"""
    with pytest.raises(ValidationError) as exc_info:
        RepoResponse(
            id=1,
            name="test",
            owner="owner",
            stars=100,
            url="not-a-valid-url"
        )
    
    errors = exc_info.value.errors()
    assert any("url" in str(error["loc"]) for error in errors)


def test_repo_response_negative_stars():
    """Test RepoResponse with negative stars (should work)"""
    # No validation prevents negative stars
    data = RepoResponse(
        id=1,
        name="test",
        owner="owner",
        stars=-10,
        url="https://github.com/owner/test"
    )
    assert data.stars == -10


def test_repo_response_zero_stars():
    """Test RepoResponse with zero stars"""
    data = RepoResponse(
        id=1,
        name="test",
        owner="owner",
        stars=0,
        url="https://github.com/owner/test"
    )
    assert data.stars == 0


def test_repo_response_large_stars():
    """Test RepoResponse with very large star count"""
    data = RepoResponse(
        id=1,
        name="popular-repo",
        owner="owner",
        stars=1000000,
        url="https://github.com/owner/popular-repo"
    )
    assert data.stars == 1000000


def test_repo_create_special_characters():
    """Test RepoCreate with special characters in names"""
    data = RepoCreate(owner="user-name_123", repo_name="my.repo-name_v2")
    
    assert data.owner == "user-name_123"
    assert data.repo_name == "my.repo-name_v2"


def test_repo_response_missing_required_fields():
    """Test RepoResponse fails without required fields"""
    with pytest.raises(ValidationError):
        RepoResponse(name="test")  # Missing other required fields
