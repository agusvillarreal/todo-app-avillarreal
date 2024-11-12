# Installation Guide

## Prerequisites

- Python 3.7+
- pip package manager
- Virtual environment (recommended)

## Step-by-Step Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/flask-todo-app
   cd flask-todo-app
   ```

2. Create virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

### api/auth.md:

```markdown
# Authentication API

## Login

Authenticate a user and receive an access token.

### Request

`POST /auth/login`

```json
{
    "username": "example_user",
    "password": "secure_password"
}

## Response 

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```