import dns.resolver


def get_ip(hostname):
    """Returns IP address for hostname. IPv4 only (for now!)."""
    try:
        resp = dns.resolver.query(hostname, "A")
        return resp[0].address
    except (dns.resolver.NXDOMAIN, IndexError):
        return None


def get_reverse_dns(ip, timeout=2):
    """Returns reverse DNS record for IP, if it exists."""
    try:
        socket.setdefaulttimeout(timeout)
        result = socket.gethostbyaddr(ip)
    except socket.herror:
        raise NameError("Unable to resolve IP `{}` to PTR".format(ip))
