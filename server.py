# -*- coding: utf-8 -*-


import sys
import time
import datetime as dt
import socket
import json
import errno
from server_ui import Ui_server
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread, pyqtSignal


CODING = "utf-8"
PORT_DEFAULT = 2222
HEADER_LENGTH = 10     # number of header bytes. Fixed length header

class ServerMainWindow(QMainWindow, Ui_server):
    """
    Simple Qt Application 
    """
    def __init__(self, parent=None):
        super(ServerMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.spinBoxPort.setValue(PORT_DEFAULT)
        self.lineEditMsg.returnPressed.connect(self.on_button_send)
        self.buttonSend.clicked.connect(self.on_button_send)
        self.buttonStartStop.clicked.connect(self.on_button_start_stop)
        self.checkBoxEcho.stateChanged.connect(self.on_checkbox_echo)
        
        # open port at startup
        self.serving = False
        self.on_button_start_stop()
        
        
    def on_button_send(self):
        msg = self.lineEditMsg.text()
        try:
            self.print_to_log("sending msg '{}'".format(msg))
            self.server.sending_jobs.append(msg)
        except Exception as e:
            self.print_to_log(e)
        
        
    def on_button_start_stop(self):
        # toggle serving bit
        self.serving = not self.serving
        
        label = {True: "close port", False: "open port"}[self.serving]
        self.buttonStartStop.setText(label)
        
        if self.serving:  
            port = self.spinBoxPort.value()
            self.print_to_log("opening port " + str(port))
            self.server = ServerThread(port)
            self.server.sigStatUpdate.connect(self.print_to_log)
            self.server.sigMsgRcvd.connect(self.incoming_msg)
            self.server.sigClientDisconnected.connect(self.on_button_start_stop)
            self.server.start()
        else:
            self.print_to_log("closing the port")
            try:
                self.server.exiting = True
            except Exception as e:
                print(e)        
    
    
    def on_checkbox_echo(self):
        is_checked = self.checkBoxEcho.isChecked()
        status = {True: "started", False: "stopped"}[is_checked]
        self.print_to_log(status + " echoing received messages")
        
        
    def print_to_log(self, text):
        self.textBrowser.append(dt.datetime.now().strftime("%H:%M:%S ") + text)


    def incoming_msg(self, msg):
        self.print_to_log("msg received '{}'".format(msg[0]))
        if self.checkBoxEcho.isChecked():
            self.server.sending_jobs.append(msg[0])
        

class ServerThread(QThread):
    sigStatUpdate = pyqtSignal(str)
    sigMsgRcvd = pyqtSignal(list)
    sigClientDisconnected = pyqtSignal()

    def __init__(self, port):
        super(ServerThread, self).__init__()
        self.port = port
        self.exiting = False            # kill thread by setting exiting=True
        self.sending_jobs = []


    def __send(self, obj):
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
        self.client_socket.send(bytes(header+json_obj, CODING))                

    def __receive(self):
        """
        Receives, deserializes from json and returns the object.
        Returns None when there is nothing to receive
        """
        try:
            # Expected message starts with a fixed-length header
            msg_length = int(self.client_socket.recv(HEADER_LENGTH).decode(CODING))
            json_obj = self.client_socket.recv(msg_length).decode(CODING)
            return json.loads(json_obj)

        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return None

            # If we got different error code, a "real" error occured
            self.sigStatUpdate.emit("IOError, client probably disconnected.")
            self.sigClientDisconnected.emit()

        except ValueError:
            self.sigStatUpdate.emit("ValueError, client probably disconnected.")
            self.sigClientDisconnected.emit()

    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((socket.gethostname(), self.port))
            
            # modifiy the socket to allow address reuse
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # prepare connection
            connected = False
            server_socket.settimeout(1)
            server_socket.listen()
            
            while not self.exiting:
                if connected:
                    # send
                    if len(self.sending_jobs):
                        self.__send(self.sending_jobs.pop())
                       
                    # receive
                    rcv = self.__receive()
                    if rcv:
                        self.sigMsgRcvd.emit([rcv])
            
                else:  # wait for a client to connect
                    try:
                        self.client_socket, client_addr = server_socket.accept()     
                        self.client_socket.setblocking(False)
                        self.sigStatUpdate.emit("server connected to " + str(client_addr))            
                        connected = True
                        
                    except socket.timeout:
                        pass
                        
                time.sleep(1e-4)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    serverMainWindow = ServerMainWindow()
    serverMainWindow.show()
    app.exec_()
