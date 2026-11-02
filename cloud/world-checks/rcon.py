import socket, struct, sys
def rcon(cmds, host="127.0.0.1", port=25575, pw="x"):
    s = socket.create_connection((host, port), timeout=600)
    def send(i, t, body):
        b = body.encode() + b"\0\0"
        s.sendall(struct.pack("<iii", len(b) + 8, i, t) + b)
        n = struct.unpack("<i", s.recv(4))[0]
        data = b""
        while len(data) < n: data += s.recv(n - len(data))
        return data[8:-2].decode(errors="replace")
    send(1, 3, pw)
    return [send(2, 2, c) for c in cmds]
if __name__ == "__main__":
    for r in rcon(sys.argv[1:]): print(r)
