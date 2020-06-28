# -*- coding: utf-8 -*-


import sys
import time
import datetime as dt
import socket
from server_ui import Ui_server
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread, pyqtSignal


CODING = "utf-8"
PORT_DEFAULT = 1234
HEADER_LENGTH = 10     # number of header bytes

class ServerMainWindow(QMainWindow, Ui_server):
    """
    Simple Qt Application 
    """
    def __init__(self, parent=None):
        super(ServerMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.spinBoxPort.setValue(PORT_DEFAULT)
        self.serving = False
        self.label_start_stop_button()
        self.buttonSend.clicked.connect(self.on_button_send)
        self.buttonStartStop.clicked.connect(self.on_button_start_stop)
        self.checkBoxEcho.stateChanged.connect(self.on_checkbox_echo)
        self.print_to_log("application started")

    
    def label_start_stop_button(self):
        label = {True: "stop", False: "start"}[self.serving]
        self.buttonStartStop.setText(label)

    
    def on_button_send(self):
        msg = self.lineEditMsg.text()
        try:
            self.server.sending_jobs.append(msg)
            self.print_to_log("sending " + msg)
        except Exception as e:
            self.print_to_log(e)
        
        
        
    def on_button_start_stop(self):
        self.serving = not self.serving
        self.label_start_stop_button()
        
        if self.serving:  
            self.print_to_log("starting the server")
            self.server = ServerThread(self.spinBoxPort.value())
            self.server.sigStatUpdate.connect(self.print_to_log)
            self.server.start()
        else:
            self.print_to_log("terminating the server")
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


class ServerThread(QThread):
    sigStatUpdate = pyqtSignal(str)
    sigMsgRcvd = pyqtSignal(list)

    def __init__(self, port):
        super(ServerThread, self).__init__()
        self.port = port
        self.exiting = False            # kill thread by setting exiting=True
        self.sending_jobs = []


    def __send(self, msg):
        header_msg = f"{len(msg):<{HEADER_LENGTH}}" + msg
        self.client_socket.send(bytes(header_msg, CODING))                
            
    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((socket.gethostname(), self.port))
            server_socket.listen(5)
            self.client_socket, client_addr = server_socket.accept()
            
            self.sigStatUpdate.emit("server connected to " + str(client_addr))
            
            self.__send("Welcome to the server")
            
            while not self.exiting:
                if len(self.sending_jobs):
                    self.__send(self.sending_jobs.pop())
                   
                time.sleep(1e-4)
        
        self.sigStatUpdate.emit("run method is exiting")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    serverMainWindow = ServerMainWindow()
    serverMainWindow.show()
    app.exec_()
