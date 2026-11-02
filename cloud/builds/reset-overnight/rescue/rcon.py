"""Minimal Minecraft RCON client (stdlib only) plus parsing of the fork's PROBE/SCAN lines."""
import re, socket, struct


def encode_packet(rid, typ, body):
    payload = struct.pack("<ii", rid, typ) + body.encode("utf8") + b"\x00\x00"
    return struct.pack("<i", len(payload)) + payload


def decode_packet(data):
    rid, typ = struct.unpack("<ii", data[:8])
    return rid, typ, data[8:-2].decode("utf8", "replace")


class Rcon:
    def __init__(self, host, port, password, timeout=60):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.s.settimeout(timeout)
        self.s.sendall(encode_packet(1, 3, password))
        rid, _, _ = self._recv()
        if rid == -1:
            raise PermissionError("rcon auth failed")

    def _read(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.s.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("rcon closed")
            buf += chunk
        return buf

    def _recv(self):
        n = struct.unpack("<i", self._read(4))[0]
        return decode_packet(self._read(n))

    def command(self, cmd):
        self.s.sendall(encode_packet(2, 2, cmd))
        return self._recv()[2]

    def close(self):
        self.s.close()


_KV = re.compile(r"(\w+)=(\S+)")


def _conv(v):
    if v in ("true", "false"):
        return v == "true"
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


def parse_kv_line(text):
    m = re.search(r"\b(PROBE|SCAN)\b(.*)", text)
    if not m:
        return None
    d = {"kind": m.group(1)}
    for k, v in _KV.findall(m.group(2)):
        d[k] = _conv(v)
    return d
