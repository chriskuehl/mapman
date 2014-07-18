#!/usr/bin/env python3
import nmap

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

def get_services(hosts):
    """Returns a list of services for the specified list of IP hosts (given as
    IP addresses)."""
    pass

def main():
    for host in get_hosts("169.229.10.0/24"):
        print(host)

if __name__ == "__main__":
    main()
