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
sudo apt update

# Enable 32-bit architecture
print_color "$YELLOW" "Enabling 32-bit architecture..."
sudo dpkg --add-architecture i386

# Add Wine repository key
print_color "$YELLOW" "Adding Wine repository key..."
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key

# Add Wine repository
print_color "$YELLOW" "Adding Wine repository..."
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/$(lsb_release -sc)/winehq-$(lsb_release -sc).sources

# Update package list again
print_color "$YELLOW" "Updating package list..."
sudo apt update

# Install Wine
print_color "$YELLOW" "Installing Wine..."
sudo DEBIAN_FRONTEND=noninteractive apt install --install-recommends winehq-stable -y

# Set up Wine prefix
print_color "$YELLOW" "Setting up Wine prefix..."
WINEARCH=win32 WINEPREFIX=~/.wine wineboot --init

# Disable Gecko and Mono installation prompts
print_color "$YELLOW" "Disabling Gecko and Mono installation prompts..."
cat > ~/.wine/user.reg << EOL
[HKEY_CURRENT_USER\Software\Wine\DllOverrides]
"winemenubuilder.exe"=""
[HKEY_CURRENT_USER\Software\Wine\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NewStartPanel]
"Use Start Banner"=dword:00000000
EOL

# Print Wine version
print_color "$GREEN" "Wine installation complete!"
wine --version
