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

The system work flow diagram is shown below:

![](doc/img/workflow.png)

To check the system usage demo, please refer to this video: 



------

### System Design

In this section, we will introduce the main features, detailed design of each module and the function of sub-modules based on the workflow diagram shown in the introduction section. 

#### Design of FTP Comm Library

The FTP Communication Library includes both server and client modules, each capable of running in parallel with the main thread to allow for seamless integration into user programs.

The FTP-server module includes the following features:

- **FTP Client Authorization** : Verifies and validates clients connecting to the server, controlling their permissions to upload, download files, create and remove directories or files.
- **User Management** : Provides an API for administrators to manage user permissions, and add or remove users.
- **Data Transfer Limitation:** Limits the file upload and download speeds for clients.

>  We use `pyftpdlib` to implement the FTP server module, reference link: https://pypi.org/project/pyftpdlib/

The FTP-client module includes the following features:

- **Connection Handling** : Login the server and manages FTP server reconnections.
- **File System Check and Switch** : Checks whether the folder exists on the server side and switches to the relevant directory.
- **File Upload and Download** :  Uploads files to and downloads files from the server.

> We use the python built-in lib `ftplib` to implement the client module, ref-link: https://docs.python.org/3/library/ftplib.html



#### Design of Log Archive Agent

The Log Archive Agent continuously monitors the node's log storage folder. When a new log file is created, it uploads the log file to the corresponding folder on the server. The main features include:

- **Uploaded File Record** :  The agent maintains a record of uploaded log files, so when the agent restarts, it knows which logs have been uploaded and which need to be uploaded.

- **New Log File Search** : The agent searches for all log files in the host log storage that match the user-defined log pattern, then compares them with the record to identify newly generated log files.

- **Log File Upload Queue** : A queue that stores the paths of new log files, transfers the logs to the server, and updates the uploaded file database.

- **FTP Client** : An FTP client that replicates the file structure on the server side and transfers the files. For example, if an agent with ID `agent01` has a log file located at `C:\usr\test\logArchiver\AgentLogFolder\Logs\PhysicalWorldSimulator\20240723\PWS_UI_20240723_111325_1.txt`, the file will be transferred to the server folder `/agent01/Logs/PhysicalWorldSimulator/20240723/` with the same log file name.

The Log Archive Agent will keep a JSON file recording the files that have been transferred to the server. It follows these steps to archive new log files:

1. When the agent starts, it checks the record file and loads the file list.
2. It checks the log file directory (specified by the user in the config file) and finds all log files that match the user-defined log file name pattern.
3. It compares the file list with the record file to identify files that need to be transferred to the server.
4. It starts the FTP client to log in to the log archive server's agent home folder and build a directory tree identical to the agent's local log directory tree.
5. It transfers the log files to the corresponding directory on the server.
6. After transferring a new log file, it updates the record file.
7. After transferring all log files, it waits for a user-defined interval (set in the config file) and then repeats the process starting from step 2.



#### Design of Log Archive Server

All agents will connect to the server to upload log files. The server manages agent access and provides a web interface for users to search and download log files. The main features include:

- **Client Authorization** : A client user record file to authorize client connections and limit file access.
- **FTP Service** : An FTP server running in the background to handle log file uploads.
- **Log Search and Download Web Host:** A web host program providing a user interface for checking, viewing, and downloading the log files archived on the server.



------

### System Setup

##### Development Environment

- python 3.7.2rc2+ 64bit [ Windows11 ]

##### Additional Lib/Software Need

- pyftpdlib : https://pypi.org/project/pyftpdlib/, install: `pip install pyftpdlib`
- Flask: https://flask.palletsprojects.com/en/3.0.x/, install: `pip install Flask`

##### Hardware Needed : None

##### Program Files List 

| Program File        | Execution Env | Description                                                  |
| ------------------- | ------------- | ------------------------------------------------------------ |
| src/plcSimulator.py | python 3.7 +  | The main PLC simulator lib provides the simulator interface, Real world emulation app connector and the Modbus-TCP sub-threading service. |