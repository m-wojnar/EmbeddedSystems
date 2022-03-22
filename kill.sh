#!/bin/bash

while read pid; do 
    kill -SIGINT $pid
done < pids

