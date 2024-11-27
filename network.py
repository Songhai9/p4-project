from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# Options générales du réseau
net.setLogLevel('info')

# Définition du réseau
net.addP4Switch('s1', cli_input='s1-commands.txt')
net.addP4Switch('s2', cli_input='s2-commands.txt')
net.addP4Switch('s3', cli_input='s3-commands.txt')
net.setP4SourceAll('simple_router.p4')

# Ajout des hôtes
net.addHost('h1')
net.addHost('h2')
net.addHost('h3')

# Création des liens
net.addLink("h1", "s1", port2=1)
net.addLink("h2", "s2", port2=1)
net.addLink("h3", "s3", port2=1)
net.addLink("s1", "s2", port1=2, port2=2)
net.addLink("s2", "s3", port1=3, port2=2)
net.addLink("s3", "s1", port1=3, port2=3)

# Stratégie d'assignation
net.mixed()

# Options générales des nœuds
net.disablePcapDumpAll()
net.disableLogAll()
net.enableCli()
net.startNetwork()