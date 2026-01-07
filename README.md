# GitHub Repository Tracker

A FastAPI-based service for tracking GitHub repositories, allowing users to create, read, update, and delete repository records by fetching data from the GitHub API.

## 1. Problem Understanding & Assumptions

### Interpretation

The core requirement is to build a RESTful API service that interacts with the GitHub API to track repository information. Users can manage repository records in a local database, with data initially populated from GitHub.

### Use Case

This service is designed for developers or organizations who want to maintain a local cache of GitHub repository information for analysis, monitoring, or integration purposes. For example, tracking star counts over time or maintaining a curated list of repositories.

### Assumptions

- **Data Formats**: Repository data is fetched from GitHub's public API in JSON format. We assume the API response structure remains consistent as per GitHub's documentation.
- **External API Reliability**: GitHub API is assumed to be available and responsive. No caching mechanism is implemented beyond the local database.
- **User Authentication**: No user authentication is required for the API endpoints. The service assumes it's used in a trusted environment or behind an authentication layer.
- **Business Logic Constraints**: Only public repositories are supported (no GitHub authentication). Repository uniqueness is not enforced (same repo can be added multiple times). Stars can be manually updated via PUT endpoint.
- **Database**: PostgreSQL is used as the database.The PostgreSQL database must exist, but tables are automatically created at application startup using SQLAlchemy metadata.
- **Ambiguous Requirements**: For the PUT endpoint, "stars" is the only updatable field. If other fields need updating, the endpoint would need modification.

## 2. Design Decisions

### Database Schema

- **Table: repositories**
  - `id`: Primary key, auto-incrementing integer for unique identification.
  - `name`: String, repository name (nullable=False).
  - `owner`: String, repository owner/login (nullable=False).
  - `stars`: Integer, current star count (nullable=False).
  - `url`: String, GitHub URL (nullable=False).
- **Indexing**: Primary key index on `id` for fast lookups. No additional indexes as the dataset is assumed to be small.
- **Choice Rationale**: Simple schema matching GitHub's core repository fields. Integer for stars allows for easy updates and comparisons.

### Project Structure

- **Layered Architecture**:
  - `main.py`: Application entry point and API routes.
  - `models.py`: SQLAlchemy ORM models.
  - `schemas.py`: Pydantic schemas for request/response validation.
  - `database.py`: Database connection and session management.
  - `external_api.py`: External API interaction logic.
  - `requirements.txt`: Python dependencies.
  - `.env`: Environment variables (not committed to version control).
- **Rationale**: Separation of concerns with clear boundaries between data access, business logic, and API presentation.

### Validation Logic

- **Pydantic Schemas**: Used for input validation (RepoCreate) and response serialization (RepoResponse).
- **URL Validation**: RepoResponse uses HttpUrl for URL field to ensure valid URLs.
- **ORM Mode**: Enabled in RepoResponse for automatic conversion from SQLAlchemy models.
- **Beyond Basic Types**: No additional custom validators, but Pydantic handles type coercion and validation automatically.

### External API Design

- **Library**: httpx for async HTTP requests to GitHub API.
- **Timeout**: 5-second timeout to prevent hanging requests.
- **Authentication**: None (public API only).
- **Rate Limits**: Not handled explicitly; relies on GitHub's rate limits for unauthenticated requests.
- **Error Handling**: Basic raise_for_status() for HTTP errors.

## 3. Solution Approach

1. **API Request**: Client sends POST /repos with owner and repo_name.
2. **External Fetch**: Service calls GitHub API to fetch repository data.
3. **Data Extraction**: Extracts name, owner, stars, and URL from GitHub response.
4. **Database Storage**: Creates new Repository record in PostgreSQL.
5. **Response**: Returns the created repository data.
6. **CRUD Operations**: GET, PUT, DELETE endpoints operate directly on local database.

Data flow: Client → FastAPI Route → External API Call → Database → Response.

## 4. Error Handling Strategy

- **GitHub API Failures**: HTTPException with 502 status if fetch_github_repo raises any exception.
- **Database Errors**: SQLAlchemy handles connection issues; unhandled exceptions would propagate.
- **Not Found**: 404 for repository not found in GET/PUT/DELETE.
- **Global Exception Handlers**: Not implemented; relies on FastAPI's default error responses.
- **Middleware**: No custom middleware for error handling.
- **Failure Management**: DB connection failures would cause application startup failure. API downtime results in 502 errors. No retry logic or fallback mechanisms.

## 5. How to Run the Project

### Setup Instructions

1. **Clone/Navigate to Project Directory**:

   ```
   cd ../github_repo_tracker
   ```

2. **Create Virtual Environment**:

   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**:

   ```
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the project root:

   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/github_tracker
   ```

   Replace with your actual PostgreSQL connection string.

5. **Run the Application**:
   ```
   python main.py
   ```
   Or with uvicorn:
   ```
   uvicorn main:app --reload
   ```

The API will be available at `http://127.0.0.1:8000`.

### Example API Calls

#### Create a Repository

```bash
curl -X POST "http://127.0.0.1:8000/repos" \
     -H "Content-Type: application/json" \
     -d '{"owner": "octocat", "repo_name": "Hello-World"}'
```

#### Get a Repository

```bash
curl -X GET "http://127.0.0.1:8000/repos/1"
```

#### Update Stars

```bash
curl -X PUT "http://127.0.0.1:8000/repos/1?stars=150"
```

#### Delete a Repository

```bash
curl -X DELETE "http://127.0.0.1:8000/repos/1"
```

### Swagger Documentation

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.
