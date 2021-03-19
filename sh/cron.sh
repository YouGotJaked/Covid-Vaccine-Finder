#!/bin/bash
cwd="$(dirname "$0")"
cd $cwd/../
source ./venv/bin/activate && python3 -m covid --find --notify
