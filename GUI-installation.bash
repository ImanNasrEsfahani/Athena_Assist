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
    print_color "$GREEN" "Script is running as root"
    return 0
elif groups | grep -q '\bsudo\b'; then
    if sudo -v -n &>/dev/null; then
        print_color "$GREEN" "User has sudo privileges and is authenticated"
        return 0
    else
        print_color "$YELLOW" "User has sudo privileges but needs to authenticate"
        sudo -v || return 1
        print_color "$GREEN" "Authentication successful"
        return 0
    fi
else
    print_color "$RED" "This script requires root privileges or sudo access"
    return 1
fi

# Check system version and distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    print_color "$BLUE" "Distribution: $NAME"
    print_color "$BLUE" "Version: $VERSION"
    print_color "$BLUE" "Codename: $VERSION_CODENAME"
else
    print_color "$RED" "Unable to determine system version and distribution"
    exit 1
fi

# Check if the distribution is Ubuntu and version is 20
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$NAME" = "Ubuntu" ] && [[ "$VERSION_ID" == "20."* ]]; then
        print_color "$GREEN" "Distribution is Ubuntu 20. Proceeding..."
    else
        print_color "$RED" "Distribution is not Ubuntu 20. Exiting..."
        exit 1
    fi
else
    print_color "$RED" "/etc/os-release file not found. Unable to determine distribution."
    exit 1
fi

# Function to generate a random password
generate_password() {
    local length=12
    local chars='abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    tr -dc "$chars" < /dev/urandom | head -c "$length"
}

# Update package list
sudo apt update -y || { print_color "$RED" "Failed to update apt packages"; exit 1; }

# Install Xfce desktop environment, VNC server, and autocutsel
sudo apt install -y xfce4 xfce4-goodies tightvncserver autocutsel || { print_color "$RED" "Failed to install xfce desktop environment"; exit 1; }

# Install more packages
sudo apt install -y firefox nano gedit zip unzip screen jq || { print_color "$RED" "Failed to install requirement packages like firefox gedit zip and etc"; exit 1; }
