# S6855 drive.py: input + screenshots for a headless Minecraft client on Xvfb (python-xlib XTest; ImageMagick `import`).
# Mouse clicks only reach GUI screens (cursor free); in-world aiming is done server-side with /tp NAME x y z yaw pitch.
import os, subprocess, time
from Xlib import X, XK, display
from Xlib.ext import xtest

DISPLAY = os.environ.get('DISPLAY', ':96')
_d = None
def d():
    global _d
    if _d is None: _d = display.Display(DISPLAY)
    return _d

SHIFT_CHARS = {'_': 'minus', ':': 'semicolon', '"': 'apostrophe', '{': 'bracketleft', '}': 'bracketright', '<': 'comma', '>': 'period', '?': 'slash', '+': 'equal', '|': 'backslash', '~': 'grave', '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0'}
NAMED = {' ': 'space', '/': 'slash', '.': 'period', ',': 'comma', '-': 'minus', '=': 'equal', ';': 'semicolon', "'": 'apostrophe', '[': 'bracketleft', ']': 'bracketright', '\\': 'backslash', '`': 'grave'}

def _kc(name):
    return d().keysym_to_keycode(XK.string_to_keysym(name))

def key(name, shift=False, hold=0.04):
    kc = _kc(name); dp = d()
    if shift: xtest.fake_input(dp, X.KeyPress, _kc('Shift_L'))
    xtest.fake_input(dp, X.KeyPress, kc); dp.sync(); time.sleep(hold)
    xtest.fake_input(dp, X.KeyRelease, kc)
    if shift: xtest.fake_input(dp, X.KeyRelease, _kc('Shift_L'))
    dp.sync(); time.sleep(0.03)

def text(s):
    for ch in s:
        if ch.isalpha(): key(ch.lower(), shift=ch.isupper())
        elif ch.isdigit(): key(ch)
        elif ch in SHIFT_CHARS: key(SHIFT_CHARS[ch], shift=True)
        else: key(NAMED[ch])

def chat(line):
    """Open chat with t, type line (leading / ok), send with Enter."""
    key('t'); time.sleep(0.4); text(line); time.sleep(0.2); key('Return'); time.sleep(0.5)

def move(x, y):
    xtest.fake_input(d(), X.MotionNotify, x=x, y=y); d().sync(); time.sleep(0.05)

def click(x, y, button=1):
    move(x, y); time.sleep(0.1)
    xtest.fake_input(d(), X.ButtonPress, button); d().sync(); time.sleep(0.08)
    xtest.fake_input(d(), X.ButtonRelease, button); d().sync(); time.sleep(0.3)

def shot(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    subprocess.run(['import', '-window', 'root', path], env={**os.environ, 'DISPLAY': DISPLAY}, check=True)
    return path

def hold(name, secs):
    """Hold a key down for secs (movement, throttle)."""
    kc = _kc(name); dp = d()
    xtest.fake_input(dp, X.KeyPress, kc); dp.sync(); time.sleep(secs)
    xtest.fake_input(dp, X.KeyRelease, kc); dp.sync()
