#!/bin/bash

# Define color codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# root user check
if [ "$(id -u)" -eq 0 ]; then
    print_color "$GREEN" "Script is running as root"
else
    print_color "$RED" "This script must be run as root"
    exit 1
fi

# Check system version and distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "Distribution: $NAME"
    echo "Version: $VERSION"
    echo "Codename: $VERSION_CODENAME"
else
    echo "Unable to determine system version and distribution"
    exit 1
fi

# Check if the distribution is Ubuntu and version is 20
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$NAME" = "Ubuntu" ] && [[ "$VERSION_ID" == "20."* ]]; then
        echo "Distribution is Ubuntu 20. Proceeding..."
    else
        echo "Distribution is not Ubuntu 20. Exiting..."
        exit 1
    fi
else
    echo "/etc/os-release file not found. Unable to determine distribution."
    exit 1
fi

# Function to print colored output
print_color() {
    echo -e "${1}${2}${NC}"
}

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        print_color "$GREEN" "Success: $1"
    else
        print_color "$RED" "Error: $1 failed"
        exit 1
    fi
}

# Check system compatibility
print_color "$YELLOW" "Checking system compatibility..."
if [ "$(uname -m)" != "x86_64" ]; then
    print_color "$YELLOW" "Warning: Docker requires a 64-bit OS. Your system may not be compatible."
fi

# Remove old versions of Docker
print_color "$YELLOW" "Removing old Docker versions if present..."
sudo apt-get remove -y docker docker.io containerd runc docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || true
check_success "Removal of old Docker versions"

# Update package list
print_color "$YELLOW" "Updating package list..."
sudo apt-get update
check_success "Package list update"

# Install prerequisites
print_color "$YELLOW" "Installing prerequisites..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
check_success "Installation of prerequisites"

# Add Docker's official GPG key
print_color "$YELLOW" "Adding Docker's GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
check_success "Addition of Docker's GPG key"

# Add Docker repository
print_color "$YELLOW" "Adding Docker repository..."
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
check_success "Addition of Docker repository"

# Update package list again
print_color "$YELLOW" "Updating package list..."
sudo apt-get update
check_success "Package list update"

# Install Docker
print_color "$YELLOW" "Installing Docker..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
check_success "Docker installation"

# Start and enable Docker service
print_color "$YELLOW" "Starting and enabling Docker service..."
sudo systemctl start docker
sudo systemctl enable docker
check_success "Docker service start and enable"

# Install Docker Compose
print_color "$YELLOW" "Installing Docker Compose..."
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
check_success "Docker Compose installation"

# Add current user to docker group
print_color "$YELLOW" "Adding current user to docker group..."
sudo usermod -aG docker $USER
check_success "User addition to docker group"

# Verify Docker installation
print_color "$YELLOW" "Verifying Docker installation..."
if sudo docker run hello-world; then
    print_color "$GREEN" "Docker installation verified successfully!"
else
    print_color "$RED" "Docker installation could not be verified. Please check for errors."
    exit 1
fi

# Create a default bridge network
print_color "$YELLOW" "Creating a default bridge network..."
sudo docker network create --driver bridge my_network
check_success "Creation of default bridge network"

# Configure firewall
print_color "$YELLOW" "Configuring firewall..."
sudo ufw allow 2375/tcp
sudo ufw allow 2376/tcp
check_success "Firewall configuration"

# Prompt for Docker Hub login
print_color "$YELLOW" "Do you want to log in to Docker Hub? (y/n)"
read -r docker_hub_login
if [[ $docker_hub_login =~ ^[Yy]$ ]]; then
    docker login
    check_success "Docker Hub login"
fi

# Print versions
print_color "$GREEN" "Installation complete! Versions:"
docker --version
docker-compose --version

print_color "$YELLOW" "Please log out and log back in for group changes to take effect."
print_color "$YELLOW" "To use Docker as a non-root user, remember to log out and back in."
