#!/bin/bash

clear

source ./venv/bin/activate

export PYTHONPATH=$PYTHONPATH:.

cd src

python3 serverApp.py

deactivate

