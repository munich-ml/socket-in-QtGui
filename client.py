# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 02:00:39 2020

@author: holge
"""

import socket
from server import PORT_DEFAULT, HEADER_LENGTH, CODING


class HTesterTcpIpClient():
    def __init__(self, port):
        self.port = port
        self.connected = False
        
    
    def connect(self):
        if not self.connected:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((socket.gethostname(), self.port))
                self.connected = True

            except Exception as e:
                print("Exception during HTesterTcpIpClient.connect:\n", str(e))
                self.connected = False
        return self.connected
    
    
    def disconnect(self):
        if self.connected:
            self.socket.close()
            self.connected = False
    

    def receive(self):
        if self.connected:
            try:
                msg_length = int(self.socket.recv(HEADER_LENGTH).strip())
                msg = self.socket.recv(msg_length)
                return msg.decode(CODING)
            
            except Exception as e:
                print("Exception during HTesterTcpIpClient.receive:\n", str(e))
                
        return None
            
    
    
if __name__ == "__main__":
    client = HTesterTcpIpClient(PORT_DEFAULT)