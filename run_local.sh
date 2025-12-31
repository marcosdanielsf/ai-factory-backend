#!/bin/bash

##############################################################################
# AI Factory API - Local Development Server
# =========================================
# Run the API locally for development and testing
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI Factory API - Local Development${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}Python Version:${NC} $PYTHON_VERSION"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo -e "${YELLOW}Using .env.example as template${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env from .env.example${NC}"
        echo -e "${RED}Please edit .env with your actual credentials${NC}"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -q -r requirements.txt

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${BLUE}Loading environment variables from .env${NC}"
    export $(cat .env | grep -v '#' | xargs)
fi

# Display startup info
echo ""
echo -e "${GREEN}Starting API server...${NC}"
echo -e "${BLUE}Host:${NC} 0.0.0.0:8000"
echo -e "${BLUE}Workers:${NC} 1 (development)"
echo -e "${BLUE}Reload:${NC} Enabled"
echo ""
echo -e "${YELLOW}Available Endpoints:${NC}"
echo -e "  ${GREEN}GET${NC}  http://localhost:8000/health"
echo -e "  ${GREEN}GET${NC}  http://localhost:8000/ping"
echo -e "  ${GREEN}GET${NC}  http://localhost:8000/docs (Swagger UI)"
echo -e "  ${GREEN}GET${NC}  http://localhost:8000/redoc (ReDoc)"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Run with uvicorn in development mode
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info

deactivate
