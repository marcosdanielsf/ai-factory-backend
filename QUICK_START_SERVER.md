# Quick Start - Secure Server

## 1. Start the Server

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework
python server.py
```

**Output:**
```
2025-01-01 00:00:00,000 - server - INFO - Starting AI Factory Testing Server v1.0.0
2025-01-01 00:00:00,001 - server - INFO - Debug mode: False
2025-01-01 00:00:00,002 - server - INFO - CORS origins: ['http://localhost:3000', 'http://localhost:3001']
2025-01-01 00:00:00,003 - server - INFO - Rate limiting: enabled
2025-01-01 00:00:00,004 - server - INFO - Rate limit: 100 requests per 60s
2025-01-01 00:00:00,005 - server - INFO - Server started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 2. Test Without Auth (Public Endpoints)

```bash
# Health check
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00.000000",
  "version": "1.0.0"
}
```

## 3. Test With Auth (Protected Endpoints)

```bash
# Get API key from .env
export API_KEY="sk-test-key-ai-factory-2025"

# Test protected endpoint
curl -H "X-API-Key: $API_KEY" http://localhost:8000/protected
```

**Response:**
```json
{
  "message": "Access granted to protected resource",
  "api_key": "sk-test-key...",
  "timestamp": "2025-01-01T00:00:00.000000"
}
```

## 4. Test API (With Auth)

```bash
# Run a test
curl -X POST \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"test_name":"my_test","iterations":5}' \
  http://localhost:8000/api/test
```

**Response:**
```json
{
  "success": true,
  "test_id": "test_20250101_000000",
  "received_data": {
    "test_name": "my_test",
    "iterations": 5
  },
  "timestamp": "2025-01-01T00:00:00.000000"
}
```

## 5. Run All Security Tests

```bash
python -m pytest test_server_security.py -v
```

**Expected:**
```
======================== 31 passed in 0.41s =========================
```

## 6. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

To test endpoints in Swagger UI:
1. Click the lock icon in top-right
2. Enter API Key: `sk-test-key-ai-factory-2025`
3. Click endpoints to test

## Configuration

Edit `.env` to customize:

```env
# API Key
API_KEY=sk-your-secret-key

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD_SECONDS=60

# Server
DEBUG=false
```

## Features Implemented

- ✅ API Key Authentication
- ✅ CORS Configuration
- ✅ 6 Security Headers
- ✅ Rate Limiting (100 req/min per IP)
- ✅ Request Logging with Request IDs
- ✅ Security Error Handling
- ✅ Health Check Endpoints
- ✅ Protected API Endpoints

## Troubleshooting

**Error: API_KEY not set**
```bash
export API_KEY="sk-test-key-ai-factory-2025"
# or add to .env file
```

**Error: Address already in use**
```bash
# Change port in server.py or kill the process
lsof -i :8000
kill -9 <PID>
```

**CORS errors in browser**
- Add your frontend URL to CORS_ORIGINS in .env
- Example: `CORS_ORIGINS=https://myapp.com`

**Rate limit exceeded**
- Wait 60 seconds or increase RATE_LIMIT_REQUESTS in .env
- For testing: set RATE_LIMIT_ENABLED=false

## Documentation

- **Full Guide**: `SERVER_SECURITY_GUIDE.md`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`
- **Tests**: `test_server_security.py`

---

**Ready to use!** Server is production-ready with security best practices.
