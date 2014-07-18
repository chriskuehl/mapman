#!/usr/bin/env python3
import os
import socket

import rackspace_monitoring.base
import rackspace_monitoring.providers
import rackspace_monitoring.types

import checks
import network
import parallel
import scan


DEFAULT_MONITORING_ZONES = \
    ("mzdfw", "mzord", "mziad", "mzlon", "mzhkg", "mzsyd")


def get_driver(user, api_key):
    """Returns an instantiated driver."""
    cls = rackspace_monitoring.providers.get_driver(
        rackspace_monitoring.types.Provider.RACKSPACE)
    return cls(user, api_key)


def delete_all_entities(driver_gen):
    """Deletes all entities from an account."""
    p = parallel.Parallel()

    for entity in driver_gen().list_entities():
        def delete(entity=entity):
            entity.driver = driver_gen()
            entity.delete()

        p.start(delete)

    p.wait()


def create_entity(driver, hostname):
    """Creates entity with given hostname and IP."""
    try:
        ip = network.get_ip(hostname)
    except socket.gaierror:
        raise NameError(
            "Unable to resolve hostname `{}` with IPv4".format(hostname))

    driver.create_entity(
        ip_addresses={"main": ip},
        label=hostname)

def create_entities(driver_gen, hostnames):
    p = parallel.Parallel()

    for hostname in hostnames:
        def create(hostname=hostname):
            driver = driver_gen()
            create_entity(driver, hostname)
            print("- added: {}".format(hostname))

        p.start(create)

    p.wait()

def create_checks(driver, entity, checks):
    for check in checks:
        driver.create_check(entity,
            label=check["label"],
            type=check["name"],
            details=check["details"],
            monitoring_zones=DEFAULT_MONITORING_ZONES,
            target_alias="main")

def poc_addall(driver_gen):
    # remove existing entities
    print("Removing existing entities...")
    delete_all_entities(driver_gen)

    # get hosts and open ports
    print("Finding hosts, adding entities...")
    hosts = scan.get_hosts("169.229.10.0/24")
    ips = [host["ip"] for host in hosts]
    open_ports = scan.get_open_ports(ips)

    # filter out hosts with no open ports
    ips = list(filter(lambda ip: open_ports.get(ip, []), ips))

    host_pairs = [[ip, network.get_reverse_dns(ip)] for ip in ips]

    # add new entities
    create_entities(driver_gen, list(zip(*host_pairs))[1])

    # build map of label -> entity
    entities = {entity.label.lower(): entity for entity \
        in driver_gen().list_entities()}

    # add checks for entities
    p = parallel.Parallel()

    for ip, hostname in host_pairs:
        entity = entities[hostname.lower()]
        ports = open_ports[ip]

        if not entity or not ports:
            continue

        def create(ip=ip, hostname=hostname, ports=ports, entity=entity):
            checks_list = checks.get_checks_for_host(hostname, ip, ports)
            create_checks(driver_gen(), entity, checks_list)

        p.start(create)

    p.wait()


def main():
    # prepare driver generator
    user, api_key = (os.environ.get("RAX_" + key) for key in ("USER", "KEY"))
    driver_gen = lambda: get_driver(user, api_key)

    poc_addall(driver_gen)


if __name__ == '__main__':
    main()
