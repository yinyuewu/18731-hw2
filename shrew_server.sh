#qsize=$1
echo set iperf-server

#TODO: add your code
iperf -s -u -p 5003 -t 1 &