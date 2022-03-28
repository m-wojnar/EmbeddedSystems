#!/bin/bash

rm -f /var/lib/motion/*
rm -f ./outputs/*
rm -f ./server/static/output.png

motion &
python ./scripts/main.py &
python ./server/app.py &
