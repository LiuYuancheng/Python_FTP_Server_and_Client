#-----------------------------------------------------------------------------
# Name:        logArchiveServerMgr.py
#
# Purpose:     This module is the data management module which provide the log 
#              files management and FTP server management functions.
#              
# Author:      Yuancheng Liu, Sandy Seah
#
# Created:     2024/08/20
# Version:     v_0.1.2
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import os
import time
import threading
from pyftpdlib.handlers import FTPHandler
from directory_tree import DisplayTree

import ftpComm
import ConfigLoader
import logArchiveServerGlobal as gv

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class CustomFTPHandler(FTPHandler):
    """ Custom FTP handler class to record the ftp client connection state (login/logout) 
        and update the global clients record list.
    """
    def on_connect(self):
        client = {
            'ip': self.remote_ip,
            'port': self.remote_port,
            'datetime': time.strftime('%Y-%m-%d %H:%M:%S',  time.localtime(self.started)),
        }
        gv.gClientInfo.append(client)
        print(f"Client connected from {self.remote_ip}:{self.remote_port} at {client['datetime']}. "
              f"Total clients connected: {len(gv.gClientInfo)}")

    def on_disconnect(self):
        for client in gv.gClientInfo:
            if client['ip'] == self.remote_ip and client['port'] == self.remote_port:
                gv.gClientInfo.remove(client)
                break
        print(f"Client disconnected from {self.remote_ip}:{self.remote_port}. "
              f"Total clients connected: {len(gv.gClientInfo)}")
        pass

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class dataManager(object):
    """ Log file storage, users and web information display management module. """
    
    def __init__(self) -> None:
        # load the user data 
        userRcdFile = os.path.join(gv.DIR_PATH, gv.CONFIG_DICT['USER_RCD'])
        if os.path.exists(userRcdFile):
            userInfoLoader = ConfigLoader.JsonLoader()
            userInfoLoader.loadFile(userRcdFile)
        # load all the agents' config data from the uploaded agents' config file.
        self.agentConfigInfo = {}
        self.getAllAgentsInfo()

    #-----------------------------------------------------------------------------
    def createAgentInfo(self, agentName):
        """ Scan the agent home directory and create the agent information dictionary.
            Args:
                agentName (str): agent name/ID string
            Returns:
                dict() : agent information dictionary, detail refer to the <agentData> 
                    in this function. Return None if not file the agent home folder. 
        """
        agentData = {
            'ID': None,
            'IP': None,
            'LoginUserName' : None,
            'UploadInv' : None,
            'Dirtree': None
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
                agentData['Dirtree'] = DisplayTree(agentDirPath, stringRep=True, showHidden=True)
            return agentData
        return None
    
    #-----------------------------------------------------------------------------
    def getAllAgentsInfo(self):
        """ Check the storage root directory and get all the agent information."""
        folderList = [d for d in os.listdir(gv.ROOT_DIR) 
                      if os.path.isdir(os.path.join(gv.ROOT_DIR, d))]
        #print(folderList)
        for agentID in folderList:
            if not (agentID in self.agentConfigInfo.keys()):
                self.agentConfigInfo[agentID] = self.createAgentInfo(agentID)
        return self.agentConfigInfo

    #-----------------------------------------------------------------------------
    def getStorageData(self):
        """ Get the storage folder and the FTP server configuration data."""
        folderList = [d for d in os.listdir(gv.ROOT_DIR) if os.path.isdir(os.path.join(gv.ROOT_DIR, d))]
        folderSize = os.path.getsize(gv.ROOT_DIR)
        storageData = {
            "FTPport": int(gv.CONFIG_DICT['FTP_SER_PORT']),
            "rootDir": gv.ROOT_DIR,
            "nodeUploadMax": int(gv.CONFIG_DICT['MAX_UPLOAD_SPEED'])/1024,
            "totalSize": int(folderSize),
            "nodeNum": len(folderList)
        }
        return storageData
    
    #-----------------------------------------------------------------------------
    def getAgentInfo(self, agentName):
        """ Get the agent information dictionary.
            Args:
                agentName (str): agent name/ID string
            Returns:
                _type_: agent information dictionary, detail refer to the <agentData> 
                    in <createAgentInfo> function. 
        """
        return self.agentConfigInfo[agentName] if agentName in self.agentConfigInfo.keys() else self.createAgentInfo(agentName)

    #-----------------------------------------------------------------------------
    def updateAgentFileTree(self, agentName):
        """ Refresh and update the file structure tree of the agent.
            Args:
                agentName (str): agent name/ID string
        """
        agentDirPath = os.path.join(gv.ROOT_DIR, agentName)
        if os.path.isdir(agentDirPath):
            self.agentConfigInfo[agentName]['Dirtree'] = DisplayTree(agentDirPath, stringRep=True, showHidden=True)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class FTPService(threading.Thread):
    """ FTP server service which can run parallel with the program main thread."""
    
    def __init__(self, parent) -> None:
        threading.Thread.__init__(self)
        self.parent = parent
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
        
    #-----------------------------------------------------------------------------
    def run(self):
        print("FTPService is running...")
        self.server.startServer()

    #-----------------------------------------------------------------------------
    def stop(self):
        print("FTPService is stoping...")
        self.server.stopServer()
