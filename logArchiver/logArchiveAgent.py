#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        logAchiveAgent.py
#
# Purpose:     This module will provide a log sychronization agent running on the 
#              machine which need to archive the log file to transfer the new generated
#              log file to the logArchive server via ftp regularly.
# 
# Author:      Yuancheng Liu
#
# Created:     2024/07/25
# Version:     v_0.1.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program design:
    Log archive agent will keep a archived files record json file to record the 
    files which have been transferred to the server.It will follow below steps to 
    archive the new log file: 
    1. When the agent start, it will check the record file and load the file list.
    2. It will check the log file directory (user set in the config file) and find 
        the all the log file which match the user defined file name suffix.
    3. It will compare the file list with the record file and find the file need to
        transfer to the server. 
    4. It will start the FTP client to log in to the log archive server's agent 
        home folder and build the directory tree which exactly same as the agent's 
        local log directory tree.
    5. Tranfer the log file to the related directory in the server.
    6. After finished transfer one new log files, it will update the record file 
    7. After finished transfer all log file, wait time T (set by user in the config 
        file) and start from step 2.
"""
import os
import time
import json
import platform

import ConfigLoader
import ftpComm

TEST_MD = False # test mode to connect to the FTP server.True: not connect False: connect

dirpath = os.path.dirname(os.path.abspath(__file__))
slashChar = '\\' if platform.system() == "Windows" else '/'

#Load the agent config file 
CONFIG_FILE_NAME = 'AgentConfig.txt'
gGonfigPath = os.path.join(dirpath, CONFIG_FILE_NAME)
iConfigLoader = ConfigLoader.ConfigLoader(gGonfigPath, mode='r')
if iConfigLoader is None:
    print("Error: The config file %s is not exist.Program exit!" %str(gGonfigPath))
    exit()
CONFIG_DICT = iConfigLoader.getJson()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def count_slashes(s):
    """ count how many slashes in the file path string."""
    return str(s).count(slashChar)

#-----------------------------------------------------------------------------
class recordMgr(ConfigLoader.JsonLoader):
    """ Uploaded file record manager class."""
    def __init__(self):
        super().__init__()

    def addOneFile(self, filePath):
        """ Add one file path to the uploaded file record."""
        if self._haveData():
            self.jsonData.append(filePath)
        else:
            self.jsonData = [filePath]

    def sortFileList(self):
        """Sort the file path list based on number of slashChar."""
        self.jsonData = sorted(self.jsonData, key=count_slashes)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class LogAchiveAgent():
    """ Log archive agent class. The agent program needs to be put in the parent 
        directory with the log file.
        example: if your log will be saved in /user/logs/xxx, put the agent in the 
        /user folder and set the 'logs' in config file.
    """
    def __init__(self):
        self.agentID = CONFIG_DICT['AGENT_ID']
        self.targetDir = os.path.join(dirpath, CONFIG_DICT['LOG_DIR']) 
        self.serverIP = CONFIG_DICT['FTP_SER_IP']
        self.serverPort = int(CONFIG_DICT['FTP_SER_PORT'])
        self.user= CONFIG_DICT['USER_NAME']
        self.password = CONFIG_DICT['USER_PWD']
        # Init the logfile record manager. 
        self.recordLoader = recordMgr()
        rcdFIle = os.path.join(dirpath, CONFIG_DICT['RCD_JSON'])
        self.loadRcdFile(rcdFIle)
        # Init the FTP client and connect to the server.
        if not TEST_MD:
            self.client = ftpComm.ftpClient(self.serverIP, self.serverPort, self.user, self.password)
            print("LogAchiveAgent: Start to login to the log server...")
            if self.client.connectToServer():
                print("LogAchiveAgent: Login to the log server successfully!")
            else:
                print("LogAchiveAgent: Login to the log server failed!")
                exit()
        self.terminate = False

    #-----------------------------------------------------------------------------
    def loadRcdFile(self, rcdFile):
        rcdFilePath = os.path.join(dirpath, rcdFile)
        if not os.path.exists(rcdFilePath):
            print("Can not find upload record file %s , create a new record" %str(rcdFilePath))
            with open(rcdFilePath, "w") as fh:
                json.dump([], fh)
        self.recordLoader.loadFile(rcdFilePath)
        
    #-----------------------------------------------------------------------------
    def findAlllogfiles(self):
        """ Find all the log files in the target directory."""
        filePathList = []
        # if don't set the file suffix, all the file in the target folder will be uploaded.
        suffix = str(CONFIG_DICT['LOG_PF']) if 'LOG_PF' in CONFIG_DICT.keys() else ''
        for root, dirs, files in os.walk(self.targetDir):
            for file in files:
                filePath = os.path.join(root, file)
                if filePath.lower().endswith(suffix):
                    filePathList.append(filePath)
        return filePathList

    #-----------------------------------------------------------------------------
    def getNewUploadFiles(self):
        """ Compate the logs in the folder and check with the record file to find 
            the new log files.
            Returns:
                list(): sorted list of new log files' path.
        """
        newUpload = []
        allLogfiles = self.findAlllogfiles()
        uploadedFiles = self.recordLoader.getJsonData()
        for fileName in allLogfiles:
            if not fileName in uploadedFiles:
                print("LogAchiveAgent: Found a new log file %s" %fileName)
                newUpload.append(fileName)
        # sort the new upload list.
        return sorted(newUpload, key=count_slashes)

    #-----------------------------------------------------------------------------
    def switchToHome(self):
        """ Swith to the FTP server side's agent root/<Agent_ID> directory, if the home 
            directory is not exist, create the home drectory in server side.
        """
        self.client.swithToDir('/')
        homeDir = self.agentID
        try:
            self.client.swithToDir(homeDir)
        except Exception as err:
            print("Home folder not found, create a new home folder.")
            self.client.createDir(homeDir)
            self.client.swithToDir(homeDir)

    #-----------------------------------------------------------------------------
    def startUpload(self, localFilePath):
        """ Start to uplaod a local file to the FTP server related folder.
            Args:
                localFilePath (str): local file path.
            Returns:
                bool: upload result.
        """
        self.switchToHome()
        # remote the local path front part to match to the FTP server directory structure.
        serPath = str(localFilePath).replace(self.targetDir, '') 
        dirList = serPath.split(slashChar)
        # Create the related directory structure on the home folder.
        if len(dirList) > 1:
            for dir in dirList[0:-1]:
                if dir != '':
                    try:
                        self.client.swithToDir(dir)
                    except Exception as erro:
                        self.client.createDir(dir)
                        self.client.swithToDir(dir)
        # Upload log file
        fileName = dirList[-1]
        try:
            self.client.uploadFile(localFilePath, fileName)
            print("LogAchiveAgent: successfully uploaded file %s" %fileName)
            return True 
        except Exception as erro:
            print("LogAchiveAgent: Failed to upload file %s" %fileName)
            print("Error: %s" %erro)
            return False 

    #-----------------------------------------------------------------------------
    def uploadOwnConfig(self):
        """ Upload the agent's config file to the FTP server's agent own folder."""
        self.switchToHome()

        fileList = self.client.listDirInfo(detail=False)
        if not CONFIG_FILE_NAME in fileList:
            print("uploadOwnConfig()> uploaded the own log file to the server side.")
            self.client.uploadFile(gGonfigPath, CONFIG_FILE_NAME)

    #-----------------------------------------------------------------------------
    def run(self):
        """ The log file upload main loop."""
        self.uploadOwnConfig()
        print("LogAchiveAgent[ID=%s]: start log archive main loop" %self.agentID)
        while not self.terminate:
            logfileList = self.getNewUploadFiles()
            uploadedCount = 0
            for filepath in logfileList:
                rst = self.startUpload(filepath)
                if rst:
                    self.recordLoader.addOneFile(filepath)
                    uploadedCount += 1
                time.sleep(0.2)
            print("Upload progress finished [%d/%d]" %(uploadedCount, len(logfileList)))
            self.recordLoader.sortFileList()
            self.recordLoader.updateRcdFile()
            time.sleep(int(CONFIG_DICT['UPLOAD_INV']))

    #-----------------------------------------------------------------------------
    def stop(self):
        self.terminate = True
        self.client.close()
        print("LogAchiveAgent[ID=%s]: stop log archive main loop" %self.agentID)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    logAchiveAgent = LogAchiveAgent()
    logAchiveAgent.run()

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
