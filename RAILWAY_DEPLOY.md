# AI Factory API - Railway Deployment Guide

## Overview

This document provides step-by-step instructions to deploy the AI Factory Testing Framework backend to Railway with performance optimization.

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Repository**: Push your code to GitHub
3. **Environment Variables**: Prepare the required secrets

## Quick Start

### Step 1: Connect GitHub Repository

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Authorize Railway to access your GitHub account
5. Select the repository containing this code
6. Select the branch (usually `main`)

### Step 2: Configure Environment Variables

In the Railway dashboard, navigate to your project and add these environment variables:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-...

# Database (Optional, if using PostgreSQL directly)
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Gunicorn Configuration (Optional)
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
GUNICORN_WORKER_CLASS=uvicorn.workers.UvicornWorker

# Logging
LOG_LEVEL=INFO
```

### Step 3: Deploy

Railway automatically detects the `Dockerfile` and deploys your application. The deployment process:

1. Builds the Docker image using the multi-stage Dockerfile
2. Installs dependencies from wheels (optimized for speed)
3. Runs health checks to verify the deployment
4. Exposes the API on a Railway-assigned domain

### Step 4: Verify Deployment

Once deployment is complete:

1. Get the generated URL from the Railway dashboard
2. Test the health check endpoint:

```bash
curl https://your-railway-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-31T10:00:00",
  "version": "1.0.0",
  "database": "connected"
}
```

## Performance Optimization

### Gunicorn Configuration

The `gunicorn.conf.py` is pre-configured with:

- **Workers**: Automatically set to `cpu_count * 2 - 1` (optimal for I/O-bound tasks)
- **Worker Class**: Uvicorn workers for async support
- **Timeout**: 120 seconds for long-running operations
- **Connection Pooling**: 1000 max connections
- **Graceful Shutdown**: 30 seconds timeout

### Memory & CPU Allocation

Current configuration in `railway.toml`:
- **Memory**: 512MB (adjustable)
- **CPU**: 1 core (adjustable)

To increase resources, modify `railway.toml` or update via Railway dashboard.

### Caching Strategy

The API includes:
- **GZIP Compression**: Automatic response compression
- **Connection Pooling**: Reuses database connections
- **Background Tasks**: Long operations run asynchronously
- **Health Checks**: Configured at `/health` endpoint

## API Endpoints

### Health Check
```
GET /health
GET /ping
```

### Testing
```
POST /api/v1/test/run          # Run single test
POST /api/v1/test/batch        # Run batch tests
GET  /api/v1/test/status/{id}  # Check batch status
```

### Agents
```
GET /api/v1/agents/{id}/results  # Get agent results
```

### Metrics
```
GET /api/v1/metrics  # System metrics
```

## Monitoring & Logs

### View Logs in Railway

1. Go to your project dashboard
2. Click on the service
3. Select "Logs" tab
4. Filter by log level or search terms

### Key Metrics to Monitor

- **Response Time**: Track `/health` endpoint
- **Error Rate**: Monitor 5xx responses
- **Database Connections**: Check Supabase connection pool
- **Memory Usage**: Watch for memory leaks

### Set Up Alerts

In Railway dashboard:
1. Go to Settings → Notifications
2. Configure alerts for:
   - Deployment failures
   - High memory usage (>80%)
   - High error rate (>1%)
   - Service down

## Troubleshooting

### Service Won't Start

Check logs for:
```
- "Failed to initialize clients"
- "Connection refused" (Supabase)
- "Missing environment variables"
```

**Solution**: Verify all environment variables are set correctly.

### High Memory Usage

Check for:
```
- Open database connections
- Large background tasks
- Memory leaks in dependencies
```

**Solution**: Increase memory in `railway.toml` or optimize code.

### Timeout Errors

Check for:
```
- Long-running tests (>120s)
- Database queries without indexes
- Network issues with Supabase
```

**Solution**: Increase `GUNICORN_TIMEOUT` or optimize queries.

### Database Connection Errors

```
- Too many connections
- Invalid credentials
- Service role key missing
```

**Solution**: Check `SUPABASE_SERVICE_ROLE_KEY` and connection limits.

## Performance Benchmarks

### Target Metrics

- **Health Check**: <50ms response time
- **Single Test**: 5-30s depending on agent complexity
- **Batch Tests**: Queued response <100ms
- **99th Percentile**: <10s for most endpoints

### Load Testing

Use k6 or Locust to test:

```bash
# k6 example
k6 run performance-test.js --vus 50 --duration 5m
```

## Scaling

### Horizontal Scaling

Railway automatically handles horizontal scaling:
1. Increase CPU/Memory allocation
2. Railway distributes load across instances
3. Monitor metrics to adjust

### Vertical Scaling

To allocate more resources:
1. Railway Dashboard → Service → Settings
2. Adjust "Memory" and "CPU" sliders
3. Redeploy (zero-downtime)

## Cost Optimization

Current configuration uses:
- 512MB RAM
- 1 CPU core
- 4 Gunicorn workers
- Expected cost: ~$5-10/month for moderate usage

To reduce costs:
- Reduce workers: `GUNICORN_WORKERS=2`
- Reduce memory: `memory = "256MB"` in railway.toml
- Use connection pooling in Supabase

## Cleanup & Rollback

### Roll Back Deployment

1. Railway Dashboard → Deployments
2. Click on previous successful deployment
3. Select "Redeploy"

### Remove Service

1. Railway Dashboard → Service
2. Select "Settings" → "Danger Zone"
3. Click "Delete Service"

## Next Steps

1. Set up continuous deployment by connecting GitHub
2. Configure automatic deployments on push to `main`
3. Monitor metrics and set up alerting
4. Load test before production traffic

## Support

For issues:
1. Check Railway documentation: https://docs.railway.app
2. View logs in Railway dashboard
3. Test locally with Docker: `docker build -t ai-factory . && docker run -p 8000:8000 ai-factory`

## References

- [Railway Docs](https://docs.railway.app)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/concepts/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [Uvicorn Workers](https://www.uvicorn.org/#running-with-gunicorn)
