import BaseHTTPServer
import SocketServer
import sys
import getopt
import threading
import signal
import socket
import httplib
from time import sleep

httpdServeRequests = True
latencySkew = 10
latencyMultiplier = 10
consumer = None
lock = threading.Lock()
next = 0


def changeNext():
    global next
    lock.acquire()
    if next == 2:
        next = 0
    else:
        next += 1
    lock.release()


def tryServer():
    try:
        conn = httplib.HTTPConnection(frontend_ips[str(next)], int(frontend_feedback_ports[str(next)]))
        conn.request("GET", "")
        response = conn.getresponse()
        if response.status == 200:
            return next;
        elif response.status == 500:
            changeNext()
            return next
    except:
        changeNext()
        print "Unable to send GET request"
        return next


class FrontendHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        resp = tryServer()
        if resp == 0:
            self.send_response(200)
        elif resp == 1:
            self.send_response(201)
        else:
            self.send_response(202)
        self.send_header("Content-type", "application/octet-stream")
        self.end_headers()
        # print (resp)
        # self.wfile.write(frontend_ips[resp] +":" + str(frontend_ports[resp]))
        # self.wfile.close()


class LoadBalancer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    def server_bind(self):
        BaseHTTPServer.HTTPServer.server_bind(self)
        self.socket.settimeout(1000)
        self.run = True

    def get_request(self):
        while self.run == True:
            try:
                sock, addr = self.socket.accept()
                sock.settimeout(1000)
                return (sock, addr)
            except socket.timeout:
                if not self.run:
                    raise socket.error

    def stop(self):
        self.run = False

    def serve(self):
        while self.run == True:
            self.handle_request()


if __name__ == '__main__':
    global frontend_feedback_ports
    global frontend_ips
    global frontend_ports
    httpserver_port = 7000

    frontend_feedback_ports = {};
    frontend_feedback_ports['0'] = 5000
    frontend_feedback_ports['1'] = 5000
    frontend_feedback_ports['2'] = 5000

    frontend_ports = {};
    frontend_ports['0'] = 4000
    frontend_ports['1'] = 4000
    frontend_ports['2'] = 4000

    frontend_ips = {};
    frontend_ips['0'] = "tile-2-0"
    frontend_ips['1'] = "tile-3-0"
    frontend_ips['2'] = "tile-4-0"

    try:
        httpd = LoadBalancer(("", httpserver_port), FrontendHttpHandler)
        server_thread = threading.Thread(target=httpd.serve)
        server_thread.daemon = True
        server_thread.start()


        def handler(signum, frame):
            print "Stopping http server..."
            httpd.stop()


        signal.signal(signal.SIGINT, handler)

    except:
        print "Error: unable to http server thread"

    # Wait for server thread to exit
    server_thread.join(100)

    httpd.stop()

