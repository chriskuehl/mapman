#!/usr/bin/env python3
import nmap

import network

def get_hosts(network):
    """Returns a list of hosts on the network. The parameter network is
    CIDR-style network string (e.g. "169.229.10.0/24").

    Returned values are dicts with keys hostname, ip, and vendor. The only
    value guaranteed to exist is ip."""

    nm = nmap.PortScanner()
    nm.scan(network, arguments="-sn")

    for host in nm.all_hosts():
        details = nm[host]

        if "ipv4" not in details["addresses"]:
            continue

        vendor = details.get("vendor")
        vendor_name = None

        if vendor and len(vendor) > 0:
            vendor_name = list(vendor.values())[0]

        yield {
            "hostname": details.get("hostname"),
            "ip": details["addresses"]["ipv4"],
            "vendor": vendor_name
        }


def get_open_ports(hosts):
    """Returns a list of open ports for the specified list of IP hosts (given as
    IP addresses)."""

    nm = nmap.PortScanner()
    nm.scan(", ".join(hosts), arguments="--top-ports 50 -sT")

    def open_ports(host):
        """Returns list of open ports for given host."""
        tcp = nm[host].get("tcp", {})
        return filter(lambda port: tcp[port]["state"] == "open", tcp)

    return {host: open_ports(host) for host in nm.all_hosts()}


def main():
    test_hosts = [host["ip"] for host in get_hosts("169.229.10.0/24")]
    #test_hosts = ["169.229.10.200", "169.229.10.25", "169.229.10.2"]

    for host, ports in get_open_ports(test_hosts).items():
        print("{}: {}".format(network.get_reverse_dns(host), list(ports)))

if __name__ == "__main__":
    main()
