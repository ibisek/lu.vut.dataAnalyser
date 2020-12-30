#!/bin/bash

clear

source ./venv/bin/activate

export PYTHONPATH=$PYTHONPATH:.

cd src

while true
do
  python3 serverApp.py
  sleep 10
done

deactivate

