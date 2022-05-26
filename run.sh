#!/bin/bash

VISUAL_MODE=false
BACKGROUND_MODE=false

ARGS_LIST=()

for arg in $@; do
    if [[ $arg == "--visual_mode" ]]; then
        VISUAL_MODE=true
        ARGS_LIST+=("--visual_mode")
    elif [[ $arg == "--interactive_mode" ]]; then
        ARGS_LIST+=("--interactive_mode")
    elif [[ $arg == "--background_mode" ]]; then
        BACKGROUND_MODE=true
    fi
done

if $VISUAL_MODE; then
    rm -f ./server/static/*
fi

if $BACKGROUND_MODE; then
    python ./scripts/main.py ${ARGS_LIST[@]} > /dev/null &

    if $VISUAL_MODE; then
        python ./server/app.py > /dev/null &
    fi
else
    if $VISUAL_MODE; then
        python ./server/app.py &
        python ./scripts/main.py ${ARGS_LIST[@]}
        pkill -f ./server/app.py
    else
        python ./scripts/main.py ${ARGS_LIST[@]}
    fi
fi
