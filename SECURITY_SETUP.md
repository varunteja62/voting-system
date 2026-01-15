# Security Setup Instructions

## Quick Setup

### 1. Install Security Dependencies

```bash
cd backend
pip install flask-limiter python-dotenv
```

Or add to requirements.txt and run:
```bash
pip install -r requirements.txt
```

### 2. Create `.env` File

Create a `.env` file in the `backend` directory with the following content:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=voting_system
DB_USER=postgres
DB_PASSWORD=varun8115

# Flask Configuration
FLASK_SECRET_KEY=change-this-to-a-random-secret-key
FLASK_ENV=development

# Security Configuration
ALLOWED_ORIGINS=http://localhost:3000

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-secure-password
```

### 3. Generate Secret Key

Generate a secure secret key:

```python
import secrets
print(secrets.token_hex(32))
```

Replace `FLASK_SECRET_KEY` in `.env` with the generated key.

### 4. Update `.gitignore`

Make sure `.env` is in your `.gitignore` file:

```
.env
*.log
```

### 5. Restart Backend

Restart your Flask backend server to apply the security changes.

## Security Features Added

1. **Environment Variables** - Sensitive data moved to `.env` file
2. **Rate Limiting** - Prevents abuse with limits on all endpoints
3. **Input Validation** - All inputs are validated and sanitized
4. **Admin Authentication** - Admin endpoints require HTTP Basic Auth
5. **Audit Logging** - All voting actions are logged
6. **CORS Security** - Only allowed origins can access the API
7. **SQL Injection Prevention** - Already using parameterized queries

## Frontend Updates Needed

Update your frontend to include admin authentication when calling admin endpoints:

```javascript
// In your admin component
const response = await axios.get(`${API_BASE_URL}/admin/votes`, {
  auth: {
    username: 'admin',  // Use from environment variable
    password: 'your-admin-password'  // Use from environment variable
  }
});
```

## Testing Security

1. Try exceeding rate limits - should get 429 error
2. Try SQL injection in voter_id - should be sanitized
3. Try accessing admin endpoints without auth - should get 401
4. Check `voting_system.log` for audit logs

