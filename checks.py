class CheckSSH():
    name = "remote.ssh"
    label = "SSH"

    def default_details(hostname, ip, port):
        return {"port": port}

class CheckHTTP():
    name = "remote.http"
    label = "HTTP"

    def default_details(hostname, ip, port):
        s = "s" if port == 443 else ""
        return {
            "method": "GET",
            "url": "http{}://{}/".format(s, hostname.lower())
        }

class CheckPing():
    name = "remote.ping"
    label = "ICMP Ping"

    def default_details(hostname, ip):
        return {"count": 5}

class CheckTCP():
    name = "remote.tcp"
    label = "Generic TCP"

    def default_details(hostname, ip, port):
        return {"port": port}

checks_by_port = {
    22: CheckSSH,
    80: CheckHTTP,
    443: CheckHTTP
}

checks_by_name = {check.name: check for check in checks_by_port.values()}

for check in (CheckPing,):
    checks_by_name[check.name] = check

def get_check_for_port(hostname, ip, port):
    check = checks_by_port.get(port, CheckTCP)

    return {
        "name": check.name,
        "label": check.label,
        "details": check.default_details(hostname, ip, port)
    }

def get_checks_for_host(hostname, ip, open_ports):
    # start with just ping check
    yield {
        "name": CheckPing.name,
        "label": CheckPing.label,
        "details": CheckPing.default_details(hostname, ip)
    }

    for port in open_ports:
        yield get_check_for_port(hostname, ip, port)
