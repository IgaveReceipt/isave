#!/bin/bash

# Pre-Deployment Check Script for Igave
# This script runs all necessary checks before deployment

set -e

echo "🔍 Starting Pre-Deployment Checks..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
    FAILURES=$((FAILURES + 1))
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  BACKEND CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd backend

# Check if virtual environment exists
if [ -d "venv" ]; then
    success "Virtual environment found"
    source venv/bin/activate
else
    error "Virtual environment not found"
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Install dependencies
echo ""
echo "📦 Installing backend dependencies..."
pip install -q -r requirements.txt
success "Dependencies installed"

# Run linting
echo ""
echo "🔍 Running flake8 linting..."
if flake8; then
    success "Linting passed"
else
    error "Linting failed"
fi

# Check migrations
echo ""
echo "🗄️  Checking migrations..."
if python manage.py makemigrations --check --dry-run; then
    success "No missing migrations"
else
    warning "Migrations need to be created"
fi

# Run tests
echo ""
echo "🧪 Running backend tests..."
if pytest -v --tb=short; then
    success "All backend tests passed"
else
    error "Backend tests failed"
fi

# Collect static files
echo ""
echo "📁 Collecting static files..."
if python manage.py collectstatic --noinput > /dev/null 2>&1; then
    success "Static files collected"
else
    error "Static files collection failed"
fi

cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  FRONTEND CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd frontend/igave_receipts

# Check Node version
NODE_VERSION=$(node --version)
echo "Node version: $NODE_VERSION"

# Install dependencies
echo ""
echo "📦 Installing frontend dependencies..."
npm ci
success "Dependencies installed"

# Security audit
echo ""
echo "🔒 Running security audit..."
if npm audit --audit-level=high; then
    success "No high-severity vulnerabilities"
else
    warning "Security vulnerabilities found - review npm audit output"
fi

# Build frontend
echo ""
echo "🏗️  Building frontend..."
if npm run build; then
    success "Frontend build successful"
else
    error "Frontend build failed"
fi

cd ../..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DEPLOYMENT READINESS SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}"
    echo "  ✓ All checks passed!"
    echo "  ✓ Ready for deployment"
    echo -e "${NC}"
    exit 0
else
    echo -e "${RED}"
    echo "  ✗ $FAILURES check(s) failed"
    echo "  ✗ Fix issues before deploying"
    echo -e "${NC}"
    exit 1
fi
