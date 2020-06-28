# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 02:00:39 2020

@author: holge
"""

import socket
from server import PORT_DEFAULT, HEADER_LENGTH, CODING


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(), PORT_DEFAULT))

while True:
    msg_length = int(client_socket.recv(HEADER_LENGTH).strip())
    msg = client_socket.recv(msg_length)
    print(msg.decode(CODING))
    
    