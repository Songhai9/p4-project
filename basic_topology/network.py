from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()
net.setLogLevel('info')

# Configuration du réseau
net.addP4Switch('s1', cli_input='s1-commands.txt')
net.addP4Switch('s2', cli_input='s2-commands.txt')
net.setP4SourceAll('../simple_router.p4')

net.addHost('h1')
net.addHost('h2')

net.addLink("h1", "s1", port2=1)
net.addLink("s1", "s2", port1=2, port2=2)
net.addLink("s2", "h2", port1=1)

net.mixed()

net.disablePcapDumpAll()
net.disableLogAll()
net.enableCli()
net.startNetwork()
