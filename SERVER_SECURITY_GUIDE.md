# AI Factory Server - Security Guide

Complete documentation for the secure FastAPI server with authentication, CORS, and rate limiting.

## Quick Start

### 1. Setup Environment Variables

Add to `.env`:

```env
# API Security
API_KEY=sk-test-key-ai-factory-2025

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD_SECONDS=60

# Server
DEBUG=false
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn python-dotenv pydantic pydantic-settings
```

### 3. Start Server

```bash
python server.py
```

Server runs on `http://localhost:8000`

---

## Security Features

### 1. API Key Authentication

All protected endpoints require an API key via the `X-API-Key` header.

**Implementation:**
- API keys stored in `.env` and loaded at startup
- Support for multiple API keys
- Validation on every protected request
- Returns 403 Forbidden for invalid/missing keys

**Usage:**

```bash
# Valid request
curl -H "X-API-Key: sk-test-key-ai-factory-2025" \
  http://localhost:8000/protected

# Invalid request
curl http://localhost:8000/protected
# Returns: 403 Forbidden
```

**In Code:**

```python
from fastapi import Security
from fastapi.security import APIKeyHeader

# Protected endpoint
@app.get("/protected", dependencies=[Depends(verify_api_key)])
async def protected_route(api_key: str = Security(api_key_header)):
    return {"message": "Access granted"}
```

---

### 2. CORS (Cross-Origin Resource Sharing)

Middleware configured to allow requests from specified origins only.

**Configuration in `.env`:**

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8000
```

**Features:**
- Configurable allowed origins
- Allow credentials support
- Allow all HTTP methods
- Allow all headers
- 10-minute cache

**Production Setup:**

```env
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

**Headers Added:**

```
Access-Control-Allow-Origin: <allowed-origin>
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

---

### 3. Security Headers

All responses include security headers to protect against common attacks.

**Headers Implemented:**

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Enable browser XSS filter |
| `Strict-Transport-Security` | `max-age=31536000` | Enforce HTTPS |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer info |
| `Permissions-Policy` | Disable geolocation, microphone, camera | Restrict browser permissions |

---

### 4. Rate Limiting

Prevent abuse by limiting requests per IP address.

**Configuration:**

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD_SECONDS=60
```

**Example:** 100 requests per 60 seconds per IP

**How It Works:**
1. Tracks request timestamps per client IP
2. Cleans up old requests outside time window
3. Returns 429 (Too Many Requests) when limit exceeded

**Error Response:**

```json
{
  "detail": "Rate limit exceeded. Max 100 requests per 60s",
  "timestamp": "2025-01-01T12:00:00"
}
```

**Disabling (Development):**

```env
RATE_LIMIT_ENABLED=false
```

---

### 5. Trusted Hosts

Validate Host header to prevent Host Header Injection attacks.

**Configuration:**

```python
TRUSTED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

---

## API Endpoints

### Public Endpoints (No Auth Required)

#### GET `/health`

Simple health check without authentication.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00.000000",
  "version": "1.0.0"
}
```

---

### Protected Endpoints (Auth Required)

All require header: `X-API-Key: <your-key>`

#### GET `/health/detailed`

Detailed health status with configuration info.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00.000000",
  "version": "1.0.0",
  "environment": "production",
  "rate_limiting": "enabled",
  "cors_origins": ["http://localhost:3000"]
}
```

#### GET `/protected`

Example protected endpoint.

**Response:**
```json
{
  "message": "Access granted to protected resource",
  "api_key": "sk-test-key...",
  "timestamp": "2025-01-01T12:00:00.000000"
}
```

#### POST `/api/test`

Run a test with data.

**Request:**
```json
{
  "test_name": "sample_test",
  "iterations": 10,
  "timeout": 30
}
```

**Response:**
```json
{
  "success": true,
  "test_id": "test_20250101_120000",
  "received_data": {
    "test_name": "sample_test",
    "iterations": 10,
    "timeout": 30
  },
  "timestamp": "2025-01-01T12:00:00.000000"
}
```

#### GET `/api/status`

Get API status and configuration.

**Response:**
```json
{
  "api_status": "running",
  "authentication": "enabled",
  "rate_limiting": {
    "enabled": true,
    "limit": "100 requests per 60s"
  },
  "cors": {
    "allowed_origins": ["http://localhost:3000"]
  },
  "timestamp": "2025-01-01T12:00:00.000000"
}
```

---

## Usage Examples

### Python (requests)

```python
import requests

API_KEY = "sk-test-key-ai-factory-2025"
BASE_URL = "http://localhost:8000"

headers = {"X-API-Key": API_KEY}

# Protected route
response = requests.get(f"{BASE_URL}/protected", headers=headers)
print(response.json())

# Run test
test_data = {"test_name": "my_test", "iterations": 5}
response = requests.post(f"{BASE_URL}/api/test", json=test_data, headers=headers)
print(response.json())

# Get status
response = requests.get(f"{BASE_URL}/api/status", headers=headers)
print(response.json())
```

### JavaScript/Fetch

```javascript
const API_KEY = "sk-test-key-ai-factory-2025";
const BASE_URL = "http://localhost:8000";

const headers = {
  "X-API-Key": API_KEY,
  "Content-Type": "application/json"
};

