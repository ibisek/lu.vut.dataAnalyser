#!/bin/bash

clear

source ./venv/bin/activate

export PYTHONPATH=.:./src:$PYTHONPATH

while true
do
  python3 ./src/serverApp.py
  sleep 10
done

deactivate

