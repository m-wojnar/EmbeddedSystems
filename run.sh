#!/bin/bash

rm -f ./server/static/*

python ./scripts/main.py &
python ./server/app.py &
