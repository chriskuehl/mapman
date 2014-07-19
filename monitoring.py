#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
import os
import socket

import rackspace_monitoring.providers
import rackspace_monitoring.types

import network
import scan


MAX_WORKERS = 100
DEFAULT_MONITORING_ZONES = \
    ("mzdfw", "mzord", "mziad", "mzlon", "mzhkg", "mzsyd")


def get_driver(user, api_key):
    """Returns an instantiated driver."""
    cls = rackspace_monitoring.providers.get_driver(
        rackspace_monitoring.types.Provider.RACKSPACE)
    return cls(user, api_key)


def delete_all_entities(driver_gen, max_workers=MAX_WORKERS):
    """Deletes all entities from the account."""
    def delete(entity):
        entity.driver = driver_gen()
        entity.delete()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for entity in driver_gen().list_entities():
            executor.submit(delete, (entity,))


def create_entity(driver, hostname):
    """Creates entity with given hostname, returning the new entity."""
    try:
        ip = network.get_ip(hostname)
    except socket.gaierror:
        raise NameError(
            "Unable to resolve hostname `{}` with IPv4".format(hostname))

    return driver.create_entity(
        ip_addresses={"main": ip},
        label=hostname)

def create_entities(driver_gen, hostnames, max_workers=MAX_WORKERS):
    create = lambda hostname: create_entity(driver_gen(), hostname)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(create, hostnames))

def create_checks(driver, entity, checks):
    for check in checks:
        driver.create_check(entity,
            label=check["label"],
            type=check["name"],
            details=check["details"],
            monitoring_zones=DEFAULT_MONITORING_ZONES,
            target_alias="main")
