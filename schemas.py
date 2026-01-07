from pydantic import BaseModel, HttpUrl, ConfigDict

class RepoCreate(BaseModel):
    owner: str
    repo_name: str

class RepoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    owner: str
    stars: int
    url: HttpUrl
