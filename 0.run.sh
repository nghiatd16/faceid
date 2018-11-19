#!/bin/bash
cd /home/tvlab/workspace/faceid
echo "Start service"
echo "Run \"tail -f logs/watch_dog.log\" to see log"
nohup ./1.watch_dog.sh &> logs/watch_dog.log &
