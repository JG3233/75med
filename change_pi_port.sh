#!/bin/bash
# Helper script to change the port on Raspberry Pi deployment
# Usage: ./change_pi_port.sh <pi-hostname-or-ip> <new-port>

set -e

PI_HOST="${1}"
NEW_PORT="${2}"
REMOTE_DIR="/home/pi/75hard"

# Colors
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

# Check arguments
if [ -z "$PI_HOST" ] || [ -z "$NEW_PORT" ]; then
    log_error "Usage: $0 <raspberry-pi-hostname-or-ip> <new-port>"
    echo ""
    echo "Example:"
    echo "  $0 raspberrypi.local 5002"
    echo "  $0 192.168.1.100 8080"
    exit 1
fi

log_info "Changing port to $NEW_PORT on $PI_HOST..."

# Test SSH connection
log_info "Testing SSH connection..."
if ! ssh pi@$PI_HOST "echo 'SSH OK'" > /dev/null 2>&1; then
    log_error "Cannot connect to pi@$PI_HOST"
    exit 1
fi

# Detect Docker Compose on Pi
log_info "Detecting Docker Compose on Pi..."
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
    log_error "Docker Compose not found on Pi"
    exit 1
fi

log_info "Using: $PI_DOCKER_COMPOSE"

# Change the port in docker-compose.yml
log_info "Updating docker-compose.yml on Pi..."
ssh pi@$PI_HOST "cd $REMOTE_DIR && sed -i 's/- \"[0-9]*:5000\"/- \"$NEW_PORT:5000\"/' docker-compose.yml"

# Restart the container
log_info "Restarting container..."
ssh pi@$PI_HOST "cd $REMOTE_DIR && $PI_DOCKER_COMPOSE down && $PI_DOCKER_COMPOSE up -d"

# Wait for startup
log_info "Waiting for app to start..."
sleep 5

# Check if running
if ssh pi@$PI_HOST "docker ps | grep 75hard-app" > /dev/null; then
    log_info "✓ Port changed successfully!"
    echo ""
    log_info "Application is now running at: http://$PI_HOST:$NEW_PORT"
    echo ""
    log_warn "Note: You may need to update any bookmarks or shortcuts"
else
    log_error "Container failed to start. Checking logs..."
    ssh pi@$PI_HOST "cd $REMOTE_DIR && $PI_DOCKER_COMPOSE logs --tail=50"
    exit 1
fi
