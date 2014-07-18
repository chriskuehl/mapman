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
            print("done: {}".format(hostname))

        p.start(create)

    p.wait()

def create_checks(driver, entity, checks):
    print("Creating checks for " + entity.label)

    for check in checks:
        print("Creating check: " + check["label"])
        driver.create_check(entity,
            label=check["label"],
            type=check["name"],
            details=check["details"],
            monitoring_zones=DEFAULT_MONITORING_ZONES,
            target_alias="main")

    print("Done creating checks for " + entity.label)


class Test:
    pass

def main():
    # prepare driver
    user, api_key = (os.environ.get("RAX_" + key) for key in ("USER", "KEY"))
    driver_gen = lambda: get_driver(user, api_key)
    driver = driver_gen()


    entity = driver.list_entities()[0]
    checks_list = checks.get_checks_for_host(entity.label, network.get_ip(entity.label), [22, 80, 443, 999])

    create_checks(driver, entity, checks_list)

    return 0

    driver.create_check(entity,
        label="foo",
        type="remote.tcp",
        details={"port": 22},
        monitoring_zones=("mzdfw", "mzord"),
        target_alias="main"
    )


    return 0

    print("deleting...")
    delete_all_entities(driver_gen)

    print("creating...")
    test_hostnames = [host["hostname"] for host in \
        scan.get_hosts("169.229.10.0/24")]
    create_entities(driver_gen, test_hostnames)

if __name__ == '__main__':
    main()
