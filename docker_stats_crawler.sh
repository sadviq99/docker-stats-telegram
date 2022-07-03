#!/bin/bash

# How often save the data
TIMER=60

# Remove abandoned files
rm -f /tmp/dockerstats /tmp/dockerstats.csv

# Remove orphan processes if any
kill -9 $(ps -ef | grep 'bash /dev/fd' | grep -v grep | grep -v $$ | awk '{print $2}')

# Save docker stats every $TIMER seconds while containers are running
while [ $(docker ps -q | wc -l) -gt 0 ]; do
    docker stats --no-stream --format "table {{.Name}};{{.CPUPerc}};{{.MemPerc}};{{.NetIO}}" > /tmp/dockerstats
    tail -n +2 /tmp/dockerstats | awk -v date="$(date '+%Y-%m-%d %T')" -v ip=";$(curl -s ifconfig.me);" -v cpucount="$(nproc --all);" '{print date ip cpucount $0}' >> /tmp/dockerstats.csv
    sleep $TIMER
done
