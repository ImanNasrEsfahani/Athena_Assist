#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NOCOLOR='\033[0m'

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies
install_dependencies() {
    echo -e "${BLUE}Installing dependencies...${NOCOLOR}"
    sudo apt update && sudo apt install -y curl jq netstat
}

install_ngrok() {
    echo -e "${BLUE}Downloading and installing Ngrok...${NOCOLOR}"
    NGROK_VERSION="3.3.1"  # Specify the version you want
    NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v${NGROK_VERSION}-linux-amd64.tgz"

    wget $NGROK_URL -O ngrok.tgz
    sudo tar xvzf ngrok.tgz -C /usr/local/bin
    rm ngrok.tgz

    echo -e "${GREEN}Ngrok version ${NGROK_VERSION} installed.${NOCOLOR}"
}

# Function to set up Ngrok configuration
setup_ngrok() {
    local auth_token=""

    # Try to read authtoken from ~/.ngrok2/ngrok.yml
    if [ -f ~/.ngrok2/ngrok.yml ]; then
        auth_token=$(grep "authtoken:" ~/.ngrok2/ngrok.yml | awk '{print $2}')
    fi

    # Try to read authtoken from ngrok.yml in this path
    if [ -f ./ngrok.yml ]; then
        auth_token=$(grep "authtoken:" ./ngrok.yml | awk '{print $2}')
    fi

    # If authtoken not found in file, prompt user
    if [ -z "$auth_token" ]; then
        echo -e "${YELLOW}Please enter your Ngrok authtoken:${NOCOLOR}"
        read -s auth_token
    fi

    # Set the authtoken
    ngrok config add-authtoken $auth_token

    # Verify if authtoken was set successfully
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to set authtoken. Please try again.${NOCOLOR}"
        setup_ngrok
    else
        echo -e "${GREEN}Authtoken set successfully.${NOCOLOR}"
    fi

    # Create ngrok configuration file with version
    mkdir -p /root/.ngrok2
    cat > /root/.ngrok2/ngrok.yml <<EOL
version: "2"
authtoken: $auth_token
EOL
}

# Function to create ngrok systemd service
create_ngrok_service() {
    echo -e "${BLUE}Creating ngrok systemd service...${NOCOLOR}"

    # Detect ngrok binary location
    NGROK_BIN=$(which ngrok)

    if [ -z "$NGROK_BIN" ]; then
        echo -e "${RED}Ngrok binary not found! Please ensure it is installed correctly.${NOCOLOR}"
        exit 1
    fi

    echo -e "${BLUE}Creating ngrok systemd service...${NOCOLOR}"
    sudo tee /etc/systemd/system/ngrok.service > /dev/null <<EOT
[Unit]
Description=ngrok
After=network.target

[Service]
ExecStart=$NGROK_BIN start --all --config=/root/.ngrok2/ngrok.yml
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
EOT

    sudo systemctl daemon-reload
    sudo systemctl enable ngrok.service
    sudo systemctl start ngrok.service
    echo -e "${GREEN}ngrok service created and started.${NOCOLOR}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if ss -tuln | grep -q ":$port "; then
        echo -e "${RED}Error: Port $port is already in use.${NOCOLOR}"
        echo -e "${RED}Here's what's using the port:${NOCOLOR}"
        ss -tulnp | grep ":$port "
        return 1  # Port is in use
    else
        echo -e "${GREEN}Port $port is available.${NOCOLOR}"
        return 0  # Port is not in use
    fi
}

# Function to start Ngrok
start_ngrok() {
    echo -e "${GREEN}Starting Ngrok...${NOCOLOR}"
    while true; do
        echo -e "${YELLOW}Enter the port number you want to expose (default: 8080):${NOCOLOR}"
        read PORT
        PORT=${PORT:-8080}

        # Check if the port is in use
        if check_port $PORT; then
            break  # Port is available, exit the loop
        else
            echo -e "${RED}Port $PORT is in use. Please choose another port.${NOCOLOR}"
        fi
    done

    # Update ngrok configuration
    cat >> /root/.ngrok2/ngrok.yml <<EOL
tunnels:
  myapp:
    proto: http
    addr: $PORT
EOL

    # Create and start the service
    create_ngrok_service

    echo -e "${GREEN}Ngrok service is now running in the background.${NOCOLOR}"
    echo -e "${YELLOW}To check the status, use: sudo systemctl status ngrok.service${NOCOLOR}"
    echo -e "${YELLOW}To stop the service, use: sudo systemctl stop ngrok.service${NOCOLOR}"
}

