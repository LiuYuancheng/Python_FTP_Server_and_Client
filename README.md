# Python_FTP_Server_and_Client

### Distributed Log File Auto Archive Program

![](doc/img/title.png)

**Program Design Purpose**: We want to create a FTP server and client program example for file transfer, then we will build a computers cluster Log file archive system to collect the log file regularly from multiple nodes then save in the file server, and provide a web interface in the log file archive server for user to check. 

```
# Created:     2024/07/23
# Version:     v_0.0.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### Introduction

Some times we want to continuously collect log files from a lot servers used for big data analysis, this program will create a FTP client and server and the log archiver which can synchronize the node's specific log storage server with the log storage. It also provide a web interface for user the check and download the log file from the web archive server. The project include 3 components :

- **FTP Communication Library:** A  lib module provide the FTP client and server for log file transfer. 
- **Log Archive Agent**: A agent program running on the nodes in the compute cluster to regularly check the log data status and upload the new generated log file to log archive server via FTP client.
- **Log Archive Server**: A service program running on the Log data base server to maintain several file structure trees which are exactly same as the client node to save the log files and provide a web interface for user to search and view the logs.



#### Introduction of FTP Comm Library

The FTP Communication lib will include the server and client module and each module can be running in parallel with the main thread for user to integrate in their program. 

The server module need to included the below features: 

- FTP client authorization : verify and validate the client to connect to server and control the client's permission to upload and download files, create directory. 
- User control: API for admin to control the user's permission, add or remove the users. 
- Data transfer limitation: limit the clients file upload and download speed of the client.

> We use pyftpdlib to implement the FTP server module, reference link: https://pypi.org/project/pyftpdlib/

The client module need to include the below features:

- Connection handling: log in the server and handle the FTP server reconnection. 
- File system check and switch: Check whether the folder at server side exist and switch to the related directory
- File upload and download: upload file and download file to or from the server. 

> We use the python built-in lib ftplib to implement the client module, ref-link: https://docs.python.org/3/library/ftplib.html



#### Introduction of Log Archive Agent

The log archive agent will keep monitoring the node log storage folder, when it find a new log file is created it will upload the log file to the related folder in the server. The main features include: 

- Uploaded file DB: the agent will keep a uploaded log files record so every time if the agent restart, it knows which log has been uploaded to the server and which log file need to upload to server. 
- New log file search: find all the log files in the host log storage which can match the user's log pattern then compare with the record to find the new generated log file 
- Log file upload queue: a queue to keep all the new log's path, transfer the log to server and update the Uploaded file DB. 
- FTP client: A FTP client to build the same files structures in the server side and transfer the file.(For example, if a agent_ID=agent01's host log file is `C:\usr\test\logArchiver\AgentLogFolder\Logs\PhysicalWoldSimulator\20240723\PWS_UI_20240723_111325_1.txt` , the file need to be transfer to the server's folder `/agent01/Logs/PhysicalWoldSimulator/20240723/` with the same log file name.)



#### Introduction of Log Archive Server

All the agent will connect to the server to upload the log files, the server will manage the agent access, and provide a web interface for the user to search and download the log files. The main features include: 

- Client authorization : a client user record file to authorize the client connection and limit the file access. 
- FTP service: A FTP server running in back ground to handle the log file upload. 
- Log search and download webhost: A web host program provide UI for user to check, view and download the log files archived in the server.   



------

### System Design

#### 



 







https://pypi.org/project/directory-tree/