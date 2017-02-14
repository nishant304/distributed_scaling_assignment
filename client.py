import sys
import getopt
import socket
import httplib
from time import time, sleep
import pygame

from pygame.locals import *
import traceback

import errno

httpdServeRequests = True
latencySkew = 10
latencyMultiplier = 10
threadCount = 0

timeout = 100.0
prevTimeOutTime = 0
minute = 1000 * 60
timeoutCount = 0

WHITE = (255, 255, 255)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
ora = (128, 128, 128)


def tryServer(ip, port):
    global timeout, timeoutCount, prevTimeOutTime
    try :
        conn = httplib.HTTPConnection(ip, port, timeout=timeout / 1000)
        conn.request("GET", "")
        response_frontend = conn.getresponse()
        if response_frontend.status == 200:
            if (timeout >500) :
                timeout -= 10.0
            print "green"
            update(green)
        else:
            print "timeout"
            update(WHITE)

    except socket.timeout:

        update(red)
        if timeout < 3000 :
            timeout += 100.0
        conn.close()

    except:
        print ("Unable to send GET request")
        update(red)
        conn.close()


def sendGET(load_balancer_ip, load_balancer_port):
    try:
        display(blue)
        sleep(0.5)
        conn = httplib.HTTPConnection(load_balancer_ip, load_balancer_port)
        conn.request("GET", "")
        response = conn.getresponse()
        print("response status" + str(response.status))
        if response.status == 200:
            tryServer("tile-2-0",4000)
        elif response.status == 201 :
            tryServer("tile-3-0", 4000)
        elif response.status == 202:
            tryServer("tile-4-0", 4000)
        else:
            print "red"


        conn.close()


    except:
        print ("Unable to send GET request")
        update(red)
        conn.close()


def getTime():
    return int(round(time() * 1000))


j = 0
k = 0


def display(color):
    global k, j
    if (50 * k == 1000):
        j += 1
        k = 0
        # sleep(.4)
    pygame.draw.rect(DISPLAY,color,(50*k,50*j,50,50))
    pygame.display.update()
    pygame.draw.rect(DISPLAY,WHITE,(50*k+5,50*j,5,50))
    pygame.display.update()


def update(color):
    global k
    pygame.draw.rect(DISPLAY,color,(50*k,50*j,50,50))
    pygame.display.update()
    pygame.draw.rect(DISPLAY,WHITE,(50*k+5,50*j,5,50))
    pygame.display.update()
    k += 1


if __name__ == '__main__':
    noOfTests =1000
    load_balancer_ip = "tile-5-0"
    load_balancer_port = 7000

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'x', ['skew=', 'ip=', 'port='])
    except getopt.GetoptError:
        print sys.argv[0] + ' [--port portnumber(default=8000)] [--skew value] [--multiplier value]'
        sys.exit(2)

    for opt, arg in optlist:
        if opt in ("-skew", "--skew"):
            noOfTests = int(arg)
        elif opt in ("-ip", "--ip"):
            load_balancer_ip = str(arg)
        elif opt in ("-port", "--port"):
            load_balancer_port = int(arg)

    pygame.init()
    DISPLAY=pygame.display.set_mode((1200,1200),0,32)
    DISPLAY.fill(WHITE)

    # pygame.font.init()


    for i in range(1, noOfTests):
        sendGET(load_balancer_ip, load_balancer_port)



        # myfont = pygame.font.SysFont("monospace", 15)

        # render text
        # label = myfont.render("Some text!", 1, (255,255,0))
        # screen.blit(label, (100, 100))

        # print("blue")

        # Start the webserver which handles incomming requests

