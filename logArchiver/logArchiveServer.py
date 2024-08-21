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
from flask import Flask, render_template, send_from_directory, abort
from directory_tree import DisplayTree

import logArchiveServerGlobal as gv
import logArchiveServerMgr as mgr


slashCar = '\\' if platform.system() == "Windows" else '/'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Start he FTP server service thread
gv.iFTPservice = mgr.FTPService(None)
gv.iFTPservice.start()
# Init the web interface.
gv.iDataMgr = mgr.dataManager()

app = Flask(__name__)

#-----------------------------------------------------------------------------
# web request handling functions.
@app.route('/')
@app.route('/index')
def index():
    """ route to introduction index page."""
    posts = {'page': 0}  # page index is used to highlight the left page slide bar.
    serverData = gv.iDataMgr.getStorageData()
    posts.update(serverData)
    return render_template('index.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/agentview')
def agentview():
    posts = {'page': 1}  # page index is used to highlight the left page slide bar.
    posts['agentsInfo'] = gv.iDataMgr.getAllAgentsInfo().values()
    #print(posts['agentsInfo'])
    return render_template('agentview.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/agent/<path:subpath>')
def show_directory(subpath=''):
    print(subpath)
    subpathList = subpath.split('/')
    if '' in subpathList: subpathList.remove('')
    if len(subpathList) == 0: abort(404)
    agentName = str(subpathList[0])
    if len(subpathList) == 1 and agentName:gv.iDataMgr.updateAgentFileTree(agentName)
    agentInfo = gv.iDataMgr.getAgentInfo(agentName)
    current_path = None
    # remove the duplicate in the path sub path.
    agents = [d for d in os.listdir(gv.ROOT_DIR) if os.path.isdir(os.path.join(gv.ROOT_DIR, d))]
    for i in range(len(subpathList)):
        testSubpath = slashCar.join(subpathList[i:])
        testPath = os.path.join(gv.ROOT_DIR, testSubpath)
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
        directories = {d: DisplayTree(os.path.join(current_path, d), stringRep=True, showHidden=True, maxDepth=2).replace('\n', '<br>')
                       for d in contents if
                       os.path.isdir(os.path.join(current_path, d))}  
        files = [f for f in contents if os.path.isfile(os.path.join(current_path, f))]
        #print(files)
        currentPath = current_path.replace(gv.ROOT_DIR, '')
        if currentPath.startswith(slashCar): currentPath = currentPath[1:]
        posts = {
                 'page': 2,
                 'agentInfoDict': agentInfo,
                 'crtPathStr': currentPath.replace(slashCar, '/'),
                 'dirDict': directories,
                 'filesList': files
                 }
        return render_template('agents.html', posts=posts)
    else:
        # Serve a file
        return send_from_directory(gv.ROOT_DIR, subpath)

@app.route('/clients')
def clients():
    posts = {'page': 3}
    posts['clients'] = mgr.clients_info
    return render_template('clients.html', posts=posts)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)
    app.run(host="0.0.0.0",
        port=int(gv.CONFIG_DICT['FLASK_SER_PORT']),
        debug=gv.CONFIG_DICT['FLASK_DEBUG_MD'],
        threaded=gv.CONFIG_DICT['FLASK_MULTI_TH'])