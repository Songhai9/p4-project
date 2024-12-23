from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()
net.setLogLevel('info')

# Add switches without cli_input since we will use a control plane script
net.addP4Switch('s1')
net.addP4Switch('s2')
net.addP4Switch('s3')
net.addP4Switch('s4')
net.addP4Switch('s5')
net.addP4Switch('s6')

net.setP4SourceAll('../simple_router.p4')

# Add hosts
for i in range(1, 13):
    net.addHost(f'h{i}')

# Host to switch links
net.addLink('h1', 's1', port2=1)
net.addLink('h2', 's1', port2=2)

net.addLink('h3', 's2', port2=1)
net.addLink('h4', 's2', port2=2)

net.addLink('h5', 's3', port2=1)
net.addLink('h6', 's3', port2=2)

net.addLink('h7', 's4', port2=1)
net.addLink('h8', 's4', port2=2)

net.addLink('h9', 's5', port2=1)
net.addLink('h10', 's5', port2=2)

net.addLink('h11', 's6', port2=1)
net.addLink('h12', 's6', port2=2)

# Switch to switch links with assigned ports
net.addLink('s1', 's4', port1=3, port2=3)
net.addLink('s1', 's5', port1=4, port2=3)
net.addLink('s1', 's2', port1=5, port2=3)

net.addLink('s2', 's5', port1=4, port2=4)
net.addLink('s2', 's6', port1=5, port2=3)

net.addLink('s3', 's4', port1=3, port2=4)
net.addLink('s3', 's5', port1=4, port2=5)
net.addLink('s3', 's6', port1=5, port2=4)

net.addLink('s4', 's5', port1=5, port2=6)
net.addLink('s5', 's6', port1=7, port2=5)

net.mixed()

net.disablePcapDumpAll()
net.disableLogAll()
net.enableCli()
net.startNetwork() 