#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
import socket

import rackspace_monitoring.providers
import rackspace_monitoring.types

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
