#!/bin/bash
# S0333 shot.sh FILE.png : screenshot of the Xvfb display (env DISPLAY_NUM, default 96)
DISPLAY=:${DISPLAY_NUM:-96} xwd -root -silent 2>/dev/null | convert xwd:- "$1"
