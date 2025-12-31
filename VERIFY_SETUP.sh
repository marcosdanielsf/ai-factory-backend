#!/bin/bash

##############################################################################
# AI Factory - Setup Verification Script
# ===================================
# Validates all deployment configuration files
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI Factory Setup Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Counter for checks
TOTAL=0
PASSED=0
FAILED=0

# Helper function
check_file() {
    local file=$1
    local description=$2

    ((TOTAL++))

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        echo "  File: $file"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description"
        echo "  File: $file (NOT FOUND)"
        ((FAILED++))
    fi
}

check_content() {
    local file=$1
    local pattern=$2
    local description=$3

    ((TOTAL++))

    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description"
        ((FAILED++))
    fi
}

# Main checks
echo -e "${BLUE}Core Application Files${NC}"
echo "----------------------------------------"
check_file "main.py" "FastAPI application"
check_file "gunicorn.conf.py" "Gunicorn configuration"
check_file "Dockerfile" "Docker configuration"
check_file "requirements.txt" "Python dependencies"

echo ""
echo -e "${BLUE}Deployment Configuration${NC}"
echo "----------------------------------------"
check_file "railway.toml" "Railway deployment config"
check_file ".dockerignore" "Docker ignore patterns"
check_file "docker-compose.yml" "Docker compose file"

echo ""
echo -e "${BLUE}Documentation${NC}"
echo "----------------------------------------"
check_file "RAILWAY_DEPLOY.md" "Railway deployment guide"
check_file "DEPLOYMENT_SUMMARY.md" "Deployment summary"

echo ""
echo -e "${BLUE}Scripts${NC}"
echo "----------------------------------------"
check_file "run_local.sh" "Local development script"
check_file "DEPLOY.sh" "Automated deployment script"
check_file "test_api_deployment.py" "API validation tests"
check_file "performance-test.js" "Performance testing"

echo ""
echo -e "${BLUE}Configuration Validation${NC}"
echo "----------------------------------------"

# Check Dockerfile content
echo -n "Checking Dockerfile configuration... "
if grep -q "FROM python:3.11-slim" Dockerfile && \
   grep -q "gunicorn" Dockerfile && \
   grep -q "HEALTHCHECK" Dockerfile; then
    echo -e "${GREEN}OK${NC}"
    ((PASSED++))
else
    echo -e "${RED}INCOMPLETE${NC}"
    ((FAILED++))
fi
((TOTAL++))

# Check requirements.txt
echo -n "Checking Python dependencies... "
if grep -q "fastapi" requirements.txt && \
   grep -q "uvicorn" requirements.txt && \
   grep -q "gunicorn" requirements.txt; then
    echo -e "${GREEN}OK${NC}"
    ((PASSED++))
else
    echo -e "${RED}MISSING DEPENDENCIES${NC}"
    ((FAILED++))
fi
((TOTAL++))

# Check railway.toml
echo -n "Checking Railway configuration... "
if grep -q "healthcheckPath" railway.toml && \
   grep -q "memory" railway.toml; then
    echo -e "${GREEN}OK${NC}"
    ((PASSED++))
else
    echo -e "${RED}INCOMPLETE${NC}"
    ((FAILED++))
fi
((TOTAL++))

# Check main.py endpoints
echo -n "Checking API endpoints... "
if grep -q "/health" main.py && \
   grep -q "/api/v1/test/run" main.py && \
   grep -q "/api/v1/test/batch" main.py; then
    echo -e "${GREEN}OK${NC}"
    ((PASSED++))
else
    echo -e "${RED}MISSING ENDPOINTS${NC}"
    ((FAILED++))
fi
((TOTAL++))

# Check environment variables
echo ""
echo -e "${BLUE}Environment Variables${NC}"
echo "----------------------------------------"

if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"

    if grep -q "SUPABASE_URL" .env; then
        echo -e "${GREEN}  ✓${NC} SUPABASE_URL configured"
    else
        echo -e "${YELLOW}  !${NC} SUPABASE_URL not set"
    fi

    if grep -q "ANTHROPIC_API_KEY" .env; then
        echo -e "${GREEN}  ✓${NC} ANTHROPIC_API_KEY configured"
    else
        echo -e "${YELLOW}  !${NC} ANTHROPIC_API_KEY not set"
    fi
else
    echo -e "${YELLOW}!${NC} .env file not found"
    if [ -f ".env.example" ]; then
        echo "  Run: cp .env.example .env"
    fi
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Verification Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo "Total Checks: $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Setup verification PASSED${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure .env with your credentials"
    echo "2. Run locally: bash run_local.sh"
    echo "3. Deploy to Railway: bash DEPLOY.sh production"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Setup verification FAILED${NC}"
    echo "Please fix the issues above before deploying."
    exit 1
fi
