#!/usr/bin/env python3
"""
License: MIT License
Copyright (c) 2023 Miel Donkers

Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib, hmac, binascii, os
import logging
from pathlib import Path
import json

def hmac_sha256(msg):
    key = os.getenv('SECRET').encode('utf-8')
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


    def do_POST(self):
        signature = self.headers.get('X-Hub-Signature-256', '').replace('sha256=', '')
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        if self.path == '/githack' and hmac_sha256(post_data) == signature:
            logging.info("Valid signature")
            data = json.loads(post_data.decode('utf-8'))
            name = data['repository']['name']
            os.chdir(cwd / name)
            os.system('./update.sh')

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8555):
    logging.basicConfig(level=logging.INFO)
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv
    
    cwd = Path(__file__).absolute().parent

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()