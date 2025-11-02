# FastAPI URL Shortener (v1.3)

A URL shortening service built with Python. This project uses the FastAPI framework and communicates with a PostgreSQL database asynchronously.  
It provides a robust API for creating and managing short links and includes a user authentication system using JWT, atomic click tracking, and a clean, modular project structure.

## Features

- URL shortening for anonymous and authenticated users.
- JWT-based user authentication (signup, login, and delete).
- Redirection from short URLs to their original target URLs.
- Race-condition-safe click tracking using atomic database operations.
- Protected endpoint for link owners to view click statistics.
- Clean, modular code structure using FastAPI's `APIRouter`.

## Tech Stack

**Backend:** Python, FastAPI  
**Database:** PostgreSQL, SQLAlchemy (with Asyncio)  
**Authentication:** Passlib, python-jose  
**Data Validation:** Pydantic
**Containerization:** Docker, Docker Compose

## Project Structure

The project is organized into a modular `app` package for clean separation of concerns:

```
app/
├── __init__.py
├── crud.py          # Database read/write/update logic
├── database.py      # Async database engine and session
├── dependencies.py  # Reusable dependencies (get_db, get_current_user)
├── jwt_utils.py     # JWT token creation
├── main.py          # Main FastAPI app assembly and startup
├── models.py        # SQLAlchemy database models
├── password_utils.py # Password hashing and verification
├── schemas.py       # Pydantic data models (validation/response)
├── utils.py         # Helper functions (e.g., short_code generation)
└── routers/
    ├── __init__.py
    ├── links.py     # API routes for /links
    └── users.py     # API routes for /users
```

## API Endpoints

The API is documented automatically using FastAPI's OpenAPI integration, available at `/docs` when the server is running.

### User Authentication (`/users`)

| Method | Path          | Description                       |
| ------ | ------------- | --------------------------------- |
| POST   | /users/signup | Register a new user account.      |
| POST   | /users/login  | Log in to get a JWT access token. |
| DELETE | /users/delete | (Protected) Delete your account.  |

### Link Management (`/links`)

| Method | Path                       | Description                                           |
| ------ | -------------------------- | ----------------------------------------------------- |
| POST   | /links/                    | Create a new short link. (Authenticated or anonymous) |
| GET    | /links/{short_code}        | Redirect to the original URL and track the click.     |
| GET    | /links/clicks/{short_code} | (Protected) Get click statistics for a link you own.  |

## Getting Started

### Prerequisites

- Docker

### Installation

**Clone the repository:**

```bash
git clone https://github.com/AlShabiliBadia/Shorter-links.git
cd Shorter-links
```

**Configure environment variables:**
Create a .env file by copying the provided template.

```bash
cp .env.example .env
```

Now, edit the .env file. You only need to set your POSTGRES*USER, POSTGRES_PASSWORD, and POSTGRES_DB. Make sure to use the same values for both the DB*... and POSTGRES\_... variables.

**Example .env:**

```
# For the FastAPI App (app service)
DB_HOST=db
DB_PORT=5432
DB_USER=myuser
DB_PASSWORD=mypassword
DB_NAME=shorter_url
# For the Postgres Container (db service)
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=shorter_url
```

**Build and run the containers:**

```bash
docker-compose up --build
```

---

## Changelog

### [v1.4] - 2025-11-02 (Docker & Dependency Fixes)

- Added full Docker and Docker Compose support for a simple, one-command setup.
- Added a DELETE /users/delete endpoint for account deletion (primarily for test isolation).
- Fixed and updated the get_current_user dependency for better robustness.

### [v1.3] - 2025-10-26 (Code Cleanup & Fixes)

- Cleaned up the code by splitting it into separate files for 'users' and 'links' using `APIRouter`.
- Moved shared code like `get_db` and `get_current_user` into their own `dependencies.py` file.
- Fixed a bug where clicks could be missed if many people used a link at the same time. Now uses a database lock (`.with_for_update()`) to count every click.
- Made the click-stats page private — only the person who created the link can see how many clicks it has.
- Improved API safety and documentation by adding `response_model` to all data-returning endpoints.

### [v1.2] - 2025-10-15

- Implemented a complete user system allowing users to sign up and log in with JWT-based authentication.
- Short links can now be associated with a user account.

### [v1.0] - Initial Version

- Established the fundamental URL shortening and redirection service for anonymous users.
