import dns.exception
import dns.resolver
import dns.reversename

def get_record(hostname, record_type="A"):
    """Returns the first record, or None, of the requested type."""
    try:
        resp = dns.resolver.query(hostname, record_type)
        return resp[0].to_text()
    except (dns.resolver.NXDOMAIN, dns.exception.SyntaxError, IndexError):
        return None

def get_ip(hostname):
    """Returns IP address for hostname. IPv4 only (for now!)."""
    return get_record(hostname, record_type="A")


def get_reverse_dns(ip):
    """Returns reverse DNS record for IP, if it exists."""
    try:
        arpa = dns.reversename.from_address(ip)
    except dns.exception.SyntaxError:
        return None

    record = get_record(arpa, "PTR")

    # remove trailing dot
    if record:
        return record[:-1]
