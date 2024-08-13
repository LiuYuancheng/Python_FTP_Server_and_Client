#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        logArchiveServer.py
#
# Purpose:     This module will provide a FTP server which can run in parallel 
#              thread for file transfer and provide a web UI for user to check 
#              the log files in the server.
# 
# Author:      Yuancheng Liu
#
# Created:     2024/07/25
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import os
import platform
import threading
from flask import Flask, render_template, send_from_directory, abort

import ConfigLoader
import ftpComm

DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
slashCar = '\\' if platform.system() == "Windows" else '/'

#Load the agent config file 
CONFIG_FILE_NAME = 'ServerConfig.txt'
gGonfigPath = os.path.join(dirpath, CONFIG_FILE_NAME)
iConfigLoader = ConfigLoader.ConfigLoader(gGonfigPath, mode='r')
if iConfigLoader is None:
    print("Error: The config file %s is not exist.Program exit!" %str(gGonfigPath))
    exit()
CONFIG_DICT = iConfigLoader.getJson()

ROOT_DIR = os.path.join(dirpath, CONFIG_DICT['LOG_DIR'])

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class FTPService(threading.Thread):
    """ FTP server service which can run parallel with the program main thread."""
    
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)
        # Create the FTP root folder if it is not exist.
        self.logArchiveDir = ROOT_DIR
        if not os.path.exists(self.logArchiveDir): os.makedirs(self.logArchiveDir)
        # Init the FTP server 
        self.servicePort = int(CONFIG_DICT['FTP_SER_PORT'])
        maxUploadSpeed = int(CONFIG_DICT['MAX_UPLOAD_SPEED'])
        maxDownloadSpeed = int(CONFIG_DICT['MAX_DOWNLOAD_SPEED'])
        userRcdFile = os.path.join(DIR_PATH, CONFIG_DICT['USER_RCD'])
        userInfoLoader = ConfigLoader.JsonLoader()
        userInfoLoader.loadFile(userRcdFile)
        userData = userInfoLoader.getJsonData()
        self.server = ftpComm.ftpServer(self.logArchiveDir, port=self.servicePort, userDict=userData, 
                                        readMaxSp=maxDownloadSpeed, writeMaxSp=maxUploadSpeed, 
                                        threadFlg=True)
        print("FTPService inited.")
        
    def run(self):
        print("FTPService is running...")
        self.server.startServer()

    def stop(self):
        print("FTPService is stoping...")
        self.server.stopServer()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Start he FTP server service thread
iFTPservice = FTPService(None)
iFTPservice.start()
# Init the web interface.
app = Flask(__name__)

@app.route('/')
@app.route('/index')
@app.route('/<path:subpath>')
def show_directory(subpath=''):
    subpathList = subpath.split('/')
    current_path = None
    # remove the duplicate in the path sub path.
    clients = ftpComm.clients_info
    agents = [d for d in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, d))]
    for i in range(len(subpathList)):
        testSubpath = slashCar.join(subpathList[i:])
        testPath = os.path.join(ROOT_DIR, testSubpath)
        if os.path.exists(testPath):
            current_path = testPath
            subpath = '/'.join(subpathList[i:])
            break
    if current_path is None: abort(404)
    print(current_path)
    if os.path.isdir(current_path):
        # List directory contents
        contents = os.listdir(current_path)
        # print(contents)
        directories = {d: os.listdir(os.path.join(current_path, d))
                       for d in contents if
                       os.path.isdir(os.path.join(current_path, d))}
        files = [f for f in contents if os.path.isfile(os.path.join(current_path, f))]
        #print(files)
        return render_template('index.html', clients=clients, agents=agents,
                               subpath=subpath, directories=directories, files=files)
    else:
        # Serve a file
        return send_from_directory(ROOT_DIR, subpath)

@app.route('/clients')
def show_clients():
    clients = ftpComm.clients_info
    return render_template('clients.html', clients=clients)


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)
    app.run(host="0.0.0.0",
        port=int(CONFIG_DICT['FLASK_SER_PORT']),
        debug=CONFIG_DICT['FLASK_DEBUG_MD'],
        threaded=CONFIG_DICT['FLASK_MULTI_TH'])