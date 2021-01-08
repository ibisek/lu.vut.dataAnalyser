#!/bin/bash

clear

source ./venv/bin/activate

export PYTHONPATH=.:./src:$PYTHONPATH

while true
do
  python3 -u ./src/serverApp.py | tee progress.log 2>&1
  sleep 10
done

deactivate

