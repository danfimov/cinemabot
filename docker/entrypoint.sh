#!/bin/sh

set -e

if [ "$RUN_MIGRATIONS_ON_STARTUP" = 1 ]
then
    >&2 echo "Applying migrations..."
    cd cinemabot/migrator && poetry run python main.py upgrade head && cd ../..
fi

exec "$@"
