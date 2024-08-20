#-----------------------------------------------------------------------------
# Name:        logArchiveServerMgr.py
#
# Purpose:     This module is used as a project global config file to set the 
#              constants, parameters and instances which will be used in the 
#              other modules in the project.
#              
# Author:      Yuancheng Liu
#
# Created:     2024/08/20
# Version:     v_0.1.1
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import os
import threading
from pyftpdlib.handlers import FTPHandler

import ftpComm
import ConfigLoader
import logArchiveServerGlobal as gv


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class dataManager(object):

    def __init__(self) -> None:
        userRcdFile = os.path.join(gv.DIR_PATH, gv.CONFIG_DICT['USER_RCD'])
        userInfoLoader = ConfigLoader.JsonLoader()
        userInfoLoader.loadFile(userRcdFile)
        self.agentConfigInfo = {}
        self.getAllAgentsInfo()

    #-----------------------------------------------------------------------------
    def getAllAgentsInfo(self):
        folderList = [d for d in os.listdir(gv.ROOT_DIR) if os.path.isdir(os.path.join(gv.ROOT_DIR, d))]
        print(folderList)
        for agentID in folderList:
            if not (agentID in self.agentConfigInfo.keys()):
                self.agentConfigInfo[agentID] = self.getAgentInfo(agentID)
        return self.agentConfigInfo

    #-----------------------------------------------------------------------------
    def getStorageData(self):
        folderList = [d for d in os.listdir(gv.ROOT_DIR) if os.path.isdir(os.path.join(gv.ROOT_DIR, d))]
        folderSize = os.path.getsize(gv.ROOT_DIR)
        storageData = {
            "FTPport": int(gv.CONFIG_DICT['FTP_SER_PORT']), 
            "nodeUploadMax": int(gv.CONFIG_DICT['MAX_UPLOAD_SPEED'])/1024,
            "totalSize": int(folderSize),
            "nodeNum": len(folderList)
        }
        return storageData
    
    #-----------------------------------------------------------------------------
    def getAgentInfo(self, agentName):
        agentData = {
            'ID': None,
            'IP': None,
            'LoginUserName' : None,
            'UploadInv' : None,
        }
        agentDirPath = os.path.join(gv.ROOT_DIR, agentName)
        if os.path.isdir(agentDirPath):
            agentData['ID'] = agentName
            configFilePath = os.path.join(agentDirPath, 'AgentConfig.txt')
            if os.path.exists(configFilePath):
                loader = ConfigLoader.ConfigLoader(configFilePath, mode='r')
                dataDict = loader.getJson()
                agentData['ID'] = dataDict['AGENT_ID']
                agentData['IP'] = dataDict['AGENT_IP']
                agentData['LoginUserName'] = dataDict['USER_NAME']
                agentData['UploadInv'] = int(dataDict['UPLOAD_INV'])
        return agentData

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
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
class FTPService(threading.Thread):
    """ FTP server service which can run parallel with the program main thread."""
    
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)
        # Create the FTP root folder if it is not exist.
        self.logArchiveDir = gv.ROOT_DIR
        if not os.path.exists(self.logArchiveDir): os.makedirs(self.logArchiveDir)
        # Init the FTP server 
        self.servicePort = int(gv.CONFIG_DICT['FTP_SER_PORT'])
        maxUploadSpeed = int(gv.CONFIG_DICT['MAX_UPLOAD_SPEED'])
        maxDownloadSpeed = int(gv.CONFIG_DICT['MAX_DOWNLOAD_SPEED'])
        userRcdFile = os.path.join(gv.DIR_PATH, gv.CONFIG_DICT['USER_RCD'])
        userInfoLoader = ConfigLoader.JsonLoader()
        userInfoLoader.loadFile(userRcdFile)
        userData = userInfoLoader.getJsonData()
        self.server = ftpComm.ftpServer(self.logArchiveDir, port=self.servicePort, userDict=userData, 
                                        readMaxSp=maxDownloadSpeed, writeMaxSp=maxUploadSpeed, 
                                        ftpHandler=CustomFTPHandler, threadFlg=True)
        print("FTPService inited.")
        
    def run(self):
        print("FTPService is running...")
        self.server.startServer()

    def stop(self):
        print("FTPService is stoping...")
        self.server.stopServer()