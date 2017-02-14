import BaseHTTPServer
import SocketServer
import sys
import getopt
import threading
import signal
import socket
import httplib
import random
from time import  time, sleep
import pygame
from pygame.locals import *

httpdServeRequests = True
latencySkew = 10
latencyMultiplier = 10
threadCount =0
timeout =100.0
prevTimeOutTime= 0
minute = 1000 * 60
timeoutCount =0
compute_resource_ip=""
compute_resource_port =0
white = (255,255,255)
green = (0,128,0)

lock  = threading.Lock()
pygame.init()
DISPLAY=pygame.display.set_mode((1200,1200),0,32)
DISPLAY.fill(white)


def onNewRequest():
    global  threadCount
    lock.acquire()
    threadCount += 1
    lock.release()

class FrontendHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        global  threadCount
        onNewRequest()
        print ("time out bound is" + str(timeout))
        start = getTime()
        resp= self.sendGET()
        print ("response time" + str(getTime() -start))
        threadCount -=1
        if resp != -1:
            self.send_response(200)
        else:
            self.send_response(500)

        self.send_header("Content-type", "application/octet-stream")
        self.end_headers()
        #self.wfile.write(resp)
        #self.wfile.close()i
        updateReq("Hello")
        updateReq("Request Count : " + str(threadCount)+ " ")
        #pygame.display.update()

    def sendGET(self):
        global  timeout,timeoutCount,prevTimeOutTime
        try:
            conn = httplib.HTTPConnection(compute_resource_ip, compute_resource_port,timeout=timeout/1000)
            conn.request("GET","")
            response = conn.getresponse()
            if response.status == 200:
                if timeout > 500.0 :
                    timeout -=30
                    #updateTimeOut("")
                    #updateTimeOut("Timeout :" + str(timeout))
                return 1

        except socket.timeout:
            print ("return time out " + str(timeoutCount))
            if timeout < 3000.0 :
                timeout += 100
                #updateTimeOut("")
                updateReq("Request Count : " + str(timeout))

            return -1

        except :
            print "Unable to send GET request"
            return -1


def getTime():

    return int(round(time() * 1000))

#font = pygame.font.SysFont(None,25)

def updateReq(msg):

    font = pygame.font.Font(None, 36)
    text = font.render(msg +"          timeout"+str(timeout), True,green)
    #textpos = text.get_rect()
    #textpos.centerx = background.get_rect().centerx
    DISPLAY.fill(white)
    DISPLAY.blit(text, [400,400])
    pygame.display.update()


def updateTimeOut(msg):

    font = pygame.font.Font(None, 36)
    text = font.render(msg, True,green)
                #textpos = text.get_rect()
                #textpos.centerx = background.get_rect().centerx
    DISPLAY.fill(white)            
    DISPLAY.blit(text, [400,600])
    pygame.display.update()


class FrontEnd(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):

    def server_bind(self):
        BaseHTTPServer.HTTPServer.server_bind(self)
        self.socket.settimeout(100)
        self.run = True

    def get_request(self):
        while self.run == True:
            try:
                sock, addr = self.socket.accept()
                sock.settimeout(100)
                return (sock, addr)
            except socket.timeout:
                print ("timeout")
                if not self.run:
                    raise socket.error

    def stop(self):
        self.run = False

    def serve(self):
        while self.run == True:
            self.handle_request()



class FrontEndFeedBackServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):

    def server_bind(self):
        BaseHTTPServer.HTTPServer.server_bind(self)
        self.socket.settimeout(100)
        self.run = True

    def get_request(self):
        while self.run == True:
            try:
                sock, addr = self.socket.accept()
                sock.settimeout(100)
                return (sock, addr)
            except socket.timeout:
                if not self.run:
                    raise socket.error

    def stop(self):
        self.run = False

    def serve(self):
        while self.run == True:
            self.handle_request()


class FrontendFeedBackHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        print ("thread count" + str(threadCount))
        if threadCount>7 :
            self.send_response(500)
        else:
            self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        self.end_headers()

if __name__ == '__main__':

    global compute_resource_ip
    global compute_resource_port

    compute_resource_ip = "tile-1-0"
    compute_resource_port = 8000
    httpserver_port = 4000
    feedback_port =5000

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'x', ['ip=', 'res_port='])
    except getopt.GetoptError:
        print sys.argv[0] + ' [--port portnumber(default=8000)] [--skew value] [--multiplier value]'
        sys.exit(2)

    for opt, arg in optlist:
        if opt in ("-ip", "--ip"):
            compute_resource_ip = str(arg)
        elif opt in ("-res_port", "--res_port"):
            compute_resource_port = int(arg)


    print (compute_resource_ip)
    print (str(compute_resource_port))
    print (str(httpserver_port))
    #pygame.init()
    #DISPLAY=pygame.display.set_mode((1200,1200),0,32)
    #DISPLAY.fill(white)

    #pygame.draw.rect(DISPLAY,white,(50,50,50,50))
    #updateReq("Hello ............")
    #pygame.display.update()
    #updateReq("Hello")


    # Start the webserver which handles incomming requests
    try:
        httpd = FrontEnd(("", httpserver_port), FrontendHttpHandler)
        server_thread = threading.Thread(target = httpd.serve)
        server_thread.daemon = True
        server_thread.start()

        feedback = FrontEndFeedBackServer(("", feedback_port), FrontendFeedBackHandler)
        feedback_thread = threading.Thread(target=feedback.serve)
        feedback_thread.daemon = True
        feedback_thread.start()


        def handler(signum, frame):
            print "Stopping http server..."
            httpd.stop()
            feedback.stop()
        signal.signal(signal.SIGINT, handler)

    except:
        print "Error: unable to http server thread"

    # Wait for server thread to exit
    feedback_thread.join(100)
    server_thread.join(100)
    feedback.stop()
    httpd.stop()





