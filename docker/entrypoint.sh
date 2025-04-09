#!/bin/sh

set -e

if [ "$RUN_MIGRATIONS_ON_STARTUP" = 1 ]
then
    >&2 echo "Applying migrations..."
    python3 -m cinemabot.infrastructure.database.migrations upgrade head
fi

exec "$@"
