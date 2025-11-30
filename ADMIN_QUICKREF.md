# Admin Quick Reference

## Setup First Admin
```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"secure123"}'

# Promote to admin (using manage_admin.py)
python manage_admin.py

# Or direct database
docker exec -it library_hold_agent-app-1 sqlite3 library_holds.db
UPDATE users SET is_admin = 1 WHERE id = 1;
.quit
```

## User Management

```bash
# List all users
GET /admin/users

# Get user details
GET /admin/users/{user_id}

# Update user
PUT /admin/users/{user_id}
Body: {"library_card_number": "...", "library_pin": "..."}

# Delete user
DELETE /admin/users/{user_id}

# Promote to admin
POST /admin/users/{user_id}/promote

# Demote from admin
POST /admin/users/{user_id}/demote
```

## Library Management

```bash
# List libraries (admin - includes inactive)
GET /admin/libraries?include_inactive=true

# List libraries (public - active only)
GET /libraries

# Create library
POST /admin/libraries
Body: {
  "name": "Library Name",
  "base_url": "https://library.org",
  "search_url": "https://library.org/search",
  "login_url": "https://library.org/login",
  "description": "Description"
}

# Update library
PUT /admin/libraries/{library_id}
Body: {"description": "New description"}

# Deactivate library (soft delete)
POST /admin/libraries/{library_id}/deactivate

# Activate library
POST /admin/libraries/{library_id}/activate

# Delete library (permanent)
DELETE /admin/libraries/{library_id}
```

## Example: Complete Admin Workflow

```bash
# 1. Login as admin
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secure123"}' \
  | jq -r '.access_token')

# 2. List all users
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/users

# 3. Update a user's library card
curl -X PUT http://localhost:8000/admin/users/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"library_card_number":"123456","library_pin":"1234"}'

# 4. Create a library
curl -X POST http://localhost:8000/admin/libraries \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "San Francisco Public Library",
    "base_url": "https://sfpl.org",
    "description": "SF Public Library"
  }'

# 5. List all libraries
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/libraries
```

## Security Notes

- ⚠️ Admins cannot delete or demote themselves
- ⚠️ Admin endpoints return 403 if user is not admin
- ⚠️ All admin endpoints require JWT authentication
- ⚠️ Admin tokens should be kept secure

## Test Scripts

```bash
# Test admin functionality
python test_admin.py

# Manage admins via CLI
python manage_admin.py
```

## API Documentation

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
