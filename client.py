# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 02:00:39 2020

@author: holge
"""

import socket
import errno
import json
from time import sleep
from server import PORT_DEFAULT, HEADER_LENGTH, CODING


class HTesterTcpIpClient():
    def __init__(self, port, auto_connect=True):
        self.port = port
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if auto_connect:
            self.connect()   
        
    
    def __str__(self):
        return str(self.socket)
    
    
    def connect(self):
        if not self.connected:
            try:
                self.set_blocking(True)   # socket must be blocking for connet
                self.socket.connect((socket.gethostname(), self.port))
                self.set_blocking(False)   # default for this class
                print("Connected to server", self.socket.getpeername())
                self.connected = True
                
            except Exception:
                print("Could not connect to server.")
                self.connected = False
        return self.connected
    
    
    def disconnect(self):
        if self.connected:
            self.socket.close()
            self.connected = False
            
            
    def set_blocking(self, blocking):
        """
        blocking <bool>: True="blocking", False="non blocking"
        """
        self.socket.setblocking(blocking)
    

    def receive(self):
        """
        Receives, deserializes from json and returns the object.
        
        May return None when used "non-blocking"
        """
        if self.connected:
            try:
                # Expected message starts with a fixed-length header
                msg_length = int(self.socket.recv(HEADER_LENGTH).decode(CODING))
                json_obj = self.socket.recv(msg_length).decode(CODING)
                return json.loads(json_obj)

            except IOError as e:
                # This is normal on non blocking connections - when there are no incoming data error is going to be raised
                # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
                # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
                if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                    return None

                # If we got different error code, a "real" error occured
                print("IOError in HTesterTcpIpClient.receive:\n", str(e))

        return None
            
    
    
if __name__ == "__main__":
    client = HTesterTcpIpClient(port=PORT_DEFAULT, auto_connect=True)
    while True:
        msg = client.receive()
        if msg is not None:
            print(msg)
            
        if msg == "EOP":
            break
        
        sleep(0.1)
    