# Function to test Ngrok
test_ngrok() {
    echo -e "${BLUE}Testing Ngrok installation...${NOCOLOR}"

    # Check if ngrok is installed
    if ! command_exists ngrok; then
        echo -e "${RED}Ngrok is not installed. Please install it first.${NOCOLOR}"
        return 1
    fi

    # Check ngrok version
    echo -e "${YELLOW}Ngrok version:${NOCOLOR}"
    ngrok version

    # Check if authtoken is set
    if ! ngrok config check; then
        echo -e "${RED}Authtoken is not set. Please set it up.${NOCOLOR}"
        setup_ngrok
    else
        echo -e "${GREEN}Authtoken is set.${NOCOLOR}"
    fi

    echo -e "${GREEN}Ngrok test completed.${NOCOLOR}"
}

# Function to check ngrok service status
check_ngrok_service() {
    echo -e "${BLUE}Checking ngrok service status...${NOCOLOR}"
    SERVICE_STATUS=$(sudo systemctl is-active ngrok.service)

    if [ "$SERVICE_STATUS" = "active" ]; then
        echo -e "${GREEN}ngrok service is active and running.${NOCOLOR}"
        return 0
    else
        echo -e "${RED}ngrok service is not active. Current status: $SERVICE_STATUS${NOCOLOR}"
        return 1
    fi
}

# Function to upgrade ngrok configuration
upgrade_ngrok_config() {
    echo -e "${BLUE}Upgrading ngrok configuration...${NOCOLOR}"
    ngrok config upgrade
    echo -e "${GREEN}Ngrok configuration upgraded.${NOCOLOR}"
}

# Main script execution
echo -e "${BLUE}Starting Ngrok installation and setup...${NOCOLOR}"

# Check and install dependencies
if ! command_exists curl; then
    install_dependencies
fi

# Check if Ngrok is already installed
if ! command_exists ngrok; then
    install_ngrok
else
    echo -e "${GREEN}Ngrok is already installed.${NOCOLOR}"
fi

# Set up Ngrok configuration
setup_ngrok

# Test Ngrok installation
test_ngrok

# Upgrade ngrok configuration
upgrade_ngrok_config

# Start Ngrok as a service
start_ngrok

# Function to display ngrok connection information
display_ngrok_info() {
    echo -e "${BLUE}Fetching ngrok connection information...${NOCOLOR}"

    # Wait for ngrok to establish a connection
    sleep 5

    # Fetch ngrok status
    NGROK_STATUS=$(curl -s http://localhost:4040/api/tunnels)

    if [ -z "$NGROK_STATUS" ]; then
        echo -e "${RED}Unable to fetch ngrok status. Make sure ngrok is running.${NOCOLOR}"
        return 1
    fi

    # Extract and display information
    PUBLIC_URL=$(echo $NGROK_STATUS | jq -r '.tunnels[0].public_url')
    PROTO=$(echo $NGROK_STATUS | jq -r '.tunnels[0].proto')
    REGION=$(echo $NGROK_STATUS | jq -r '.tunnels[0].region')

    echo -e "${GREEN}Ngrok connection established:${NOCOLOR}"
    echo -e "Public URL: ${YELLOW}$PUBLIC_URL${NOCOLOR}"
    echo -e "Protocol: ${YELLOW}$PROTO${NOCOLOR}"
    # echo -e "Region: ${YELLOW}$REGION${NOCOLOR}"

    # Fetch and display latency
    # LATENCY=$(curl -s http://localhost:4040/api/metrics | jq -r '.latency.p50')
    # echo -e "Latency (p50): ${YELLOW}${LATENCY}ms${NOCOLOR}"

    # Display local port being forwarded
    LOCAL_PORT=$(echo $NGROK_STATUS | jq -r '.tunnels[0].config.addr' | sed 's/:.*//')
    echo -e "Local Port: ${YELLOW}$LOCAL_PORT${NOCOLOR}"

    echo -e "\n${GREEN}To stop ngrok, use: ${YELLOW}sudo systemctl stop ngrok.service${NOCOLOR}"
}

# Wait for 2 seconds before checking status
echo -e "${YELLOW}Waiting for 2 seconds before checking service status...${NOCOLOR}"
sleep 2.5

# Check service status
if check_ngrok_service; then
    # Display ngrok connection information
    display_ngrok_info
else
    echo -e "${YELLOW}Please start the ngrok service and try again.${NOCOLOR}"
fi

echo -e "${GREEN}Ngrok installation, setup, and service creation complete.${NOCOLOR}"
