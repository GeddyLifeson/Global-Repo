#!/bin/bash
# S0313 cmd.sh LOG "command" : send a console command to a server started by srvup.sh (rcon alternative: S0071 rcon.py)
echo "$2" > "$1.in"
