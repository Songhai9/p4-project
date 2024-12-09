#!/usr/bin/env python3
from p4utils.mininetlib.network_API import NetworkAPI
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
import networkx as nx
from p4utils.utils.helper import load_topo

class SimpleRouterController(object):
    def __init__(self):
        """Initialise le contrôleur avec la topologie et les connexions aux switches."""
        self.topo = load_topo('topology.json')
        self.controllers = {}
        self.connect_to_switches()
        self.reset_states()
        self.set_table_defaults()

    def connect_to_switches(self):
        """Établit les connexions Thrift avec tous les switches P4."""
        for p4switch in self.topo.get_p4switches():
            thrift_port = self.topo.get_thrift_port(p4switch)
            self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)

    def reset_states(self):
        """Réinitialise l'état de tous les switches."""
        [controller.reset_state() for controller in self.controllers.values()]

    def set_table_defaults(self):
        """Configure les actions par défaut des tables."""
        for controller in self.controllers.values():
            controller.table_set_default("ipv4_lpm", "drop", [])

    def compute_shortest_paths(self):
        """Calcule les chemins les plus courts entre tous les hôtes."""
        G = nx.Graph()
        for link in self.topo.edges():
            G.add_edge(link[0], link[1])

        self.shortest_paths = {}
        hosts = self.topo.get_hosts()
        for src_host in hosts:
            for dst_host in hosts:
                if src_host != dst_host:
                    path = nx.shortest_path(G, src_host, dst_host)
                    self.shortest_paths[(src_host, dst_host)] = path


    def install_forwarding_rules(self):
        """Installe les règles de transfert basées sur les chemins les plus courts."""
        for (src_host, dst_host), path in self.shortest_paths.items():
            dst_ip = self.topo.get_host_ip(dst_host).split('/')[0]  # Retire le masque
            
            # Pour chaque segment du chemin
            for i in range(len(path)-1):
                current_node = path[i]
                next_hop = path[i+1]

                # On ne programme des règles que sur les nœuds P4 (switches)
                if self.topo.isP4Switch(current_node):
                    controller = self.controllers[current_node]

                    # Obtenir le port de sortie
                    out_port = self.topo.node_to_node_port_num(current_node, next_hop)

                    # Déterminer la MAC du prochain saut
                    if self.topo.isHost(next_hop):
                        # Si le prochain nœud est un hôte
                        next_hop_mac = self.topo.get_host_mac(next_hop)
                    else:
                        # Si le prochain nœud est un switch
                        next_hop_mac = self.topo.node_to_node_mac(current_node, next_hop)

                    # Installer la règle de transfert
                    controller.table_add(
                        "ipv4_lpm",
                        "ipv4_forward",
                        [f"{dst_ip}/32"],
                        [next_hop_mac, str(out_port)]
                    )


    def route(self):
        """Configure le routage pour l'ensemble du réseau."""
        self.compute_shortest_paths()
        self.install_forwarding_rules()

if __name__ == '__main__':
    controller = SimpleRouterController()
    controller.route() 