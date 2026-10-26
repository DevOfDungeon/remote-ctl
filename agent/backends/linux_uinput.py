from evdev import UInput
from evdev import ecodes as e

from .. import keynames
from .base import InputBackend

_BUTTONS = {"left": e.BTN_LEFT, "right": e.BTN_RIGHT, "middle": e.BTN_MIDDLE}

# named keys the phone may press
_KEYS = {
    "esc": e.KEY_ESC, "enter": e.KEY_ENTER, "backspace": e.KEY_BACKSPACE,
    "tab": e.KEY_TAB, "space": e.KEY_SPACE, "delete": e.KEY_DELETE,
    "up": e.KEY_UP, "down": e.KEY_DOWN, "left": e.KEY_LEFT, "right": e.KEY_RIGHT,
    "home": e.KEY_HOME, "end": e.KEY_END, "pageup": e.KEY_PAGEUP,
    "pagedown": e.KEY_PAGEDOWN, "f5": e.KEY_F5,
}
for _c in "abcdefghijklmnopqrstuvwxyz0123456789":
    _KEYS[_c] = getattr(e, f"KEY_{_c.upper()}")

_MODS = {"ctrl": e.KEY_LEFTCTRL, "alt": e.KEY_LEFTALT,
         "shift": e.KEY_LEFTSHIFT, "meta": e.KEY_LEFTMETA}

assert set(_KEYS) == set(keynames.KEY_NAMES), "keymap out of sync with keynames"

# characters for type_text (US layout): char -> (keycode, needs_shift)
_SHIFTED_DIGITS = ")!@#$%^&*("
_PUNCT = {
    " ": (e.KEY_SPACE, False), "\n": (e.KEY_ENTER, False),
    "-": (e.KEY_MINUS, False), "_": (e.KEY_MINUS, True),
    "=": (e.KEY_EQUAL, False), "+": (e.KEY_EQUAL, True),
    ",": (e.KEY_COMMA, False), "<": (e.KEY_COMMA, True),
    ".": (e.KEY_DOT, False), ">": (e.KEY_DOT, True),
    "/": (e.KEY_SLASH, False), "?": (e.KEY_SLASH, True),
    ";": (e.KEY_SEMICOLON, False), ":": (e.KEY_SEMICOLON, True),
    "'": (e.KEY_APOSTROPHE, False), '"': (e.KEY_APOSTROPHE, True),
    "[": (e.KEY_LEFTBRACE, False), "{": (e.KEY_LEFTBRACE, True),
    "]": (e.KEY_RIGHTBRACE, False), "}": (e.KEY_RIGHTBRACE, True),
    "\\": (e.KEY_BACKSLASH, False), "|": (e.KEY_BACKSLASH, True),
    "`": (e.KEY_GRAVE, False), "~": (e.KEY_GRAVE, True),
}

_KBD_CODES = sorted(
    set(_KEYS.values()) | set(_MODS.values()) | {code for code, _ in _PUNCT.values()}
)


def _char_to_key(ch: str):
    if ch.isascii() and ch.isalpha():
        return getattr(e, f"KEY_{ch.upper()}"), ch.isupper()
    if ch.isascii() and ch.isdigit():
        return getattr(e, f"KEY_{ch}"), False
    if ch in _SHIFTED_DIGITS:
        return getattr(e, f"KEY_{_SHIFTED_DIGITS.index(ch)}"), True
    return _PUNCT.get(ch)


class Backend(InputBackend):
    def __init__(self) -> None:
        self.mouse = UInput(
            {
                e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_HWHEEL],
                e.EV_KEY: list(_BUTTONS.values()),
            },
            name="remote-ctl-mouse",
        )
        self.kbd = UInput({e.EV_KEY: _KBD_CODES}, name="remote-ctl-keyboard")

    # ---- mouse ----
    def move(self, dx: int, dy: int) -> None:
        self.mouse.write(e.EV_REL, e.REL_X, dx)
        self.mouse.write(e.EV_REL, e.REL_Y, dy)
        self.mouse.syn()

    def scroll(self, dx: int, dy: int) -> None:
        self.mouse.write(e.EV_REL, e.REL_WHEEL, dy)
        self.mouse.write(e.EV_REL, e.REL_HWHEEL, -dx)
        self.mouse.syn()

    def click(self, button: str) -> None:
        code = _BUTTONS[button]
        self.mouse.write(e.EV_KEY, code, 1)
        self.mouse.syn()
        self.mouse.write(e.EV_KEY, code, 0)
        self.mouse.syn()

    # ---- keyboard ----
    def _k(self, code: int, down: int) -> None:
        self.kbd.write(e.EV_KEY, code, down)
        self.kbd.syn()

    def key(self, name, mods=()):
        held = [_MODS[m] for m in mods]
        for m in held:
            self._k(m, 1)
        self._k(_KEYS[name], 1)
        self._k(_KEYS[name], 0)
        for m in reversed(held):
            self._k(m, 0)

    def type_text(self, text: str) -> None:
        for ch in text:
            mapped = _char_to_key(ch)
            if mapped is None:
                continue  # unsupported character: skip it
            code, shift = mapped
            if shift:
                self._k(e.KEY_LEFTSHIFT, 1)
            self._k(code, 1)
            self._k(code, 0)
            if shift:
                self._k(e.KEY_LEFTSHIFT, 0)

    def close(self) -> None:
        self.mouse.close()
        self.kbd.close()