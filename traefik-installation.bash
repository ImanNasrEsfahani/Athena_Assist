#!/bin/bash

# Function to check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        echo "Docker is already installed."
        return 0
    else
        echo "Docker is not installed."
        return 1
    fi
}

# Function to install Docker
install_docker() {
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    echo "Docker installed successfully."
}

# Function to install and configure Traefik
setup_traefik() {
    echo "Setting up Traefik..."

    # Prompt for necessary information
    read -p "Enter your domain (e.g., example.com): " DOMAIN
    read -p "Enter email for Let's Encrypt: " EMAIL
    read -p "Enter desired HTTP port (default 80): " HTTP_PORT
    HTTP_PORT=${HTTP_PORT:-80}
    read -p "Enter desired HTTPS port (default 443): " HTTPS_PORT
    HTTPS_PORT=${HTTPS_PORT:-443}
    read -p "Enter Traefik dashboard subdomain (e.g., traefik.example.com): " DASHBOARD_DOMAIN

    # Create necessary directories
    mkdir -p traefik
    cd traefik

    # Create traefik.yml
    cat > traefik.yml <<EOL
api:
  dashboard: true

entryPoints:
  web:
    address: ":${HTTP_PORT}"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":${HTTPS_PORT}"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false

certificatesResolvers:
  letsencrypt:
    acme:
      email: ${EMAIL}
      storage: acme.json
      httpChallenge:
        entryPoint: web
EOL

    # Create empty acme.json and set permissions
    touch acme.json
    chmod 600 acme.json

    # Generate admin password for Traefik dashboard
    ADMIN_PASSWORD=$(openssl passwd -apr1)
    sed -i "s/admin:${ADMIN_PASSWORD}/admin:$(echo $ADMIN_PASSWORD | sed 's/\//\\\//g')/" docker-compose.yml

    # Start Traefik
    docker-compose up -d

    echo "Traefik has been set up and is running."
    echo "Access the Traefik dashboard at: https://${DASHBOARD_DOMAIN}"
    echo "Username: admin"
    echo "Password: The password you entered"

    # Create docker-compose.yml
    cat > docker-compose.yml <<EOL
version: '3'

services:
  traefik:
    image: traefik:v2.5
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    ports:
      - ${HTTP_PORT}:80
      - ${HTTPS_PORT}:443
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/traefik.yml:ro
      - ./acme.json:/acme.json
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.entrypoints=websecure"
      - "traefik.http.routers.traefik.rule=Host(\`${DASHBOARD_DOMAIN}\`)"
      - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
      - "traefik.http.routers.traefik.service=api@internal"
      - "traefik.http.routers.traefik.middlewares=auth"
      - "traefik.http.middlewares.auth.basicauth.users=admin:${ADMIN_PASSWORD}"

networks:
  default:
    name: traefik_network
EOL

}

# Main script execution
if check_docker; then
    echo "Proceeding with Traefik setup."
else
    install_docker
fi

setup_traefik

echo "Setup complete. Please ensure your domain's DNS is properly configured to point to this server."
