#!/bin/bash
# Automated deployment script for 75 Hard Challenge Tracker to Raspberry Pi
# Usage: ./deploy_to_pi.sh <raspberry-pi-hostname-or-ip> [--build-on-pi]

set -e  # Exit on error

# Configuration
PI_HOST="${1:-raspberrypi.local}"
APP_NAME="75hard-app"
REMOTE_DIR="/home/pi/75hard"
BUILD_ON_PI="${2}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
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

# Check if host is provided
if [ -z "$PI_HOST" ]; then
    log_error "Usage: $0 <raspberry-pi-hostname-or-ip> [--build-on-pi]"
    exit 1
fi

log_info "Deploying 75 Hard Tracker to $PI_HOST..."

# Test SSH connection
log_info "Testing SSH connection to $PI_HOST..."
if ! ssh pi@$PI_HOST "echo 'SSH connection successful'" > /dev/null 2>&1; then
    log_error "Cannot connect to pi@$PI_HOST. Please check:"
    echo "  1. SSH is enabled on your Raspberry Pi"
    echo "  2. The hostname/IP is correct"
    echo "  3. You can login with: ssh pi@$PI_HOST"
    exit 1
fi

log_info "SSH connection successful!"

# Create remote directory
log_info "Creating remote directory at $REMOTE_DIR..."
ssh pi@$PI_HOST "mkdir -p $REMOTE_DIR"

# Sync files to Raspberry Pi (excluding unnecessary files)
log_info "Syncing application files to Raspberry Pi..."
rsync -avz --exclude '__pycache__' \
           --exclude '*.pyc' \
           --exclude '.git' \
           --exclude 'instance' \
           --exclude '.env' \
           --exclude 'venv' \
           --exclude '.venv' \
           ./ pi@$PI_HOST:$REMOTE_DIR/

# Create .env file on Pi if it doesn't exist
log_info "Checking .env configuration..."
ssh pi@$PI_HOST "cd $REMOTE_DIR && if [ ! -f .env ]; then
    echo 'Creating .env file...'
    cat > .env << 'EOF'
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///instance/75hard.db
EOF
fi"

# Check if Docker is installed
log_info "Checking if Docker is installed on Raspberry Pi..."
if ! ssh pi@$PI_HOST "command -v docker" > /dev/null 2>&1; then
    log_warn "Docker not found. Installing Docker..."
    ssh pi@$PI_HOST "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo usermod -aG docker pi"
    log_info "Docker installed. You may need to reboot your Pi and run this script again."
    log_warn "Run: ssh pi@$PI_HOST 'sudo reboot'"
    exit 0
fi

# Detect Docker Compose on Pi
log_info "Detecting Docker Compose version on Raspberry Pi..."
PI_DOCKER_COMPOSE=$(ssh pi@$PI_HOST 'bash -s' << 'DETECT_SCRIPT'
if command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
    echo "docker compose"
elif command -v docker-compose &> /dev/null; then
    echo "docker-compose"
else
    echo ""
fi
DETECT_SCRIPT
)

if [ -z "$PI_DOCKER_COMPOSE" ]; then
    log_warn "Docker Compose not found. Installing..."
    ssh pi@$PI_HOST "sudo pip3 install docker-compose"
    PI_DOCKER_COMPOSE="docker-compose"
fi

log_info "Using: $PI_DOCKER_COMPOSE"

# Build or pull image
if [ "$BUILD_ON_PI" == "--build-on-pi" ]; then
    log_info "Building Docker image on Raspberry Pi (this may take 5-10 minutes)..."
    ssh pi@$PI_HOST "cd $REMOTE_DIR && $PI_DOCKER_COMPOSE build"
else
    log_info "Note: To build on Pi, use: $0 $PI_HOST --build-on-pi"
fi

# Stop existing container if running
log_info "Stopping existing container if running..."
ssh pi@$PI_HOST "cd $REMOTE_DIR && $PI_DOCKER_COMPOSE down" || true

# Start the application
log_info "Starting application with Docker Compose..."
ssh pi@$PI_HOST "cd $REMOTE_DIR && $PI_DOCKER_COMPOSE up -d"

# Wait for health check
log_info "Waiting for application to start (checking health)..."
sleep 10

# Check if container is running
if ssh pi@$PI_HOST "docker ps | grep $APP_NAME" > /dev/null; then
    log_info "✓ Deployment successful!"
    echo ""
    log_info "Application is running at: http://$PI_HOST:5000"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    ssh pi@$PI_HOST 'cd $REMOTE_DIR && $PI_DOCKER_COMPOSE logs -f'"
    echo "  Stop app:     ssh pi@$PI_HOST 'cd $REMOTE_DIR && $PI_DOCKER_COMPOSE down'"
    echo "  Restart app:  ssh pi@$PI_HOST 'cd $REMOTE_DIR && $PI_DOCKER_COMPOSE restart'"
    echo "  App status:   ssh pi@$PI_HOST 'cd $REMOTE_DIR && $PI_DOCKER_COMPOSE ps'"
else
    log_error "Container failed to start. Checking logs..."
    ssh pi@$PI_HOST "cd $REMOTE_DIR && $PI_DOCKER_COMPOSE logs"
    exit 1
fi
