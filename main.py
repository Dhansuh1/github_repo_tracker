import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
from models import Repository
from schemas import RepoCreate, RepoResponse
from external_api import fetch_github_repo


Base.metadata.create_all(bind=engine)

app = FastAPI(title="GitHub Repository Tracker")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/repos", response_model=RepoResponse, status_code=201)
async def create_repo(payload: RepoCreate, db: Session = Depends(get_db)):
    try:
        data = await fetch_github_repo(payload.owner, payload.repo_name)
    except Exception:
        raise HTTPException(status_code=502, detail="GitHub API failed")

    repo = Repository(
        name=data["name"],
        owner=data["owner"]["login"],
        stars=data["stargazers_count"],
        url=data["html_url"]
    )

    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@app.get("/repos/{repo_id}", response_model=RepoResponse)
def get_repo(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo


@app.put("/repos/{repo_id}")
def update_repo(repo_id: int, stars: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    repo.stars = stars
    db.commit()
    return {"message": "Stars updated"}


@app.delete("/repos/{repo_id}", status_code=204)
def delete_repo(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    db.delete(repo)
    db.commit()



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
