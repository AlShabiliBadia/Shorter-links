# FastAPI URL Shortener (v1.2)

A URL shortening service built with Python. This project uses the FastAPI framework and communicates with a PostgreSQL database asynchronously.

It provides an API for creating and managing short links, and includes a user authentication system using JWT.

---

## Features

- URL shortening for anonymous and authenticated users.
- JWT-based user authentication (signup and login).
- Redirection from short URLs to their original target URLs.
- Click tracking for each link.

---

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL, SQLAlchemy (with Asyncio)
- **Authentication**: Passlib, python-jose
- **Data Validation**: Pydantic

---

## Getting Started

### Prerequisites

- Python 3.8+
- A running PostgreSQL database.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/AlShabiliBadia/Shorter-links.git
    cd https://github.com/AlShabiliBadia/Shorter-links.git
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

    _On Windows, use `venv\Scripts\activate`_

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file by copying the provided template. Then, edit the `.env` file with your database details and secrets.
    ```bash
    cp .env.example .env
    ```

### Running the Server

Start the application using Uvicorn.

```bash
uvicorn app.main:app --reload
```

## Changelog

### [v1.2] - 2025-10-15

- **User Authentication**: Implemented a complete user system, allowing users to sign up and log in with JWT-based authentication.
- **Link Ownership**: Short links can now be associated with a user account.

### [v1.0] - Initial Version

- **Core Functionality**: Established the fundamental URL shortening and redirection service for anonymous users.
