#!/usr/bin/env/python

import sys
import os
import socket
import signal
import ReadingCommands
import Roomba
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from multiprocessing import Process

global roomba
global server

class SimpleHandler(WebSocket):

    def handleMessage(self):
        print("Message Received: " + str(self.data))

        # Shuts down the server and the Roomba proc
        if str(self.data) == "SHUTDOWN":
            print("Shutdown signal received, exiting...")
            roomba.term()
            self.close()
            sys.exit(0)

        # Moves the Roomba forward
        if str(self.data) == "START":
            print("Signalled to begin")
            roomba.forward()
            self.sendMessage(unicode('VSTART'))

        # Halts the Roomba movement to take reading
        if str(self.data) == "READING":
            print("Signalled to read, stopping movement")
            roomba.stop()
            roomba.stopBumpListener()
            print("Movement halted")
            self.signProc = Process(target=self.sendMessage(unicode('VREADING')))
            self.signProc.start()
            self.signProc.join()
            ReadingCommands.spin()
            print("Done taking reading")
            roomba.startBumpListener()
            roomba.forward()

        # DEPRECATED
        # # Signals the motor to spin the iPhone
        # if str(self.data) == "READNOW":
            # print("Taking reading...")
            # self.signaller = Process(self.sendMessage(unicode('VREADNOW')))
            # self.signaller.start()
            # ReadingCommands.spin()
            # print("Done taking reading")
            # roomba.startBumpListener()
            # roomba.forward()

        # Perform clean-up operations at end of experiment
        if str(self.data) == "ENDEXP":
            print("Signalled End of experiment")
            self.sendMessage(unicode('VENDEXP'))
            roomba.term()

    def handleConnected(self):
        print("New Connection: " + str(self.address))

    def handleClose(self):
        print("Closed Connection: " + str(self.address))

def signal_handler(signal, frame):
    print("TCP: SIGINT received, exiting...")
    roomba.term()
    sys.exit(0)

def get_ip_address():
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.connect(("8.8.8.8", 80))
    # return s.getsockname()[0]
    return '192.168.1.1'

def sendBump(bump):
    if bump == 1:
        server.sendMessage("B1")
    else:
        server.sendMessage("B2")

if __name__ == '__main__':
    port = 9000
    ipaddr = get_ip_address()

    server = SimpleWebSocketServer(str(ipaddr), port, SimpleHandler)
    print("Serving TCP Socket on " + str(ipaddr) + ":" + str(port))
    server.serveforever()
    roomba = Roomba.Roomba()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()

