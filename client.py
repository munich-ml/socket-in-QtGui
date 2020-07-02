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
        self.socket = None
        if auto_connect:
            self.connect()   
        
    
    def __str__(self):
        return str(self.socket)
    
    
    def connect(self):
        if self.socket is None:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((socket.gethostname(), self.port))
                self.set_blocking(False)   # default for this class
                print("Connected to server", self.socket.getpeername())
                
            except Exception:
                print("Could not connect to server.")
                self.socket = None
    
        else:
            print("Already connected!")
    
    
    def disconnect(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
            
            
    def set_blocking(self, blocking):
        """
        blocking <bool>: True="blocking", False="non blocking"
        """
        self.socket.setblocking(blocking)
    

    def send(self, obj):
        """
        Input <JSON serializable object> obj is serialized to a json string,
        added to a fixed length header, converted to <bytes>
        and send to the client socket.
        """
        # serialize the object to json
        json_obj = json.dumps(obj)
        
        # create the fixed length header    '0000000022' = 22 bytes
        header = str(len(json_obj))
        header = (HEADER_LENGTH - len(header)) * "0" + header
        
        # send header + json object
        self.socket.send(bytes(header+json_obj, CODING))    
        

    def receive(self):
        """
        Receives, deserializes from json and returns the object.
        
        May return None when used "non-blocking"
        """
        if self.socket:
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
    
    '''
    while True:
        msg = client.receive()
        if msg is not None:
            print(msg)
            
        if msg == "EOP":
            break
        
        sleep(0.1)
    '''