# Security Features

This document outlines the security measures implemented in the Voting System.

## Security Features Implemented

### 1. Environment Variables
- Database credentials are stored in environment variables
- Secret keys are loaded from `.env` file (not committed to git)
- Use `.env.example` as a template for your `.env` file

### 2. Input Validation & Sanitization
- All user inputs are validated before processing
- Voter IDs are sanitized to prevent injection attacks
- Base64 image format validation
- Field length limits to prevent buffer overflow

### 3. Rate Limiting
- Registration: 10 attempts per minute
- Verification: 20 attempts per minute
- Voting: 5 attempts per minute
- General API: 200 requests per day, 50 per hour

### 4. CORS Configuration
- CORS is configured to only allow requests from specified origins
- Update `ALLOWED_ORIGINS` in `.env` file for your frontend URL

### 5. Admin Authentication
- Admin endpoints require HTTP Basic Authentication
- Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env` file
- Default credentials should be changed in production

### 6. Audit Logging
- All voting actions are logged with:
  - Timestamp
  - Action type
  - Voter ID
  - IP address
  - Additional details
- Logs are stored in `voting_system.log` file

### 7. SQL Injection Prevention
- All database queries use parameterized statements
- User inputs are never directly interpolated into SQL queries

### 8. Secure Database Connection
- Database credentials are not hardcoded
- Connection errors are logged securely

## Setup Instructions

### 1. Create `.env` File

Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=voting_system
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Flask Configuration
FLASK_SECRET_KEY=generate-a-random-secret-key-here
FLASK_ENV=development

# Security Configuration
ALLOWED_ORIGINS=http://localhost:3000

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-to-secure-password
```

### 2. Generate Secret Key

Generate a secure secret key:

```python
import secrets
print(secrets.token_hex(32))
```

### 3. Install Security Dependencies

```bash
pip install flask-limiter python-dotenv
```

### 4. Update Frontend for Admin Authentication

When calling admin endpoints from the frontend, include authentication:

```javascript
const response = await axios.get(`${API_BASE_URL}/admin/votes`, {
  auth: {
    username: 'admin',
    password: 'your-admin-password'
  }
});
```

## Additional Security Recommendations

### Production Deployment

1. **HTTPS**: Always use HTTPS in production
2. **Secret Key**: Use a strong, randomly generated secret key
3. **Database**: Use SSL/TLS for database connections
4. **Environment**: Set `FLASK_ENV=production`
5. **Firewall**: Restrict database access to application server only
6. **Backup**: Regular database backups
7. **Monitoring**: Set up monitoring and alerting for suspicious activity
8. **Updates**: Keep all dependencies updated

### Additional Hardening

1. **Two-Factor Authentication**: Consider adding 2FA for admin access
2. **Vote Encryption**: Encrypt votes at rest in the database
3. **Vote Anonymization**: Separate voter identity from votes
4. **Blockchain**: Consider blockchain for vote immutability
5. **Penetration Testing**: Regular security audits

## Log Files

- Application logs: `voting_system.log`
- Review logs regularly for suspicious activity
- Rotate logs to prevent disk space issues

## Security Contacts

If you discover a security vulnerability, please contact the development team immediately.

