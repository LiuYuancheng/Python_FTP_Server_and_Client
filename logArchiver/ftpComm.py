#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        ftpServer.py
#
# Purpose:     This module will provide a FTP server which can run in parallel 
#              thread for file transfer.
# 
# Author:      Yuancheng Liu
#
# Created:     2024/07/23
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import os

from ftplib import FTP
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer  
DEF_FTP_PORT = 8081
DEF_PERM = 'elradfmwM'  # Default permission for user

# Read permissions:
# "e" = change directory (CWD, CDUP commands)
# "l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE commands)
# "r" = retrieve file from the server (RETR command)
# Write permissions:
# "a" = append data to an existing file (APPE command)
# "d" = delete file or directory (DELE, RMD commands)
# "f" = rename file or directory (RNFR, RNTO commands)
# "m" = create directory (MKD command)
# "w" = store a file to the server (STOR, STOU commands)
# "M" = change file mode / permission (SITE CHMOD command) New in 0.7.0
# "T" = change file modification time (SITE MFMT command) New in 1.5.3
DIR_PATH = dirpath = os.path.dirname(os.path.abspath(__file__))
DEF_USER = {
    'admin': {
        'passwd': '123456',
        'perm': DEF_PERM,
        'dirpath': os.path.join(dirpath, 'ftpServer_data')
    }
}

DEF_READ_MAX_SPEED = 300 * 1024  # 300 Kb/sec (30 * 1024)
DEF_WRITE_MAX_SPEED = 300 * 1024  # 300 Kb/sec (30 * 1024)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class ftpServer(object):
    
    """ FTP server class."""
    def __init__(self, rootDirPath, port=DEF_FTP_PORT, userDict=DEF_USER,
                 readMaxSp=DEF_READ_MAX_SPEED, writeMaxSp=DEF_WRITE_MAX_SPEED,
                 threadFlg=False):
        self._port = int(port)
        if not os.path.exists(rootDirPath):
            os.makedirs(rootDirPath)
        self._rootPath = rootDirPath
        self._user = userDict
        self._threadFlg = threadFlg

        # Instantiate a dummy authorizer for managing 'virtual' users
        self.authorizer = DummyAuthorizer()
        self._initAuthorization()

        self.dtphandler = ThrottledDTPHandler
        self.dtphandler.read_limit = int(readMaxSp)
        self.dtphandler.write_limit = int(writeMaxSp)

        # Instantiate FTP handler class
        self.handler = FTPHandler
        self.handler.authorizer = self.authorizer
        self.handler.dtp_handler = self.dtphandler

        # Define a customized banner (string returned when client connects)
        self.handler.banner = "FTP server ready, license port: %s" % str(self._port)

        address = ('0.0.0.0', self._port)
        self.server = None
        if self._threadFlg:
            self.server = ThreadedFTPServer(address, self.handler)
        else:
            self.server = FTPServer(address, self.handler)
        print("FTP server started on port: %s" % str(self._port))

    #-----------------------------------------------------------------------------
    def _initAuthorization(self):
        """ Initialize the user authorization."""
        for user, info in self._user.items():
            userDir = info['dirpath'] if 'dirpath' in info.keys() else self._rootPath
            self.authorizer.add_user(user, info['passwd'], userDir, perm=info['perm'])
        self.authorizer.add_anonymous(os.getcwd())

    #-----------------------------------------------------------------------------
    def addUser(self, user, passwd, dirpath=None, perm='elradfmwM'):
        """ Add a new user to the server."""
        if user in self._user.keys():
            print("User %s already exists" % user)
            return False
        self._user[user] = {'passwd': passwd, 'dirpath': dirpath, 'perm': perm}
        if dirpath is None: dirpath = self._rootPath
        self.authorizer.add_user(user, passwd, dirpath, perm=perm)
        print("User %s added" % user)
        return True

    #-----------------------------------------------------------------------------
    def removeUser(self, user):
        """ Remove a user from the server."""
        if user not in self._user.keys():
            print("User %s does not exist" % user)
            return False
        self.authorizer.remove_user(user)
        del self._user[user]
        print("User %s removed" % user)
        return True

    #-----------------------------------------------------------------------------
    def getCurrentUsersInfo(self):
        return self._user

    #-----------------------------------------------------------------------------
    def startServer(self):
        """ Start the FTP server."""
        print("Starting FTP server...")
        if self.server is not None:
            self.server.serve_forever()
        print("FTF server stopped")

    #-----------------------------------------------------------------------------
    def stopServer(self):
        """ Stop the FTP server."""
        print("Stopping FTP server...")
        if self.server is not None:
            self.server.close_all()
        print("FTF server stopped")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class ftpClient(object):
    """ FTP client class for file transfer. """

    def __init__(self, host, port, user, pwd):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.client = FTP()
        self.connected = False

    def connectToServer(self):
        """ Connect to FTP server. """
        self.client.connect(self.host, self.port)
        self.client.login(self.user, self.pwd)
        print(self.client.getwelcome())
        return True

    def createDir(self, dirname):
        self.client.mkd(dirname)

    def swithToDir(self, dir):
        """ Switch to the target directory. """
        self.client.cwd(dir)

    def uploadFile(self, localFile, remoteFile):
        """ Upload file to FTP server. """
        try:
            self.client.storbinary('STOR ' + remoteFile, open(localFile, 'rb'))
            return True
        except Exception as err:
            print("ftpClient() upload file Error: %s" %str(err))
            return False

    def downloadFile(self, remoteFile, localFile):
        """ Download file from FTP server. """
        try:
            self.client.retrbinary('RETR ' + remoteFile, open(localFile, 'wb').write)
            return True
        except Exception as err:
            print("ftpClient() download file Error: %s" %str(err))
            return False

    def close(self):
        self.client.quit()

