#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        ftpTestcaseClient.py
#
# Purpose:     Test case module for <ftpComm.py>, this module will start a ftp 
#              test client use the test data set in ftpClient_data folder.
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
    print("Start the client testcase.")
    dir = os.path.join(dirpath, 'ftpClient_data')
    # Test case 0
    print("Test case 0: init ftp client and connect to server.")
    client = ftpComm.ftpClient('127.0.0.1', 8081, 'client1', '123456')
    client.connectToServer()
    if client.getConnectionStatus(): 
        print("- Pass")
    else:
        print("- Fail")
    #  Test case 1
    print("Test case 1: test create folder")
    # clear last test data
    serverDir = os.path.join(dirpath, 'ftpServer_data', 'client1')
    uploadFile = os.path.join(serverDir, 'uploadfile.pdf')
    if os.path.exists(uploadFile):os.remove(uploadFile)
    if os.path.exists(serverDir):os.rmdir(serverDir)
    client.swithToDir('/')
    client.createDir('client1')
    dirs = client.listDirInfo(detail=False)
    if 'client1' in dirs:
        print("- Pass")
    else:
        print("- Fail")
    # Test case 2
    print("Test case 2: test upload file")
    client.swithToDir('client1')
    localFile = os.path.join(dir,'Railway_signaling.pdf')
    client.uploadFile(localFile, 'uploadfile.pdf')
    dirs = client.listDirInfo(detail=False)
    if 'uploadfile.pdf' in dirs:
        print("- Pass")
    else:
        print("- Fail")
    # Test case 3
    print("Test case 3: test downloadfile")
    client.swithToDir('/')
    downloadfilepath = os.path.join(dir, 'downloadfile.pdf')
    client.downloadFile('Hacking - NMap Quick Reference Guide.pdf', downloadfilepath)
    if os.path.exists(downloadfilepath):
        print("- Pass")
    else:
        print("- Fail")

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()