# CMU 18731 HW2
# Code referenced from: git@bitbucket.org:huangty/cs144_bufferbloat.git
# Edited by: Soo-Jin Moon, Deepti Sunder Prakash

#!/usr/bin/python

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

import sys
import os

# Parse arguments

parser = ArgumentParser(description="Shrew tests")
parser.add_argument('--bw-host', '-B',
                    dest="bw_host",
                    type=float,
                    action="store",
                    help="Bandwidth of host links",
                    required=True)
parser.add_argument('--bw-net', '-b',
                    dest="bw_net",
                    type=float,
                    action="store",
                    help="Bandwidth of network link",
                    required=True)
parser.add_argument('--delay',
                    dest="delay",
                    type=float,
                    help="Delay in milliseconds of host links",
                    default='10ms')
parser.add_argument('--n',
                    dest="n",
                    type=int,
                    action="store",
                    help="Number of nodes in one side of the dumbbell.",
                    required=True)

parser.add_argument('--maxq',
                    dest="maxq",
                    action="store",
                    help="Max buffer size of network interface in packets",
                    default=1000)

# Expt parameters
args = parser.parse_args()

class DumbbellTopo(Topo):
    "Dumbbell topology for Shrew experiment"
    def build(self, n=6, bw_net=10, delay='20ms', bw_host=10, maxq=None):
        hl1 = self.addHost('hl1', ip='10.0.0.1')
        hr1 = self.addHost('hr1', ip='10.0.0.2' )
        hl2 = self.addHost('hl2', ip='10.0.0.3')
        hr2 = self.addHost('hr2', ip='10.0.0.4')
        a1 = self.addHost('a1', ip='10.0.0.5')
        a2 = self.addHost('a2', ip='10.0.0.6')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        self.addLink(hl1, s1, bw=bw_host, delay=delay, max_queue_size=maxq)
        self.addLink(hr1, s2, bw=bw_host, delay=delay, max_queue_size=maxq)
        self.addLink(hl2, s1, bw=bw_host, delay=delay, max_queue_size=maxq)
        self.addLink(hr2, s2, bw=bw_host, delay=delay, max_queue_size=maxq)
        self.addLink(a1, s1, bw=bw_host, delay=delay, max_queue_size=maxq)
        self.addLink(a2, s2, bw=bw_host, delay=delay, max_queue_size=maxq)
        self.addLink(s1, s2, bw=bw_net, delay=delay, max_queue_size=maxq)

def bbnet():
    "Create network and run shrew  experiment"
    print "starting mininet ...."
    topo = DumbbellTopo(n=args.n, bw_net=args.bw_net,
                    delay='%sms' % (args.delay),
                    bw_host=args.bw_host, maxq=int(args.maxq))

    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink,
                  autoPinCpus=True)
    net.start()
    dumpNodeConnections(net.hosts)

    ### test reachability
    net.pingAll()

    ### iperf
    hl1, hr1, hl2, hr2 = net.get('hl1', 'hr1', 'hl2', 'hr2')
    hl1.cmd('iperf -s -p 5001 -i 1 &')
    hl2.cmd('iperf -s -p 5002 -i 1 &')
    hr1.cmd('iperf -c %s -p 5001 -t 600 &' % hl1.IP())
    hr2.cmd('iperf -c %s -p 5002 -t 600 &' % hl2.IP())

    CLI(net)
    net.stop()

if __name__ == '__main__':
    bbnet()
