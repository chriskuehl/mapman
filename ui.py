#!/usr/bin/env python3

import http.server


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
            self.wfile.write(self.path.encode("utf-8"))


def main():
    bind = "0.0.0.0", 8000
    httpd = http.server.HTTPServer(bind, RequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
