# Admin User Guide

This guide covers the admin functionality for managing users and libraries in the Library Hold Tracker system.

## Overview

Admin users have special privileges to:
- View and manage all user accounts
- Promote/demote users to/from admin role
- Create, update, and manage library information
- View sensitive user information (library card numbers, PINs)

## Setup: Creating Your First Admin

When you first deploy the system, you need to manually promote a user to admin.

### Method 1: Using the manage_admin.py script

1. Register a user through the API first:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@library.com","password":"admin123"}'
```

2. Run the admin management script:
```bash
python manage_admin.py
```

3. Follow the prompts to promote your user to admin.

### Method 2: Direct database access

```bash
# Access the database
docker exec -it library_hold_agent-app-1 sqlite3 library_holds.db

# Find your user ID
SELECT id, username FROM users;

# Promote user to admin (replace 1 with your user ID)
UPDATE users SET is_admin = 1 WHERE id = 1;

# Verify
SELECT id, username, is_admin FROM users;

# Exit
.quit
```

## User Management Endpoints

All admin endpoints require authentication with an admin user's JWT token.

### Get All Users
```bash
GET /admin/users?skip=0&limit=100

# Example:
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  http://localhost:8000/admin/users
```

**Response:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@library.com",
    "is_admin": true,
    "library_card_number": "21901028207102",
    "library_pin": "013175",
    "library_name": "Contra Costa",
    "created_at": "2025-11-30T10:00:00"
  },
  ...
]
```

### Get Specific User
```bash
GET /admin/users/{user_id}

# Example:
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  http://localhost:8000/admin/users/2
```

### Update User Information
```bash
PUT /admin/users/{user_id}

# Example: Update user's library card
curl -X PUT http://localhost:8000/admin/users/2 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "library_card_number": "21901028207102",
    "library_pin": "013175",
    "library_name": "Contra Costa"
  }'

# Example: Change username
curl -X PUT http://localhost:8000/admin/users/2 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "newusername"}'
```

**Updatable fields:**
- `username`
- `email`
- `is_admin`
- `library_card_number`
- `library_pin`
- `library_name`

### Delete User
```bash
DELETE /admin/users/{user_id}

# Example:
curl -X DELETE http://localhost:8000/admin/users/2 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Note:** Admins cannot delete their own account.

### Promote User to Admin
```bash
POST /admin/users/{user_id}/promote

# Example:
curl -X POST http://localhost:8000/admin/users/2/promote \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Demote User from Admin
```bash
POST /admin/users/{user_id}/demote

# Example:
curl -X POST http://localhost:8000/admin/users/2/demote \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Note:** Admins cannot demote themselves.

## Library Management Endpoints

### Get All Libraries (Admin)
```bash
GET /admin/libraries?include_inactive=false

# Example:
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  "http://localhost:8000/admin/libraries?include_inactive=true"
```

### Get Active Libraries (Public)
```bash
GET /libraries

# Example (no auth required):
curl http://localhost:8000/libraries
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Contra Costa County Library",
    "base_url": "https://ccclib.org",
    "search_url": "https://ccclib.bibliocommons.com/v2/search",
    "login_url": "https://ccclib.bibliocommons.com/user/login",
    "description": "Contra Costa County Library System",
    "is_active": true,
    "created_at": "2025-11-30T10:00:00",
    "updated_at": "2025-11-30T10:00:00"
  }
]
```

### Create Library
```bash
POST /admin/libraries

# Example:
curl -X POST http://localhost:8000/admin/libraries \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "San Francisco Public Library",
    "base_url": "https://sfpl.org",
    "search_url": "https://sfpl.bibliocommons.com/v2/search",
    "login_url": "https://sfpl.bibliocommons.com/user/login",
    "description": "San Francisco Public Library System"
  }'
```

**Required fields:**
- `name` (unique)
- `base_url`

**Optional fields:**
- `search_url`
- `login_url`
- `description`

### Update Library
```bash
PUT /admin/libraries/{library_id}

# Example:
curl -X PUT http://localhost:8000/admin/libraries/1 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "is_active": true
  }'
```

### Delete Library
```bash
DELETE /admin/libraries/{library_id}

# Example:
curl -X DELETE http://localhost:8000/admin/libraries/1 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Note:** This permanently removes the library from the database.

### Deactivate Library
```bash
POST /admin/libraries/{library_id}/deactivate

# Example:
curl -X POST http://localhost:8000/admin/libraries/1/deactivate \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Note:** Deactivating is preferred over deleting. Deactivated libraries are hidden from public endpoints but preserved in the database.

### Activate Library
```bash
POST /admin/libraries/{library_id}/activate

# Example:
curl -X POST http://localhost:8000/admin/libraries/1/activate \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Testing Admin Functionality

Use the provided test script:

```bash
python test_admin.py
```

This script will:
1. Create/login as admin user
2. Create a regular user
3. List all users
4. Update user information
5. Create a library
6. List libraries
7. Update library information
8. Deactivate/activate library
9. Promote user to admin

## Security Considerations

1. **Admin Token Security:** Admin tokens should be kept secure and never exposed in client-side code or public repositories.

2. **First Admin:** The first admin user must be manually promoted through database access or the manage_admin.py script.

3. **Admin Actions:** Admin actions are logged in the application and should be audited regularly.

4. **Self-Protection:** Admins cannot delete or demote themselves to prevent accidental lockout.

5. **Sensitive Data:** Admin endpoints expose sensitive user data (library card numbers, PINs). Consider:
   - Encrypting library_pin in the database
   - Adding audit logging for admin actions
   - Implementing IP whitelisting for admin endpoints
   - Adding rate limiting

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_admin BOOLEAN DEFAULT 0 NOT NULL,
    library_card_number VARCHAR,
    library_pin VARCHAR,
    library_name VARCHAR DEFAULT 'Contra Costa',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Libraries Table
```sql
CREATE TABLE libraries (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    base_url VARCHAR NOT NULL,
    search_url VARCHAR,
    login_url VARCHAR,
    description VARCHAR,
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Documentation

Access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

All admin endpoints are documented with request/response schemas and can be tested directly from the Swagger UI.
