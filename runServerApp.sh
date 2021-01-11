#!/bin/bash

clear

source ./venv/bin/activate

export PYTHONPATH=.:./src:$PYTHONPATH

while true
do
  python3 -u ./src/serverApp.py | tee -a progress.log 2>&1
  sleep 15
done

deactivate

