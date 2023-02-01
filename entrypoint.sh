#!/usr/bin/env bash

# -e exit on non 0 return
set -e
# -u exit on undefined variables
set -u
# -x print command before running
#set -x
# bubble up the non 0 on pipes
set -o pipefail

if [[ ! -v PORT ]]; then
    export PORT="8080"
fi

echo "Launching Entrypoint -> $@"

export BRANCH_NAME=${BRANCH_NAME}

#if [[ $# -gt 0 ]]; then
#  # execute whatever command you want
#  exec "$@"
#else
  # if there are no arguments passed, just start the webserver
  echo "Running webserver"
  uvicorn main:app --host 0.0.0.0 --port=${PORT}
#fi
