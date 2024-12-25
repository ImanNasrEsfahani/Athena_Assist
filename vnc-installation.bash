#!/bin/bash

# Function to generate a random password
generate_password() {
    local length=12
    local chars='abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    tr -dc "$chars" < /dev/urandom | head -c "$length"
}

# Generate a random password
VNC_PASSWORD=$(generate_password)

# Update package list
sudo apt update -y

# Install Xfce desktop environment, VNC server, and autocutsel
sudo apt install -y xfce4 xfce4-goodies tightvncserver autocutsel

# Install Firefox
sudo apt install -y firefox nano gedit zip unzip

# Set VNC password automatically
mkdir -p ~/.vnc
echo "$VNC_PASSWORD" | vncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd

# Create VNC configuration file
cat > ~/.vnc/xstartup << EOF
#!/bin/bash
xrdb $HOME/.Xresources
autocutsel -fork
autocutsel -selection PRIMARY -fork
startxfce4 &
EOF

# Make the xstartup file executable
chmod +x ~/.vnc/xstartup

# Create a systemd service file for VNC
sudo tee /etc/systemd/system/vncserver@.service > /dev/null << EOF
[Unit]
Description=Start TightVNC server at startup
After=syslog.target network.target

[Service]
Type=forking
User=$USER
Group=$USER
WorkingDirectory=$HOME

PIDFile=$HOME/.vnc/%H:%i.pid
ExecStartPre=-/usr/bin/vncserver -kill :%i > /dev/null 2>&1
ExecStart=/usr/bin/vncserver -depth 24 -geometry 1280x800 :%i
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable VNC service
sudo systemctl enable vncserver@1.service

# Start VNC service
sudo systemctl start vncserver@1

# Set up firewall rules (if UFW is enabled)
sudo ufw allow 5901/tcp

# Install xfonts-base to prevent grey screen issues
sudo apt install -y xfonts-base
vncconfig &

# Check the SSH port in use by reading the sshd_config file
ssh_port=$(grep -i "^Port" /etc/ssh/sshd_config | awk '{print $2}')
ssh_port=${ssh_port:-22}  # Default to 22 if not found

# Define color codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print connection information
echo -e "${GREEN}VNC server and Firefox installation complete!${NC}"
echo -e "${YELLOW}To connect, create an SSH tunnel with:${NC}"
echo -e "${CYAN}ssh -L 59000:localhost:5901 -C -N -l $USER $(hostname -I | awk '{print $1}') -p $ssh_port${NC}"
echo -e "${YELLOW}Generated VNC password:${NC} ${CYAN}$VNC_PASSWORD${NC}"
echo -e "${YELLOW}Download and install some VNC application like TightVNC Viewer that is free${NC}"
echo -e "${YELLOW}Then use a VNC client to connect to${NC} ${CYAN}localhost:59000${NC}"
echo -e "${YELLOW}Copy-paste functionality should now be enabled between your local machine and the VNC session.${NC}"
echo -e "${YELLOW}Firefox browser is now installed and available in your VNC session.${NC}"
