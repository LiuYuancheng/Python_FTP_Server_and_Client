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
import ftpComm
dirpath = os.path.dirname(os.path.abspath(__file__))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    print('Start ftp test server...')
    dir = os.path.join(dirpath, 'ftpServer_data')
    server = ftpComm.ftpServer(dir, port=8081, threadFlg=True)
    server.addUser('client1', '123456')
    server.startServer()

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()