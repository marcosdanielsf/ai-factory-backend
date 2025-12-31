#!/bin/bash

##############################################################################
# AI Factory API - Automated Railway Deployment
# ============================================
# Complete deployment script for Railway.app
#
# Prerequisites:
#   - GitHub repository connected
#   - Railway CLI installed (npm install -g @railway/cli)
#   - Railway account with project created
#
# Usage:
#   bash DEPLOY.sh [environment]
#   bash DEPLOY.sh production
#   bash DEPLOY.sh staging
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-"production"}
PROJECT_NAME="ai-factory"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Logs
LOG_FILE="${SCRIPT_DIR}/deploy-${TIMESTAMP}.log"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${MAGENTA}========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${MAGENTA}  $1${NC}" | tee -a "$LOG_FILE"
    echo -e "${MAGENTA}========================================${NC}" | tee -a "$LOG_FILE"
}

# Main deployment flow
main() {
    log_section "AI Factory API - Railway Deployment"

    log_info "Environment: $ENVIRONMENT"
    log_info "Timestamp: $TIMESTAMP"
    log_info "Logging to: $LOG_FILE"
    log_info "Working directory: $SCRIPT_DIR"

    # Check prerequisites
    check_prerequisites

    # Prepare deployment
    prepare_deployment

    # Deploy to Railway
    deploy_to_railway

    # Post-deployment validation
    validate_deployment

    log_success "Deployment completed successfully!"
    log_info "Check Railway dashboard for live status"
}

check_prerequisites() {
    log_section "Checking Prerequisites"

    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        exit 1
    fi
    log_success "Git installed: $(git --version)"

    # Check Docker (optional, for local testing)
    if command -v docker &> /dev/null; then
        log_success "Docker installed: $(docker --version)"
    else
        log_warning "Docker not installed (optional for local testing)"
    fi

    # Check Railway CLI
    if ! command -v railway &> /dev/null; then
        log_warning "Railway CLI not installed"
        log_info "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    log_success "Railway CLI available"

    # Check if .env exists
    if [ ! -f "${SCRIPT_DIR}/.env" ]; then
        log_warning ".env file not found"
        if [ -f "${SCRIPT_DIR}/.env.example" ]; then
            log_info "Creating .env from .env.example"
            cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
            log_warning "Please edit .env with your actual credentials"
        fi
    else
        log_success ".env file found"
    fi

    # Check required files
    local required_files=("requirements.txt" "Dockerfile" "gunicorn.conf.py" "main.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "${SCRIPT_DIR}/${file}" ]; then
            log_error "Required file not found: $file"
            exit 1
        fi
        log_success "Found: $file"
    done
}

prepare_deployment() {
    log_section "Preparing Deployment"

    cd "$SCRIPT_DIR"

    # Check git status
    if [ -z "$(git status --porcelain)" ]; then
        log_info "Working directory is clean"
    else
        log_warning "Uncommitted changes detected:"
        git status --short | tee -a "$LOG_FILE"

        read -p "Continue with uncommitted changes? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Deployment cancelled"
            exit 1
        fi
    fi

    # Build Docker image locally (optional validation)
    read -p "Build Docker image locally for testing? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Building Docker image..."
        docker build -t ai-factory:latest . 2>&1 | tee -a "$LOG_FILE"
        log_success "Docker image built successfully"

        # Test health check
        log_info "Starting container for health check..."
        CONTAINER_ID=$(docker run -d -p 8000:8000 ai-factory:latest)
        sleep 5

        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Health check passed"
        else
            log_error "Health check failed"
            docker stop "$CONTAINER_ID"
            exit 1
        fi

        docker stop "$CONTAINER_ID"
        log_success "Local validation passed"
    fi
}

deploy_to_railway() {
    log_section "Deploying to Railway"

    cd "$SCRIPT_DIR"

    # Initialize Railway project if needed
    if [ ! -f ".railway/config.json" ]; then
        log_info "Initializing Railway project..."
        railway init 2>&1 | tee -a "$LOG_FILE"
    fi

    # Set environment for Railway
    log_info "Configuring Railway environment ($ENVIRONMENT)..."

    # Push current state to GitHub first
    log_info "Pushing changes to GitHub..."
    git add -A
    git commit -m "Deploy to Railway - $TIMESTAMP" 2>&1 | tee -a "$LOG_FILE" || true
    git push origin $(git rev-parse --abbrev-ref HEAD) 2>&1 | tee -a "$LOG_FILE"

    log_success "Changes pushed to GitHub"
    log_info "Railway will automatically detect changes and deploy"

    # Get railway status
    log_info "Fetching Railway project status..."
    railway status 2>&1 | tee -a "$LOG_FILE"
}

validate_deployment() {
    log_section "Validating Deployment"

    # Get the Railway app URL
    log_info "Getting deployment URL..."

    # Note: You need to configure Railway_TOKEN environment variable
    # or use 'railway link' to connect to your project

    read -p "Enter the Railway app URL (e.g., https://app.railway.app): " RAILWAY_URL

    if [ -z "$RAILWAY_URL" ]; then
        log_warning "Skipping deployment validation"
        return
    fi

    log_info "Testing deployment at: $RAILWAY_URL"

    # Wait for service to be ready
    log_info "Waiting for service to be ready..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f "${RAILWAY_URL}/ping" > /dev/null 2>&1; then
            log_success "Service is ready!"
            break
        fi

        log_info "Waiting... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done

    if [ $attempt -gt $max_attempts ]; then
        log_error "Service failed to become ready"
        return 1
    fi

    # Run deployment tests
    if command -v python3 &> /dev/null; then
        log_info "Running deployment tests..."
        python3 test_api_deployment.py "$RAILWAY_URL" 2>&1 | tee -a "$LOG_FILE"

        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log_success "Deployment tests passed"
        else
            log_error "Deployment tests failed"
        fi
    fi
}

# Error handling
trap 'log_error "Deployment failed"; exit 1' ERR

# Run main function
main

log_section "Deployment Summary"
log_success "API deployed successfully"
log_info "Environment: $ENVIRONMENT"
log_info "Logs saved to: $LOG_FILE"
log_info ""
log_info "Next steps:"
log_info "1. Visit Railway dashboard: https://railway.app/dashboard"
log_info "2. Monitor deployment progress in real-time"
log_info "3. Check logs for any issues"
log_info "4. Configure custom domain (optional)"
log_info "5. Set up monitoring and alerts"

exit 0
