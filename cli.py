#!/usr/bin/env python3

import json
import sys

import checks
import monitoring
import network
import parallel
import scan

def main():
    user = input("Enter Rackspace username: ")
    api_key = input("Enter API Key: ")
    driver_gen = lambda: monitoring.get_driver(user, api_key)

    if confirm("Remove all existing entities from monitoring?"):
        print("Removing existing entities...")
        monitoring.delete_all_entities(driver_gen)
        print("Existing entities removed.")

    network = input("Enter network to scan (CIDR-style): ")
    print("Scanning network {} for hosts...".format(network))

    hosts = list(scan.get_hosts("169.229.10.0/24"))

    print("Found {} hosts:".format(len(hosts)))

    for host in hosts:
        print("- {} ({})".format(host["hostname"], host["ip"]))

    if not confirm("Add {} hosts as entities to monitoring?".format(
        len(hosts)), default=True):
        sys.exit(0)

    monitoring.create_entities(driver_gen,
        [host["hostname"] for host in hosts])

    entities = {entity.label.lower(): entity for entity \
        in driver_gen().list_entities()}

    print("Added {} entities to monitoring.".format(len(hosts)))

    if not confirm("Proceed to service scan of hosts?", default=True):
        sys.exit(0)

    ips = [host["ip"] for host in hosts]
    open_ports = scan.get_open_ports(ips)
    total_open = sum(len(ports) for ports in open_ports.values())

    print("Found the following open ports:")

    for ip in ips:
        print("- {}: {}".format(ip, open_ports[ip]))

    print("Total: {} open ports found (across {} hosts)".format(
        total_open, len(hosts)))

    host_checks = []

    for host in hosts:
        ip, hostname = host["ip"], host["hostname"]
        entity = entities[hostname.lower()]
        ports = open_ports[ip]

        if not entity or not ports:
            continue


        checks_list = list(checks.get_checks_for_host(hostname, ip, ports))
        host_checks.append([ip, hostname, checks_list, entity])

    total_checks = sum(len(p[2]) for p in host_checks)

    print("We can automatically add {} checks.".format(total_checks))

    if not confirm("Review checks?", default=True):
        sys.exit(0)


    for ip, hostname, checks_list, entity in host_checks:
        print("{} ({})".format(hostname, ip))

        for check in checks_list:
            details = json.dumps(check["details"])
            print("- {}({})".format(check["label"], details))

        print()

    if not confirm("Add these checks automatically?", default=True):
        sys.exit(0)

    p = parallel.Parallel()

    for ip, hostname, checks_list, entity in host_checks:
        def create(ip=ip, hostname=hostname, checks_list=checks_list, entity=entity):
            monitoring.create_checks(driver_gen(), entity, checks_list)
            print("- created checks: {}".format(hostname))

        p.start(create)

    p.wait()
    print("Checks added! Enjoy :-)")


def confirm(prompt="Continue?", default=False):
    choices = "Yn" if default else "yN"
    response = input("{} [{}] ".format(prompt, choices)).lower()

    if response in ("y", "yes"):
        return True

    if response in ("n", "no"):
        return False

    return default

if __name__ == "__main__":
    main()
