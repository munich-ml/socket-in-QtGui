# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 02:00:39 2020

@author: holge
"""

import socket
import errno
from server import PORT_DEFAULT, HEADER_LENGTH, CODING


class HTesterTcpIpClient():
    def __init__(self, port, auto_connect=True):
        self.port = port
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if auto_connect:
            self.connect()   
        
    
    def connect(self):
        if not self.connected:
            try:
                self.set_blocking(True)   # socket mus be blocking for connet
                self.socket.connect((socket.gethostname(), self.port))
                self.set_blocking(False)   # default for this class
                self.connected = True
                
            except Exception as e:
                print("Could not connect to server.\n", str(e))
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
        if self.connected:
            try:
                msg_length = int(self.socket.recv(HEADER_LENGTH).strip())
                msg = self.socket.recv(msg_length)
                return msg.decode(CODING)

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
    client = HTesterTcpIpClient(PORT_DEFAULT)