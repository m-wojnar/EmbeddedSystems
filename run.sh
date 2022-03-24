#!/bin/bash

rm -f ./outputs/*
rm -f ./var/lib/motion/*

motion &
python ./scripts/files_manager.py &
python ./scripts/images_processing.py &
python ./server/app.py &
