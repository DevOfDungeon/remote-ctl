# Threat model

**Asset:** the ability to move the mouse and type as the logged-in user.
That is equivalent to full control of the session.

**Attackers:** (1) anyone on the same LAN/Wi-Fi, (2) anyone who sniffs traffic,
(3) a malicious page open in the phone browser, (4) local processes on the PC.

**Current mitigations:** bearer token (constant-time compare), strict message
schema + value limits, loopback bind by default, no root, token not in URL.

**Known gaps (todo):** no TLS (token + input visible on the wire), no origin
check on the WebSocket, token stored in localStorage, in-memory rate limit only,
/dev/uinput is writable by the whole `input` group.