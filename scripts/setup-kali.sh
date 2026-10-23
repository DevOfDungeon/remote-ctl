#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y python3-venv python3-dev build-essential

# uinput: kernel module + permission for the 'input' group
sudo modprobe uinput
echo uinput | sudo tee /etc/modules-load.d/uinput.conf >/dev/null
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-uinput.rules >/dev/null
sudo usermod -aG input "$USER"
sudo udevadm control --reload && sudo udevadm trigger

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
echo "Done. Log out and back in so the 'input' group applies."