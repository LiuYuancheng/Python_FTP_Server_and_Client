#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        fileSychServerRun.py
#
# Purpose:     This App will provide a file synchronization/share service for 
#              multiple clients to upload and download files.
# 
# Author:      Yuancheng Liu, Wei Wei
#
# Created:     2025/01/22
# Version:     v_0.0.1
# License:     MIT License
#-----------------------------------------------------------------------------

import os
import sys
import threading

print("Current working directory is : %s" % os.getcwd())
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
print("Current source code location : %s" % dirpath)
APP_NAME = ('fileSychSys', 'Server')

TOPDIR = 'src'
LIBDIR = 'lib'

idx = dirpath.find(TOPDIR)
gTopDir = dirpath[:idx + len(TOPDIR)] if idx != -1 else dirpath   # found it - truncate right after TOPDIR
# Config the lib folder 
gLibDir = os.path.join(gTopDir, LIBDIR)
if os.path.exists(gLibDir):
    sys.path.insert(0, gLibDir)

import ftpComm

#-----------------------------------------------------------------------------
# load the config file.
import ConfigLoader
CONFIG_FILE_NAME = 'fileSychServerConfig.txt'
gGonfigPath = os.path.join(dirpath, CONFIG_FILE_NAME)
iConfigLoader = ConfigLoader.ConfigLoader(gGonfigPath, mode='r')
if iConfigLoader is None:
    print("Error: The config file %s is not exist.Program exit!" %str(gGonfigPath))
    exit()
CONFIG_DICT = iConfigLoader.getJson()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class FTPService(threading.Thread):
    """ FTP server service which can run parallel with the program main thread."""
    
    def __init__(self, parent, userFilePath, shareDirPath) -> None:
        threading.Thread.__init__(self)
        self.parent = parent
        # Create the file share directory
        self.shareDirPath = shareDirPath
        # Init the FTP server 
        self.servicePort = int(CONFIG_DICT['FTP_SER_PORT'])
        maxUploadSpeed = int(CONFIG_DICT['MAX_UPLOAD_SPEED'])
        maxDownloadSpeed = int(CONFIG_DICT['MAX_DOWNLOAD_SPEED'])
        userInfoLoader = ConfigLoader.JsonLoader()
        userInfoLoader.loadFile(userFilePath)
        userData = userInfoLoader.getJsonData()
        self.server = ftpComm.ftpServer(self.shareDirPath, port=self.servicePort, userDict=userData, 
                                        readMaxSp=maxDownloadSpeed, writeMaxSp=maxUploadSpeed, 
                                        ftpHandler=None, threadFlg=True)
        print("FTPService inited.")
        
    #-----------------------------------------------------------------------------
    def run(self):
        print("FTPService is running...")
        self.server.startServer()

    #-----------------------------------------------------------------------------
    def stop(self):
        print("FTPService is stopping...")
        self.server.stopServer()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
print("Init File Share Point Server...")

print(" - Check Share point folder.")
shareDirPath = os.path.join(DIR_PATH, CONFIG_DICT['SHARE_DIR'])
if not os.path.exists(shareDirPath):
    print("SharePoint Folder not exist, create dir: %s" %shareDirPath)
    os.makedirs(shareDirPath)

print(" - Load user record file.")
userRcdFile = os.path.join(DIR_PATH, CONFIG_DICT['USER_RCD'])
if not os.path.exists(userRcdFile):
    print("User record file not exist, create file: %s" %userRcdFile)
    exit()

serviceThread = FTPService(None, userRcdFile, shareDirPath)
serviceThread.start()
