#!/bin/bash

echo "" > pids

motion &
echo "$!" >> pids

python ./scripts/files_manager.py &
echo "$!" >> pids

python ./scripts/images_processing.py &
echo "$!" >> pids

