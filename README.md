# Python_FTP_Server_and_Client

### Distributed Log File Automated Archive System

![](doc/img/title.png)

**Program Design Purpose**: This project aims to create an FTP server&client lib program for file transfer and a Log files synchronization system for log data archiving. We will develop an automated log file archive system that regularly collects newly generated log files from multiple nodes in a computer cluster and saves them on a central log file historian server. Additionally, a web interface will be provided on the log file historian server to allow users to access and review the archived logs.

```
# Created:     2024/07/23
# Version:     v_0.1.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
```

**Table of Contents**

[TOC]

------

### Introduction

Often, there is a need to continuously collect program log files from numerous servers for big data analysis, system operation monitoring, or threat detection. This project will create an automated log file archiver, which can synchronize specific log storage on nodes with a central log storage server. Additionally, it provides a web interface for users to check and download log files from the web archive server. The project includes three components:

- **FTP Communication Library** : A library module providing FTP client and server functionality for log file transfer.
- **Log Archive Agent** : An agent program running on the nodes in the compute cluster to regularly check the log data status and upload newly generated log files to the log archive server with the FTP client.
- **Log Archive Server:** A service program running on the log database server to maintain several file structure trees identical to those on the client nodes, save the log files, and provide a web interface for users to search and view the logs.



------

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

#### [Under editing]



 







https://pypi.org/project/directory-tree/