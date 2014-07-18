#!/usr/bin/env python3
import os
import socket

import rackspace_monitoring.providers
import rackspace_monitoring.types

import network


def get_driver(user, api_key):
    """Returns an instantiated driver."""
    cls = rackspace_monitoring.providers.get_driver(
        rackspace_monitoring.types.Provider.RACKSPACE)
    return cls(user, api_key)


def delete_all_entities(driver):
    """Deletes all entities from an account."""
    for entity in driver.list_entities():
        entity.delete()


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


def main():
    # prepare driver
    user, api_key = (os.environ.get("RAX_" + key) for key in ("USER", "KEY"))
    driver = get_driver(user, api_key)

    delete_all_entities(driver)
    create_entity(driver, "raptors.ocf.berkeley.edu")

    print(driver.list_entities())

if __name__ == '__main__':
    main()
