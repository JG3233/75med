#!/bin/bash

# Install Docker and Docker Compose on Raspberry Pi
# Run with: chmod +x install_docker_pi.sh && sudo ./install_docker_pi.sh

echo "Installing Docker and Docker Compose on Raspberry Pi..."

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index and install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo apt-get install -y docker-compose-plugin

# Add pi user to docker group
sudo usermod -aG docker $USER

# Enable and start Docker service
sudo systemctl enable docker
sudo systemctl start docker

echo "Docker and Docker Compose installed!"
echo "You may need to reboot or logout/login for user permissions to take effect."
echo "Then run: docker-compose up -d"
