#!/bin/bash
# Quick local testing script for Docker setup
# Usage: ./test_local.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect docker compose command (v2 vs v1)
detect_docker_compose() {
    if command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    elif command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    else
        echo ""
    fi
}

DOCKER_COMPOSE=$(detect_docker_compose)

log_info "Testing Docker setup locally..."

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    log_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if Docker Compose is available
if [ -z "$DOCKER_COMPOSE" ]; then
    log_error "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

log_info "Using: $DOCKER_COMPOSE"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    log_info "Creating .env file..."
    cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///instance/75hard.db
EOF
    log_info "✓ .env file created"
fi

# Stop any existing containers
log_info "Stopping any existing containers..."
$DOCKER_COMPOSE down 2>/dev/null || true

# Build and start
log_info "Building Docker image (this may take a minute)..."
$DOCKER_COMPOSE build

log_info "Starting container..."
$DOCKER_COMPOSE up -d

# Wait for health check
log_info "Waiting for application to start..."
sleep 5

# Check if running
if docker ps | grep 75hard-app > /dev/null; then
    log_info "✓ Container is running!"
    echo ""
    log_info "Application available at: http://localhost:5001"
    echo ""
    log_warn "Note: Using port 5001 to avoid macOS AirPlay conflict on port 5000"
    echo ""
    echo "Useful commands:"
    echo "  View logs:   $DOCKER_COMPOSE logs -f"
    echo "  Stop app:    $DOCKER_COMPOSE down"
    echo "  Restart:     $DOCKER_COMPOSE restart"
    echo "  Shell:       $DOCKER_COMPOSE exec 75hard-app /bin/bash"
    echo ""
    log_warn "Press Ctrl+C to stop viewing logs (container keeps running)"
    echo ""
    $DOCKER_COMPOSE logs -f
else
    log_error "Container failed to start. Showing logs..."
    $DOCKER_COMPOSE logs
    exit 1
fi
