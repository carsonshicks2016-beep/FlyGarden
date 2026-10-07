#!/bin/zsh
set -e
cd /Users/carsonhicks/FlyGarden
exec /Users/carsonhicks/FlyGarden/.venv-next/bin/python /Users/carsonhicks/FlyGarden/scripts/launcher.py "$@"
