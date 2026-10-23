from evdev import UInput
from evdev import ecodes as e

from .base import InputBackend

_BUTTONS = {"left": e.BTN_LEFT, "right": e.BTN_RIGHT, "middle": e.BTN_MIDDLE}


class Backend(InputBackend):
    def __init__(self) -> None:
        self.mouse = UInput(
            {
                e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_HWHEEL],
                e.EV_KEY: list(_BUTTONS.values()),
            },
            name="remote-ctl-mouse",
        )

    def move(self, dx: int, dy: int) -> None:
        self.mouse.write(e.EV_REL, e.REL_X, dx)
        self.mouse.write(e.EV_REL, e.REL_Y, dy)
        self.mouse.syn()

    def scroll(self, dx: int, dy: int) -> None:
        # natural scrolling: finger down = content down. Flip signs for traditional.
        self.mouse.write(e.EV_REL, e.REL_WHEEL, dy)
        self.mouse.write(e.EV_REL, e.REL_HWHEEL, -dx)
        self.mouse.syn()

    def click(self, button: str) -> None:
        code = _BUTTONS[button]
        self.mouse.write(e.EV_KEY, code, 1)
        self.mouse.syn()
        self.mouse.write(e.EV_KEY, code, 0)
        self.mouse.syn()

    def close(self) -> None:
        self.mouse.close()