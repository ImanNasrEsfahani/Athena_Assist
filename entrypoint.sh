#!/bin/bash

# Start Xvfb
Xvfb :99 -screen 0 1024x768x16 &
export DISPLAY=:99

# Start the mt5linux server
wine python -m mt5linux "C:\users\root\AppData\Local\Programs\Python\Python310\python.exe"
