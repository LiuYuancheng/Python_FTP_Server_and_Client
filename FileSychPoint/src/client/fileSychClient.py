#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        fileSychClient.py
#
# Purpose:     This App will provide a file synchronization/share client for 
#              the clients to compare the files in share points server and the
#              client's local folder, then download the missing file from server 
#              to local.
# 
# Author:      Yuancheng Liu, Wei Wei
#
# Created:     2025/01/22
# Version:     v_0.0.1
# License:     MIT License
#-----------------------------------------------------------------------------

import os
from os import walk
import sys
import time

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
CONFIG_FILE_NAME = 'fileSychClientConfig.txt'
gGonfigPath = os.path.join(dirpath, CONFIG_FILE_NAME)
iConfigLoader = ConfigLoader.ConfigLoader(gGonfigPath, mode='r')
if iConfigLoader is None:
    print("Error: The config file %s is not exist.Program exit!" %str(gGonfigPath))
    exit()
CONFIG_DICT = iConfigLoader.getJson()

SYCH_INTEVAL = int(CONFIG_DICT['SYCH_INTERVAL'])

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
print("Init File Share Point Client...")

print(" - Check share local folder.")
localDirPath = os.path.join(DIR_PATH, CONFIG_DICT['LOCAL_DIR'])
if not os.path.exists(localDirPath):
    print("SharePoint Local folder not exist, create dir: %s" %localDirPath)
    os.makedirs(localDirPath)

client = ftpComm.ftpClient(CONFIG_DICT['SERVER_IP'], int(CONFIG_DICT['SERVER_PORT']), 
                           CONFIG_DICT['USER_NAME'], CONFIG_DICT['USER_PASSWD'])
client.connectToServer()
if client.getConnectionStatus(): 
    print("- Login to the server.")
else:
    print("- Login Failed.")
    exit()

terminate = False

while not terminate:
    serverFileList = client.listDirInfo(detail=False)
    serverFileList.sort()
    print(" - Get the file list from share point server: %s" %str(serverFileList))
    localfilenames = next(walk(localDirPath), (None, None, []))[2]  # [] if no file
    localfilenames.sort()
    if localfilenames == serverFileList:
        print(" - No file changed, sleep %d seconds." %SYCH_INTEVAL)
        time.sleep(SYCH_INTEVAL)
    else:
        print(" - File changed, start to sync.")
        for filename in serverFileList:
            if filename not in localfilenames:
                print(" - Download file: %s from server" %filename)
                localFilePath = os.path.join(localDirPath, filename)
                client.downloadFile(filename, localFilePath)
                
        for filename in localfilenames:
            if filename not in serverFileList:
                print(" - Delete file: %s from local" %filename)
                localFilePath = os.path.join(localDirPath, filename)
                os.remove(localFilePath)
        time.sleep(SYCH_INTEVAL)


