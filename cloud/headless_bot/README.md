# Headless client test lane (cloud)
Real NeoForge 26.1.2 server + real client (portablemc) under Xvfb. Handshake, registries, models, GUIs are real; screenshots via ImageMagick, keys/clicks via python-xlib.
- `lane.py` (S6854) Lane class: build server+client dirs from a jar list, boot, join, `server_cmd`, `look`, `shot`, log greps.
- `drive.py` (S6855) keys, chat, GUI clicks, screenshots. In-world mouse is not delivered; aim with `/tp Tester x y z yaw pitch`, use = R key.
- `discover.py` (S6867) registry ids a jar ships.
- `checks/qol_checks.py` (S6856), `checks/combat_checks.py` (S6868), `checks/bosses_rush.py` (S6870), `checks/storage_checks.py` (S6869).
One-time: `java -jar neoforge-26.1.2.116-installer.jar --install-server /tmp/claude-0/lane/srv-base`, JDK25 at /tmp/claude-0/jdk25 (tools/get_jdk25.sh), `pip install portablemc python-xlib pillow`.
Limits: light packs only (server 2.5-3G + client 3G); full pack does not fit. Flat overworld at spawn. First client start ~3 min (llvmpipe), later ~50 s.
