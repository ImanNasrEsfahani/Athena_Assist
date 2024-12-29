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

# Update package list
print_color "$YELLOW" "Updating package list..."
sudo apt update || { print_color "$RED" "Failed to update apt packages"; exit 1; }

# Enable 32-bit architecture
print_color "$YELLOW" "Enabling 32-bit architecture..."
sudo dpkg --add-architecture i386 || { print_color "$RED" "Failed to make system 32 bit"; exit 1; }

# Add Wine repository key
print_color "$YELLOW" "Adding Wine repository key..."
sudo mkdir -pm755 /etc/apt/keyrings || { print_color "$RED" "Failed to create folder"; exit 1; }
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key || { print_color "$RED" "Failed to download Wine repository key"; exit 1; }

# Add Wine repository
print_color "$YELLOW" "Adding Wine repository..."
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/$(lsb_release -sc)/winehq-$(lsb_release -sc).sources || { print_color "$RED" "Failed to add Wine repository"; exit 1; }

# Update package list again
print_color "$YELLOW" "Updating package list..."
sudo apt update || { print_color "$RED" "Failed to update apt packages"; exit 1; }

# Install Wine
print_color "$YELLOW" "Installing Wine..."
sudo DEBIAN_FRONTEND=noninteractive apt install --install-recommends winehq-stable -y || { print_color "$RED" "Failed to install Wine"; exit 1; }

# Set up Wine prefix
print_color "$YELLOW" "Setting up Wine prefix..."
WINEARCH=win32 WINEPREFIX=~/.wine wineboot --init || { print_color "$RED" "Failed to set up Wine prefix"; exit 1; }

# Disable Gecko and Mono installation prompts
print_color "$YELLOW" "Disabling Gecko and Mono installation prompts..."
cat > ~/.wine/user.reg << EOL
[HKEY_CURRENT_USER\Software\Wine\DllOverrides]
"winemenubuilder.exe"=""
[HKEY_CURRENT_USER\Software\Wine\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NewStartPanel]
"Use Start Banner"=dword:00000000
EOL

# Install winetricks
print_color "$YELLOW" "Installing winetricks..."
sudo apt install -y cabextract || { print_color "$RED" "Failed to install cabextract"; exit 1; }
wget https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks || { print_color "$RED" "Failed to download winetricks"; exit 1; }
sudo mv winetricks /usr/local/bin/
sudo chmod +x /usr/local/bin/winetricks || { print_color "$RED" "Failed to set permissions for winetricks"; exit 1; }

# Print Wine version
print_color "$GREEN" "Wine installation complete!"
wine --version || { print_color "$RED" "Failed to get Wine version"; exit 1; }

# Print winetricks version
print_color "$GREEN" "Winetricks installation complete!"
winetricks --version || { print_color "$RED" "Failed to get winetricks version"; exit 1; }
