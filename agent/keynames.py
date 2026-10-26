KEY_NAMES = frozenset(
    {"esc", "enter", "backspace", "tab", "space", "delete",
     "up", "down", "left", "right", "home", "end", "pageup", "pagedown", "f5"}
    | set("abcdefghijklmnopqrstuvwxyz0123456789")
)
MOD_NAMES = frozenset({"ctrl", "alt", "shift", "meta"})