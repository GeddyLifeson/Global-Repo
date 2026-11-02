#!/bin/bash
# shot.sh FILE.png
DISPLAY=:95 xwd -root -silent 2>/dev/null | convert xwd:- $1
