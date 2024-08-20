#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        ftpTestcaseServer.py
#
# Purpose:     Test case module for <ftpComm.py>, this module will start a ftp 
#              test server use the test data set in ftpServer_data folder.
# 
# Author:      Yuancheng Liu
#
# Created:     2024/07/23
# Version:     v_0.1.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import os
import time
from pyftpdlib.handlers import FTPHandler
import ftpComm
dirpath = os.path.dirname(os.path.abspath(__file__))

clients_info = []

class CustomFTPHandler(FTPHandler):
    def on_connect(self):
        client = {
            'ip': self.remote_ip,
            'port': self.remote_port,
            'datetime': time.strftime('%Y-%m-%d %H:%M:%S',  time.localtime(self.started)),
        }
        clients_info.append(client)
        print(f"Client connected from {self.remote_ip}:{self.remote_port} at {client['datetime']}. "
              f"Total clients connected: {len(clients_info)}")

    def on_disconnect(self):
        for client in clients_info:
            if client['ip'] == self.remote_ip and client['port'] == self.remote_port:
                clients_info.remove(client)
                break
        print(f"Client disconnected from {self.remote_ip}:{self.remote_port}. "
              f"Total clients connected: {len(clients_info)}")
        pass

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    print('Start ftp test server...')
    dir = os.path.join(dirpath, 'ftpServer_data')
    server = ftpComm.ftpServer(dir, port=8081, ftpHandler=CustomFTPHandler, threadFlg=True)
    server.addUser('client1', '123456')
    server.startServer()

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()