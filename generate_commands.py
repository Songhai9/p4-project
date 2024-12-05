import json
import argparse
import os
from ipaddress import ip_address

def ip_to_mac(ip_str):
    parts = ip_str.split('.')
    return "00:00:%02x:%02x:%02x:%02x" % (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("topology", help="Path to the topology json file")
    args = parser.parse_args()

    topo_file = args.topology
    with open(topo_file, 'r') as f:
        topo = json.load(f)

    links = topo.get("links", [])
    hosts = topo.get("hosts", {})
    switches = topo.get("switches", {})

    adjacency = { n: [] for n in hosts.keys() }
    for s in switches.keys():
        adjacency[s] = []

    switch_port_map = { s: {} for s in switches.keys() }
    for link in links:
        # Updated to use dictionary format for links
        n1, n2 = link["node1"], link["node2"]
        if n1 in switches:
            if n2 not in switch_port_map[n1]:
                port_num = len(switch_port_map[n1]) + 1
                switch_port_map[n1][n2] = port_num
        if n2 in switches:
            if n1 not in switch_port_map[n2]:
                port_num = len(switch_port_map[n2]) + 1
                switch_port_map[n2][n1] = port_num

    host_ips = {}
    for i, h in enumerate(hosts.keys(), start=1):
        host_ip = f"10.0.{i}.{i}"
        host_ips[h] = host_ip

    if not os.path.exists("command_files"):
        os.makedirs("command_files")

    for s in switches.keys():
        cmd_file = f"command_files/{s}-commands.txt"
        with open(cmd_file, 'w') as out:
            out.write("table_set_default ipv4_lpm drop\n")
            for h, hip in host_ips.items():
                if h in switch_port_map[s]:
                    port = switch_port_map[s][h]
                    mac = ip_to_mac(hip)
                    out.write(f"table_add ipv4_lpm ipv4_forward {hip}/32 => {mac} {port}\n")
                else:
                    neighbors = [n for n in switch_port_map[s].keys() if n.startswith('s')]
                    if neighbors:
                        next_hop = neighbors[0]
                        port = switch_port_map[s][next_hop]
                        mac = "00:00:0a:00:00:01"
                        out.write(f"table_add ipv4_lpm ipv4_forward {hip}/32 => {mac} {port}\n")
                    else:
                        pass

    print("Command files generated in command_files/")

if __name__ == "__main__":
    main()
