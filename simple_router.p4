#include <core.p4>
#include <v1model.p4>

// ==========================================================
// 1) Headers
// ==========================================================

// Ethernet
header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

// IPv4
header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;       // On utilise ce champ pour détecter la présence du header waypoint
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

// Waypoint header (après IPv4 si protocol=0xFD)
header waypoint_t {
    bit<8>  total_waypoints;  // Nombre total de waypoints
    bit<8>  next_idx;         // Index du waypoint courant
    bit<32> w1;               // Waypoint #1 (adresse IP du waypoint #1)
    bit<32> w2;               // Waypoint #2 (adresse IP du waypoint #2)
    // Ajoutez plus de champs si vous voulez plus de waypoints
}

// Structs
struct metadata {
    /* empty */
}

struct headers {
    ethernet_t ethernet;
    ipv4_t     ipv4;
    waypoint_t waypoint;   // On ajoute ce header
}

// ==========================================================
// 2) Parser
// ==========================================================
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata)
{
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x0800: parse_ipv4;    // IPv4
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            0xFD: parse_waypoint;  // Notre protocole "spécial" (0xFD) pour waypoint
            default: accept;
        }
    }

    state parse_waypoint {
        packet.extract(hdr.waypoint);
        transition accept;
    }
}

// ==========================================================
// 3) Checksum verification (vide ici)
// ==========================================================
control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

// ==========================================================
// 4) Ingress
// ==========================================================
control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata)
{
    // ---------- Actions ----------
    action drop() {
        mark_to_drop(standard_metadata);
    }

    // Action de forwarding normal IPv4
    action ipv4_forward(bit<48> dst_mac, bit<9> port) {
        hdr.ethernet.dstAddr = dst_mac;
        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    // Action de forwarding pour les paquets waypoint
    action waypoint_forward(bit<48> dst_mac, bit<9> port) {
        hdr.ethernet.dstAddr = dst_mac;
        standard_metadata.egress_spec = port;
        // Optionnel : on peut aussi décrémenter le TTL
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    // Action : incrémente l'index de waypoint
    //          Si on a atteint le dernier waypoint, on repasse en protocole "classique" (ex: 0x06 => TCP)
    action increment_waypoint_index() {
        hdr.waypoint.next_idx = hdr.waypoint.next_idx + 1;
        if (hdr.waypoint.next_idx >= hdr.waypoint.total_waypoints) {
            // On a fini tous les waypoints, on repasse en mode IPv4 normal
            hdr.ipv4.protocol = 0x06;  // Ex: 0x06 = TCP, ou 0x11 = UDP, selon votre usage
        }
    }

    // ---------- Tables ----------
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
        }
        size = 1024;
        default_action = drop();
    }

    table waypoint_table {
        // On match sur l'index de waypoint
        key = {
            hdr.waypoint.next_idx: exact;
        }
        actions = {
            waypoint_forward;
            increment_waypoint_index;
            drop;
        }
        size = 32;
        default_action = drop();
    }

    apply {
        // 1) Vérifier si IPv4 est valide
        if (!hdr.ipv4.isValid()) {
            drop();
            return;
        }

        // 2) Si c'est un paquet waypoint (protocol=0xFD), on applique la table waypoint_table
        if (hdr.waypoint.isValid() && hdr.ipv4.protocol == 0xFD) {
            waypoint_table.apply();
        }
        // 3) Sinon, routage IPv4 normal
        else {
            ipv4_lpm.apply();
        }
    }
}

// ==========================================================
// 5) Egress
// ==========================================================
control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply { }
}

// ==========================================================
// 6) ComputeChecksum
// ==========================================================
control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {
        // Recalcule le checksum IPv4
        update_checksum(
            hdr.ipv4.isValid(),
            {
                hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.diffserv,
                hdr.ipv4.totalLen,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.fragOffset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr
            },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16
        );
    }
}

// ==========================================================
// 7) Deparser
// ==========================================================
control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.waypoint);  // On émet le header s’il est valid, sinon rien
    }
}


// ==========================================================
// 8) V1Switch instantiation
// ==========================================================
V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
