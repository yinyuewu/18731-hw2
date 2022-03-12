#!/bin/bash 

echo running iperf-client

ATTACK_PERIOD=1
BURST_DURATION=0.2
BURST_RATE="10M"
SLEEP_TIME=0.8 # $ATTACK_PERIOD - $BURST_DURATION

for i in {1..30}
do
    iperf -c 10.0.0.5 -u -p 5003 -t $BURST_DURATION -b $BURST_RATE
    sleep $SLEEP_TIME
done