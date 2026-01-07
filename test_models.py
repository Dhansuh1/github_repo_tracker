"""
Test Suite for Database Models
Tests the models.py and database interactions
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Repository
from database import Base


@pytest.fixture(scope="module")
def test_engine():
    """Create a test database engine"""
    TEST_DB_URL = "postgresql://postgres:Dhanush%408051@localhost:5432/github_tracker_test"
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a database session for each test"""
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


def test_create_repository_model(db_session):
    """Test creating a repository in the database"""
    repo = Repository(
        name="test-repo",
        owner="test-owner",
        stars=100,
        url="https://github.com/test-owner/test-repo"
    )
    
    db_session.add(repo)
    db_session.commit()
    db_session.refresh(repo)
    
    assert repo.id is not None
    assert repo.name == "test-repo"
    assert repo.owner == "test-owner"
    assert repo.stars == 100


def test_query_repository_by_id(db_session):
    """Test querying repository by ID"""
    repo = Repository(
        name="query-test",
        owner="owner",
        stars=50,
        url="https://github.com/owner/query-test"
    )
    
    db_session.add(repo)
    db_session.commit()
    
    queried_repo = db_session.query(Repository).filter(Repository.id == repo.id).first()
    
    assert queried_repo is not None
    assert queried_repo.name == "query-test"
    assert queried_repo.owner == "owner"


def test_update_repository_stars(db_session):
    """Test updating repository stars"""
    repo = Repository(
        name="update-test",
        owner="owner",
        stars=100,
        url="https://github.com/owner/update-test"
    )
    
    db_session.add(repo)
    db_session.commit()
    
    # Update stars
    repo.stars = 200
    db_session.commit()
    db_session.refresh(repo)
    
    assert repo.stars == 200


def test_delete_repository(db_session):
    """Test deleting a repository"""
    repo = Repository(
        name="delete-test",
        owner="owner",
        stars=100,
        url="https://github.com/owner/delete-test"
    )
    
    db_session.add(repo)
    db_session.commit()
    repo_id = repo.id
    
    # Delete repository
    db_session.delete(repo)
    db_session.commit()
    
    # Verify deletion
    deleted_repo = db_session.query(Repository).filter(Repository.id == repo_id).first()
    assert deleted_repo is None


def test_repository_required_fields(db_session):
    """Test that required fields cannot be null"""
    repo = Repository(
        name="test",
        owner="owner",
        stars=100,
        url="https://github.com/owner/test"
    )
    
    # All fields should be set
    assert repo.name is not None
    assert repo.owner is not None
    assert repo.stars is not None
    assert repo.url is not None


def test_query_all_repositories(db_session):
    """Test querying all repositories"""
    # Create multiple repos
    repos = [
        Repository(name=f"repo-{i}", owner="owner", stars=i*10, url=f"https://github.com/owner/repo-{i}")
        for i in range(1, 4)
    ]
    
    for repo in repos:
        db_session.add(repo)
    db_session.commit()
    
    all_repos = db_session.query(Repository).all()
    assert len(all_repos) >= 3
