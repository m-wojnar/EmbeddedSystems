#!/bin/bash

motion &
python ./scripts/files_manager.py &
python ./scripts/images_processing.py &

