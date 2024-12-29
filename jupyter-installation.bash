#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NOCOLOR='\033[0m'

# Function to print colored output
print_color() {
    echo -e "${1}${2}${NOCOLOR}"
}

# Check if user is root or has sudo privileges
if [ "$(id -u)" -eq 0 ]; then
    echo "Script is running as root"
    return 0
elif groups | grep -q '\bsudo\b'; then
    if sudo -v -n &>/dev/null; then
        echo "User has sudo privileges and is authenticated"
        return 0
    else
        echo "User has sudo privileges but needs to authenticate"
        sudo -v || return 1
        echo "Authentication successful"
        return 0
    fi
else
    echo "This script requires root privileges or sudo access"
    return 1
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

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        print_color "$GREEN" "Success: $1"
    else
        print_color "$RED" "Error: $1 failed"
        exit 1
    fi
}

# Check if port 8888 is in use
sudo apt install -y jq netstat
if netstat -tuln | grep -q :8888; then
    print_color "$RED" "Error: Port 8888 is already in use. Please free up this port before running the script."
    port_info=$(sudo ss -tulnp | grep :8888)
    echo "$port_info"
    exit 1
else
    print_color "$GREEN" "Port 8888 is available. Proceeding with installation."
fi


# Update system packages
print_color "$BLUE" "Updating system packages..."
sudo apt update && sudo apt upgrade -y
check_success "System update"

# Install Python and pip
print_color "$BLUE" "Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-dev python3-venv jupyter-core
check_success "Python and pip installation"

# Create a virtual environment
print_color "$BLUE" "Creating a virtual environment..."
python3 -m venv ~/jupyter_env
source ~/jupyter_env/bin/activate
check_success "Virtual environment creation"

# Upgrade pip in the virtual environment
print_color "$BLUE" "Upgrading pip..."
pip install --upgrade pip
check_success "Pip upgrade"

# Install Jupyter and common data science packages
print_color "$BLUE" "Installing Jupyter and common packages..."
pip install jupyter numpy pandas matplotlib
check_success "Jupyter and package installation"

# Backup existing configuration
if [ -f ~/.jupyter/jupyter_notebook_config.py ]; then
    print_color "$BLUE" "Backing up existing Jupyter configuration..."
    cp ~/.jupyter/jupyter_notebook_config.py ~/.jupyter/jupyter_notebook_config.py.bak
fi

# jupyter password
jupyter notebook password
check_success "Jupyter password setup"

# Configure Jupyter
print_color "$BLUE" "Configuring Jupyter..."
cat << EOF >> ~/.jupyter/jupyter_notebook_config.py
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8888
c.NotebookApp.notebook_dir = '/'
EOF
check_success "Jupyter configuration"

# Configure firewall
print_color "$BLUE" "Configuring firewall..."
sudo ufw allow 8888
check_success "Firewall configuration"

# Create systemd service
# Find the path to jupyter-notebook
JUPYTER_PATH=$(which jupyter-notebook)
print_color "$BLUE" "Creating systemd service for Jupyter..."
print_color "$YELLOW" "Jupyter notebook path: $JUPYTER_PATH"

sudo tee /etc/systemd/system/jupyter.service > /dev/null <<EOF
[Unit]
Description=Jupyter Notebook

[Service]
Type=simple
PIDFile=/run/jupyter.pid
ExecStart=$JUPYTER_PATH --config=~/.jupyter/jupyter_notebook_config.py
User=$USER
Group=$USER
WorkingDirectory=/$USER
Restart=always
RestartSec=20

[Install]
WantedBy=multi-user.target
EOF
check_success "Systemd service creation"

# Start and enable the service
sudo systemctl daemon-reload
sudo systemctl enable jupyter.service
sudo systemctl start jupyter.service

# Function to check Jupyter installation status
check_jupyter_status() {
    print_color "$BLUE" "Checking Jupyter installation status..."

    if systemctl is-active --quiet jupyter.service; then
        print_color "$GREEN" "Jupyter is running successfully."
        jupyter_url=$(hostname -I | awk '{print $1}')
        print_color "$YELLOW" "You can access Jupyter Notebook at: http://$jupyter_url:8888"

        token=$(jupyter server list | grep -oP 'token=\K[a-zA-Z0-9]+')
        if [ -n "$token" ]; then
            print_color "$YELLOW" "Jupyter token: $token"
            print_color "$YELLOW" "You can access Jupyter at: http://localhost:8888/tree?token=$token"
        else
            print_color "$RED" "Jupyter token not found"
        fi

        # Check if Jupyter is responsive
        if curl -s --head --request GET "http://localhost:8888/tree?token=$token" | grep "200 OK" > /dev/null; then
            print_color "$GREEN" "Jupyter Notebook is responding to requests."
        else
            print_color "$RED" "Jupyter Notebook is not responding. Please check the configuration and logs."
        fi

    else
        print_color "$RED" "Jupyter service is not running. Please check the logs for errors."
        print_color "$YELLOW" "You can check the service status with: sudo systemctl status jupyter.service"
        print_color "$YELLOW" "Or you can check the cause by: journalctl -u jupyter.service -f"
        exit 1
    fi
}

sleep 2.5
check_jupyter_status

status_output=$(sudo systemctl status jupyter.service 2>&1)
echo "$status_output"

print_color "$GREEN" "Jupyter Notebook installation and configuration complete."
print_color "$YELLOW" "To check the status, use: sudo systemctl status jupyter.service"
print_color "$YELLOW" "To stop the service, use: sudo systemctl stop jupyter.service"
