import sys

from .base import InputBackend


def get_backend() -> InputBackend:
    if sys.platform.startswith("linux"):
        from .linux_uinput import Backend
    elif sys.platform == "win32":
        from .windows_sendinput import Backend
    else:
        raise RuntimeError(f"unsupported platform: {sys.platform}")
    return Backend()