#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install xRDP and required packages
sudo apt install -y xrdp xorgxrdp ubuntu-desktop gnome-shell

# Add xrdp user to ssl-cert group
sudo adduser xrdp ssl-cert

# Configure xsession
echo "gnome-session" > ~/.xsession
chmod +x ~/.xsession

# Restart xRDP service
sudo systemctl restart xrdp

# Enable xRDP service to start on boot
sudo systemctl enable xrdp

# Configure polkit to allow color management for all users
sudo bash -c "cat > /etc/polkit-1/localauthority/50-local.d/45-allow-colord.pkla" << EOF
[Allow Colord for all users]
Identity=unix-user:*
Action=org.freedesktop.color-manager.create-device;org.freedesktop.color-manager.create-profile;org.freedesktop.color-manager.delete-device;org.freedesktop.color-manager.delete-profile;org.freedesktop.color-manager.modify-device;org.freedesktop.color-manager.modify-profile
ResultAny=no
ResultInactive=no
ResultActive=yes
EOF

# Disable light-locker to prevent screen locking issues
sudo apt remove -y light-locker

# Configure GNOME to use Xorg instead of Wayland
sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/' /etc/gdm3/custom.conf

# Allow console access
echo "allowed_users=anybody" | sudo tee /etc/X11/Xwrapper.config

# Restart GNOME Display Manager
sudo systemctl restart gdm3

# Check xRDP status
sudo systemctl status xrdp

echo "xRDP installation and configuration completed. Please reboot your system."
