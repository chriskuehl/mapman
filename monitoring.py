#!/usr/bin/env python3
import os
import socket

import rackspace_monitoring.base
import rackspace_monitoring.providers
import rackspace_monitoring.types

import network
import parallel
import scan


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
            print("done: {}".format(hostname))

        p.start(create)

    p.wait()

def main():
    # prepare driver
    user, api_key = (os.environ.get("RAX_" + key) for key in ("USER", "KEY"))
    driver_gen = lambda: get_driver(user, api_key)
    driver = driver_gen()

    print("deleting...")
    delete_all_entities(driver_gen)

    print("creating...")
    test_hostnames = [host["hostname"] for host in \
        scan.get_hosts("169.229.10.0/24")]
    create_entities(driver_gen, test_hostnames)

if __name__ == '__main__':
    main()