// Protected route
fetch(`${BASE_URL}/protected`, { headers })
  .then(res => res.json())
  .then(data => console.log(data));

// Run test
const testData = { test_name: "my_test", iterations: 5 };
fetch(`${BASE_URL}/api/test`, {
  method: "POST",
  headers,
  body: JSON.stringify(testData)
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### cURL

```bash
API_KEY="sk-test-key-ai-factory-2025"

# Health check (no auth)
curl http://localhost:8000/health

# Protected endpoint
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/protected

# Run test
curl -X POST \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"test_name":"my_test","iterations":5}' \
  http://localhost:8000/api/test

# Get status
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/status
```

---

## Testing

### Run Security Tests

```bash
python -m pytest test_server_security.py -v
```

### Test Coverage

The `test_server_security.py` includes:

1. **Health Checks** (2 tests)
   - Public access without auth
   - Response format validation

2. **Authentication** (5 tests)
   - Valid API key acceptance
   - Invalid key rejection
   - Missing key handling
   - Header case sensitivity
   - Detailed health auth requirements

3. **CORS** (3 tests)
   - CORS headers present
   - Allow-origin handling
   - Method configuration

4. **Security Headers** (7 tests)
   - X-Content-Type-Options
   - X-Frame-Options
   - X-XSS-Protection
   - Strict-Transport-Security
   - Referrer-Policy
   - Permissions-Policy
   - All headers present

5. **Rate Limiting** (3 tests)
   - Per-IP tracking
   - Health check exemption
   - Cleanup of old requests

6. **API Endpoints** (3 tests)
   - /api/test success
   - Auth requirement
   - /api/status functionality

7. **Error Handling** (3 tests)
   - 404 errors
   - Error response format
   - Invalid JSON handling

8. **Request Headers** (2 tests)
   - X-Request-ID header
   - X-Process-Time header

9. **Settings** (3 tests)
   - Environment loading
   - CORS configuration
   - Rate limit settings

---

## Production Deployment

### Environment Variables

```env
# Production API Key - Use a strong, random key
API_KEY=sk-prod-$(openssl rand -hex 32)

# Production CORS Origins
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Disable debug mode
DEBUG=false

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD_SECONDS=60
```

### Docker Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY server.py .
COPY .env .

EXPOSE 8000

CMD ["python", "server.py"]
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      API_KEY: ${API_KEY}
      CORS_ORIGINS: ${CORS_ORIGINS}
      DEBUG: 'false'
    restart: always
```

### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Logging

### Log Levels

- **INFO:** Normal operations, startups, shutdowns
- **WARNING:** Invalid API keys, rate limit exceeded
- **ERROR:** Unhandled exceptions

### Log Format

```
2025-01-01 12:00:00,000 - server - INFO - Starting AI Factory Testing Server v1.0.0
2025-01-01 12:00:00,500 - server - INFO - [uuid] GET /health
2025-01-01 12:00:00,510 - server - INFO - [uuid] 200 - 0.010s
2025-01-01 12:00:05,000 - server - WARNING - Invalid API key attempt: sk-invalid-...
```

---

## Troubleshooting

### Issue: "Invalid API Key" on valid key

**Solution:** Ensure:
1. API_KEY is set in `.env`
2. Header name is exactly `X-API-Key` (case-sensitive)
3. No extra spaces in the key

### Issue: CORS errors in browser

**Solution:**
1. Check CORS_ORIGINS includes your frontend URL
2. For development: `http://localhost:3000`
3. For production: `https://yourdomain.com`

### Issue: Rate limit exceeded

**Solution:**
1. Increase RATE_LIMIT_REQUESTS
2. Increase RATE_LIMIT_PERIOD_SECONDS
3. Or disable: `RATE_LIMIT_ENABLED=false` (dev only)

### Issue: Server won't start

**Solution:**
1. Check API_KEY is set: `echo $API_KEY`
2. Check FastAPI installation: `pip install fastapi`
3. Check port not in use: `lsof -i :8000`

---

## API Documentation

Once server is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

> Note: You can test protected endpoints directly in Swagger UI using the lock icon in the top-right.

---

## Security Best Practices

1. **API Keys**
   - Use strong, random keys in production
   - Rotate keys periodically
   - Never commit keys to git
   - Use `.env` or environment variables

2. **CORS**
   - Be specific with allowed origins
   - Avoid `"*"` in production
   - Disable credentials if not needed

3. **Rate Limiting**
   - Adjust limits based on expected traffic
   - Monitor for abuse patterns
   - Consider IP-based blocking

4. **HTTPS**
   - Use HTTPS in production
   - Get SSL certificate (Let's Encrypt)
   - Set `Strict-Transport-Security` header

5. **Monitoring**
   - Log all requests
   - Alert on repeated 403 errors
   - Monitor 429 rate limit responses
   - Track response times

6. **Updates**
   - Keep dependencies updated
   - Monitor security advisories
   - Test updates in staging first

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-01 | Initial release with API key auth, CORS, security headers, rate limiting |

---

## Support

For issues or questions:

1. Check this guide
2. Review test file: `test_server_security.py`
3. Check server logs: `python server.py`
4. Check environment variables: `.env`

---

*Last updated: January 2025*
