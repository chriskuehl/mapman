#!/usr/bin/env python3

import cgi
import http.server
import json
import sys
import urllib.parse

import monitoring
import network
import parallel
import scan

driver_gen = None
all_hosts = {}
open_ports = {}

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def sane_request(self):
        """Very naive sanity checking."""
        return ".." not in self.path

    def do_HEAD(self):
        """Handles HEAD requests. Requests to static are passed to the
        superclass, other requests are 405 Method Not Allowed'd for
        simplicity."""
        if not self.sane_request():
            self.send_response(403)
            self.end_headers()
            return

        if self.path.startswith("/static/"):
            self.path = "/ui/" + self.path[len("/static"):]
            super().do_HEAD()
        else:
            self.send_response(405)
            self.end_headers()


    def do_GET(self):
        if not self.sane_request():
            self.send_response(403)
            self.end_headers()
            return

        if self.path.startswith("/static/"):
            self.path = "/ui/" + self.path[len("/static/"):]
            super().do_GET()
        else:
            parts = urllib.parse.urlparse(self.path)
            data = urllib.parse.parse_qs(parts.query)

            # remove query string
            self.path = self.path[:self.path.index("?")]

            if self.path == "/":
                # TODO: technically relative redirects are not allowed,
                # although ~all browsers accept them
                self.send_response(301)
                self.send_header("Location", "/static/index.html")
                self.end_headers()
            elif self.path == "/all-hosts":
                network = data["network"][0]

                if network in all_hosts:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()

                    self.wfile.write(json.dumps(all_hosts[network]).encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()

                    self.wfile.write("not ready yet".encode("utf-8"))
            elif self.path == "/open-ports":
                network = data["network"][0]

                if network in open_ports:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()

                    self.wfile.write(json.dumps(open_ports[network]).encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()

                    self.wfile.write("not ready yet".encode("utf-8"))


    def do_POST(self):
        if not self.sane_request():
            self.send_response(403)
            self.end_headers()
            return

        if self.path.startswith("/static/"):
            self.send_response(405)
            self.end_headers()
        else:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST",
                     "CONTENT_TYPE": self.headers.get("Content-Type")})

            if self.path == "/network":
                network = form["network"].value
                print(network)

                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write("starting scan".encode("ascii"))

                # start scan in the background
                def do_scan():
                    all_hosts[network] = list(scan.get_hosts(network))

                p = parallel.Parallel()
                p.start(do_scan)
            elif self.path == "/set-hosts":
                network = form["network"].value
                hosts = json.loads(form["hosts"].value)

                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write("starting scan".encode("ascii"))

                # add entities and start port scan in the background
                def do_scan():
                    print("Creating entities...")
                    monitoring.create_entities(driver_gen, hosts)
                    print("Done creating entities, starting port scan...")

                    ips = [network.get_ip(host) for host in hosts]
                    print("start open ports")
                    open_ports[network] = scan.get_open_ports(ips)
                    print("done open ports")

                p = parallel.Parallel()
                p.start(do_scan)


def main():
    global driver_gen

    if len(sys.argv) != 3: # todo: argparse
        print("syntax: {} username apikey".format(sys.argv[0]),
            file=sys.stderr)
        sys.exit(1)

    user, api_key = sys.argv[1:]
    driver_gen = lambda: monitoring.get_driver(user, api_key)

    print("Initialized with username `{}` and API key.".format(user))
    print("Now listening on http://localhost:8000/")

    bind = "0.0.0.0", 8000
    httpd = http.server.HTTPServer(bind, RequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
