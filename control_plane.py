#!/usr/bin/env python3

import networkx as nx
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI

class SimpleRouterController(object):

    def __init__(self, topo_file='topology.json'):
        # Charge la topologie
        self.topo = load_topo(topo_file)
        # Dictionnaire "nom_switch" -> "API Thrift"
        self.controllers = {}
        self.connect_to_switches()

        self.reset_states()
        self.set_table_defaults()

        # Contiendra les chemins calculés
        self.shortest_paths = {}

    def connect_to_switches(self):
        """Établit les connexions Thrift avec tous les switches P4 de la topologie."""
        for sw_name in self.topo.get_p4switches():
            thrift_port = self.topo.get_thrift_port(sw_name)
            self.controllers[sw_name] = SimpleSwitchThriftAPI(thrift_port)

    def reset_states(self):
        """Reset l'état de chaque switch (efface tables, compteurs, etc.)."""
        for api in self.controllers.values():
            api.reset_state()

    def set_table_defaults(self):
        """
        Définir les actions par défaut pour les tables.
        - ipv4_lpm => drop
        - waypoint_table => drop
        """
        for api in self.controllers.values():
            api.table_set_default("ipv4_lpm", "drop", [])
            api.table_set_default("waypoint_table", "drop", [])

    def compute_shortest_paths(self):
        """Calcule tous les plus courts chemins (basé sur networkx)"""
        G = nx.Graph()
        # Ajouter tous les liens de la topologie
        for (node1, node2) in self.topo.edges():
            G.add_edge(node1, node2)

        hosts = self.topo.get_hosts()
        for src_host in hosts:
            for dst_host in hosts:
                if src_host != dst_host:
                    path = nx.shortest_path(G, src_host, dst_host)
                    self.shortest_paths[(src_host, dst_host)] = path

    def install_forwarding_rules(self):
        """
        Installe les règles de routage IP normal (table ipv4_lpm)
        pour assurer la connectivité de base entre tous les hôtes.
        """
        for (src_host, dst_host), path in self.shortest_paths.items():
            dst_ip = self.topo.get_host_ip(dst_host).split('/')[0]
            # Parcourir les segments du chemin
            for i in range(len(path) - 1):
                current_node = path[i]
                next_node    = path[i + 1]

                # On ne programme que si le "current_node" est un switch
                if self.topo.isP4Switch(current_node):
                    out_port = self.topo.node_to_node_port_num(current_node, next_node)

                    # MAC du prochain saut
                    if self.topo.isHost(next_node):
                        next_mac = self.topo.get_host_mac(next_node)
                    else:
                        next_mac = self.topo.node_to_node_mac(current_node, next_node)

                    self.controllers[current_node].table_add(
                        table_name="ipv4_lpm",
                        action_name="ipv4_forward",
                        match_keys=[f"{dst_ip}/32"],
                        action_params=[next_mac, str(out_port)]
                    )

    # =========================================================================
    # ========== Partie Waypoint : installation de règles waypoint_table ======
    # =========================================================================

    def install_waypoint_forward(self, switch_name, next_idx_value, dst_mac, out_port):
        """
        Installe une règle dans "waypoint_table":
           Match:  hdr.waypoint.next_idx = next_idx_value
           Action: waypoint_forward(dst_mac, out_port)
        """
        self.controllers[switch_name].table_add(
            "waypoint_table",
            "waypoint_forward",
            [str(next_idx_value)],
            [dst_mac, str(out_port)]
        )

    def install_waypoint_increment(self, switch_name, next_idx_value):
        """
        Installe une règle dans "waypoint_table":
           Match:  hdr.waypoint.next_idx = next_idx_value
           Action: increment_waypoint_index()
        => À utiliser sur le switch "waypoint effectif".
        """
        self.controllers[switch_name].table_add(
            "waypoint_table",
            "increment_waypoint_index",
            [str(next_idx_value)],
            []
        )

    def example_waypoint_config(self):
        """
        Exemple minimal : 
        - Sur s1, si next_idx=0 => forward vers s2
        - Sur s2, si next_idx=0 => increment l'index
          (ce qui fera passer le protocole en normal si total_waypoints=1)

        Adaptez selon vos besoins réels.
        """
        # Sur s1, on forward quand next_idx=0 => (MAC de s2, port s1->s2)
        s1_s2_port = self.topo.node_to_node_port_num("s1", "s2")
        s1_s2_mac  = self.topo.node_to_node_mac("s1", "s2")

        self.install_waypoint_forward(
            switch_name="s1",
            next_idx_value=0,
            dst_mac=s1_s2_mac,
            out_port=s1_s2_port
        )

        # Sur s2, si next_idx=0 => on increment 
        # (on suppose que s2 est le waypoint effectif)
        self.install_waypoint_increment("s2", 0)

    # =========================================================================

    def run(self):
        """
        Lance la configuration globale:
          1) Calcule les plus courts chemins
          2) Installe le routage IP normal
          3) (Optionnel) Installe des règles waypoint (exemple)
        """
        self.compute_shortest_paths()
        self.install_forwarding_rules()

        # Décommentez si vous voulez tester l'exemple minimal :
        # self.example_waypoint_config()


if __name__ == "__main__":
    controller = SimpleRouterController()
    controller.run()
    print("Configuration terminée !")
