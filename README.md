# remote-ctl
Control a computer from your phone: trackpad, keyboard, slides.

## Run
    ./scripts/setup-kali.sh        # once; then log out/in
    source .venv/bin/activate
    RC_TOKEN=choose-a-long-secret RC_HOST=0.0.0.0 python -m agent

Open http://<pc-ip>:8000 on your phone and enter the token.

## Gestures
tap = click · two-finger tap = right click · two-finger drag = scroll

## Security
Read docs/threat-model.md before exposing this beyond your LAN.
The tool injects keyboard and mouse input, runs over plain HTTP in v0.1, and shouldn’t be exposed beyond a trusted network.
