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

# Stop Wine services
print_color "$YELLOW" "Stopping Wine services..."
wineserver -k || print_color "$RED" "Failed to stop Wine services"

# Uninstall Wine
print_color "$YELLOW" "Uninstalling Wine..."
sudo apt remove --purge winehq-stable wine-stable wine-stable-amd64 wine-stable-i386 wine32:i386 -y || print_color "$RED" "Failed to uninstall Wine"

# Remove Wine dependencies
print_color "$YELLOW" "Removing Wine dependencies..."
sudo apt autoremove -y || print_color "$RED" "Failed to remove dependencies"

# Remove Wine configuration files
print_color "$YELLOW" "Removing Wine configuration files..."
rm -rf ~/.wine || print_color "$RED" "Failed to remove Wine configuration files"

# Remove Wine menu entries
print_color "$YELLOW" "Removing Wine menu entries..."
rm -f ~/.config/menus/applications-merged/wine* || print_color "$RED" "Failed to remove Wine menu entries"
rm -rf ~/.local/share/applications/wine || print_color "$RED" "Failed to remove Wine application shortcuts"

# Remove Wine icons
print_color "$YELLOW" "Removing Wine icons..."
rm -f ~/.local/share/icons/hicolor/*/*/application-x-wine-extension* || print_color "$RED" "Failed to remove Wine icons"

# Remove Wine repository
print_color "$YELLOW" "Removing Wine repository..."
sudo rm -f /etc/apt/sources.list.d/winehq-*.sources || print_color "$RED" "Failed to remove Wine repository"

# Remove Wine repository key
print_color "$YELLOW" "Removing Wine repository key..."
sudo rm -f /etc/apt/keyrings/winehq-archive.key || print_color "$RED" "Failed to remove Wine repository key"

# Remove winetricks
print_color "$YELLOW" "Removing winetricks..."
sudo rm -f /usr/local/bin/winetricks || print_color "$RED" "Failed to remove winetricks"

# Update package list
print_color "$YELLOW" "Updating package list..."
sudo apt update || print_color "$RED" "Failed to update package list"

print_color "$GREEN" "Wine and its dependencies have been removed successfully!"
