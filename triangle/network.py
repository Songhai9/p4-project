from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()
net.setLogLevel('info')

net.addP4Switch('s1')
net.addP4Switch('s2')
net.addP4Switch('s3')
net.setP4SourceAll('../simple_router.p4')

net.addHost('h1')
net.addHost('h2')
net.addHost('h3')

net.addLink('h1', 's1', port2=1)
net.addLink('s1', 's2', port1=2, port2=2)
net.addLink('s2', 'h2', port1=1)
net.addLink('s1', 's3', port1=3, port2=3)
net.addLink('s3', 'h3', port1=1)
net.addLink('s2', 's3', port1=4, port2=4)

net.mixed()

net.disablePcapDumpAll()
net.disableLogAll()
net.enableCli()
net.startNetwork()
