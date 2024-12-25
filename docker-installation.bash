#!/bin/bash

# Define color codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    echo -e "${1}${2}${NC}"
}

# Update package list
print_color "$YELLOW" "Updating package list..."
sudo apt-get update

# Install prerequisites
print_color "$YELLOW" "Installing prerequisites..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
print_color "$YELLOW" "Adding Docker's GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add Docker repository
print_color "$YELLOW" "Adding Docker repository..."
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package list again
print_color "$YELLOW" "Updating package list..."
sudo apt-get update

# Install Docker
print_color "$YELLOW" "Installing Docker..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Start and enable Docker service
print_color "$YELLOW" "Starting and enabling Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
print_color "$YELLOW" "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
print_color "$YELLOW" "Adding current user to docker group..."
sudo usermod -aG docker $USER

# Print versions
print_color "$GREEN" "Installation complete! Versions:"
docker --version
docker-compose --version

print_color "$YELLOW" "Please log out and log back in for group changes to take effect."
