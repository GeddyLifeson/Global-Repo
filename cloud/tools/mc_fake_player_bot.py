# S6843 Headless fake-player bot for Minecraft 26.1.2 (protocol 775): logs in offline, answers keep-alives, chunk batches and teleports so spawners and other player-triggered things run on a server with no client. Usage: bot.py HOST PORT NAME LOGFILE (server compression handled).
import socket,struct,sys,time,uuid,threading,zlib
COMP=[False]
HOST,PORT,NAME=sys.argv[1],int(sys.argv[2]),sys.argv[3]
def vi(n):
    o=b""
    while True:
        b=n&0x7f; n>>=7
        if n: o+=bytes([b|0x80])
        else: o+=bytes([b]); return o
def rvi(s):
    n=0;sh=0
    while True:
        b=s.recv(1)
        if not b: raise EOFError
        b=b[0]; n|=(b&0x7f)<<sh; sh+=7
        if not b&0x80: return n
def st(x): b=x.encode(); return vi(len(b))+b
s=socket.create_connection((HOST,PORT))
def send(i,payload=b""):
    d=vi(i)+payload
    if COMP[0]: d=vi(0)+d
    s.sendall(vi(len(d))+d)
def rd():
    n=rvi(s); d=b""
    while len(d)<n:
        c=s.recv(n-len(d))
        if not c: raise EOFError
        d+=c
    if COMP[0]:
        j=0;sh=0;dl=0
        while True:
            b=d[j];j+=1;dl|=(b&0x7f)<<sh;sh+=7
            if not b&0x80: break
        d=d[j:] if dl==0 else zlib.decompress(d[j:])
    i=0;sh=0;pid=0
    while True:
        b=d[i];i+=1;pid|=(b&0x7f)<<sh;sh+=7
        if not b&0x80: break
    return pid,d[i:]
send(0,vi(775)+st(HOST)+struct.pack(">H",PORT)+vi(2))
send(0,st(NAME)+uuid.uuid3(uuid.NAMESPACE_DNS,NAME).bytes)
state="login"; t0=time.time(); log=open(sys.argv[4],"w")
def L(*a): log.write(" ".join(map(str,a))+"\n"); log.flush()
while True:
    pid,p=rd()
    if state=="login":
        L("login",pid,len(p))
        if pid==2: send(3); state="config"
        elif pid==0: L("DISCONNECT",p[:200]); break
        elif pid==3: COMP[0]=True; L('compression on')
    elif state=="config":
        L("config",pid,len(p))
        if pid==14: send(7,vi(0))
        elif pid==3: send(3); state="play"
        elif pid==4: send(4,p[:8])
        elif pid==5: send(5,p[:4])
        elif pid==2: L("disconnect",p[:300]); break
    else:
        if pid==44: send(28,p[:8])
        elif pid==61: send(45,p[:4])
        elif pid==11: send(11,struct.pack(">f",20.0))
        elif pid==49 and not hasattr(sys,"loaded"): sys.loaded=1; send(44); L("joined play")
        elif pid==72:
            n=0;sh=0;i=0
            while True:
                b=p[i];i+=1;n|=(b&0x7f)<<sh;sh+=7
                if not b&0x80: break
            send(0,vi(n)); L('teleport confirm',n)
        # teleport confirm: unknown id, handle via any packet starting with small varint when name matches
        L("play",pid,len(p))
        if pid==0x46 or pid==70:
            pass
