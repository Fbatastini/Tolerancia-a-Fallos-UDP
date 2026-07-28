#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.cli import CLI

def run_topology():
    net = Mininet(controller=OVSController, link=TCLink)
    net.addController('c0')

    host_1 = net.addHost('h1', ip='10.0.0.1')
    host_2 = net.addHost('h2', ip='10.0.0.2')
    switch = net.addSwitch('s1')

    net.addLink(host_1, switch, loss=10)
    net.addLink(host_2, switch)

    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run_topology()
