# Use a base image with good VNC support
FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables
ENV USER=root
ENV PASSWORD=root
ENV DISPLAY=:0
ENV RESOLUTION=1024x768x24

# Install necessary packages
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    xfce4 \
    xfce4-goodies \
    supervisor \
    net-tools \
    vim \
    wget \
    xterm \
    curl \
    xdotool \
    python3 \
    python3-pip \
    xserver-xorg-input-all \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /root/.vnc /etc/supervisor/conf.d

# Set VNC password
RUN x11vnc -storepasswd ${PASSWORD} /root/.vnc/passwd

# Configure supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create a startup script
RUN echo '#!/bin/bash\n\
Xvfb $DISPLAY -screen 0 $RESOLUTION -ac +extension GLX +render -noreset &\n\
sleep 1\n\
xfce4-session &\n\
x11vnc -display $DISPLAY -forever -usepw -create -shared -rfbport 5900\n'\
> /root/startup.sh && chmod +x /root/startup.sh

# Create supervisor configuration
RUN echo '[supervisord]\n\
nodaemon=true\n\
\n\
[program:startup]\n\
command=/root/startup.sh\n\
autorestart=true\n\
priority=1000\n'\
> /etc/supervisor/conf.d/supervisord.conf

# Configure X11 input devices
RUN echo 'Section "InputClass"\n\
    Identifier "evdev keyboard catchall"\n\
    MatchIsKeyboard "on"\n\
    Option "XkbLayout" "us"\n\
    Driver "evdev"\n\
EndSection\n\
\n\
Section "InputClass"\n\
    Identifier "evdev pointer catchall"\n\
    MatchIsPointer "on"\n\
    Driver "evdev"\n\
EndSection' > /etc/X11/xorg.conf.d/10-input.conf

# Create .Xauthority to prevent access issues
RUN touch /root/.Xauthority

# Expose VNC port
EXPOSE 5900

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]