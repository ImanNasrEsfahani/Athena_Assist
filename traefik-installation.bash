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
    sudo apt-get update || { echo "Failed to update package list"; exit 1; }

    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common || { echo "Failed to install prerequisites"; exit 1; }
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - || { echo "Failed to add Docker GPG key"; exit 1; }
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"  || { echo "Failed to add Docker repository"; exit 1; }
    sudo apt-get update || { echo "Failed to update package list"; exit 1; }
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io || { echo "Failed to install Docker"; exit 1; }
    sudo systemctl enable docker || { echo "Failed to enable Docker service"; exit 1; }
    sudo systemctl start docker || { echo "Failed to start Docker service"; exit 1; }
    sudo usermod -aG docker $USER || { echo "Failed to add user to Docker group"; exit 1; }
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

    # Generate admin password for Traefik dashboard
    echo "Please enter a password for the Traefik dashboard:"
    ADMIN_PASSWORD=$(openssl passwd -apr1) || { echo "Failed to generate password hash"; exit 1; }
    ESCAPED_PASSWORD=$(echo "$ADMIN_PASSWORD" | sed 's/\$/\$\$/g') || { echo "Failed to escape password"; exit 1; }

    # Create necessary directories
    mkdir -p traefik || { echo "Failed to create traefik directory"; exit 1; }
    cd traefik || { echo "Failed to change to traefik directory"; exit 1; }

    # Create traefik.yml
    cat > traefik.yml <<EOL || { echo "Failed to create traefik.yml"; exit 1; }
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
    touch acme.json || { echo "Failed to create acme.json"; exit 1; }
    chmod 600 acme.json || { echo "Failed to set permissions on acme.json"; exit 1; }

    # Create docker-compose.yml
    cat > docker-compose.yml <<EOL || { echo "Failed to create docker-compose.yml"; exit 1; }
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
      - "traefik.http.middlewares.auth.basicauth.users=admin:$ESCAPED_PASSWORD"

networks:
  default:
    name: traefik_network
EOL

    docker network create traefik-network || { echo "Creating traefik network has problem"; exit 1; }
    echo "Traefik network has been created"

    # Start Traefik
    # docker-compose up -d || { echo "Failed to start Traefik"; exit 1; }

    echo "Traefik has been set up and is waiting to run with FastAPI."
    echo "Access the Traefik dashboard at after run with FastAPI: https://${DASHBOARD_DOMAIN}"
    echo "Username: admin"
    echo "Password: The password you entered"
}

# Main script execution
if check_docker; then
    echo "Proceeding with Traefik setup."
else
    install_docker
fi

setup_traefik

echo "Setup complete. Please ensure your domain's DNS is properly configured to point to this server."
