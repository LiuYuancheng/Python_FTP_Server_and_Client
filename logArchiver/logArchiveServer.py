#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        logArchiveServer.py
#
# Purpose:     This module will provide a FTP server which can run in parallel 
#              thread to handle log files submission and provide a web UI for user 
#              to check the log files in the server.
# 
# Author:      Yuancheng Liu, Sandy Seah
#
# Created:     2024/07/25
# Version:     v_0.1.1
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------

import os
import platform
from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for, session, send_file
from directory_tree import DisplayTree

import logArchiveServerGlobal as gv
import logArchiveServerMgr as mgr

slashCar = '\\' if platform.system() == "Windows" else '/'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Start the FTP server service thread
gv.iFTPservice = mgr.FTPService(None)
gv.iFTPservice.start()
# Init the log file manager.
gv.iDataMgr = mgr.dataManager()
# Init the web interface.
app = Flask(__name__)
app.secret_key = 'insert_secret_key_here'

#-----------------------------------------------------------------------------
# web request handling functions.
@app.route('/')
@app.route('/index')
def index():
    """ route to introduction index page."""
    posts = {'page':0}  # page index is used to highlight the left page slide bar.
    serverData = gv.iDataMgr.getStorageData()
    posts.update(serverData)
    return render_template('index.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/agentview')
def agentview():
    """ route to all agents general information view page."""
    posts = {
             'page': 1,
             'agentsInfo': gv.iDataMgr.getAllAgentsInfo().values()
             }
    return render_template('agentview.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/agent/<path:subpath>', methods=['GET', 'POST'])
def show_directory(subpath=''):
    """ route to individual agent log files view page."""
    subpathList = subpath.split('/')
    if '' in subpathList: subpathList.remove('') # remove the duplicate '///' in url
    if len(subpathList) == 0: abort(404)
    agentName = str(subpathList[0])
    if len(subpathList) == 1 and agentName:gv.iDataMgr.updateAgentFileTree(agentName)
    agentInfo = gv.iDataMgr.getAgentInfo(agentName)
    
    currentPath = None
    # remove the duplicate in the path sub path.
    for i in range(len(subpathList)):
        testSubpath = slashCar.join(subpathList[i:])
        testPath = os.path.join(gv.ROOT_DIR, testSubpath)
        if os.path.exists(testPath):
            currentPath = testPath
            subpath = '/'.join(subpathList[i:])
            break
    
    if currentPath is None: abort(404)
    print(currentPath)
    if os.path.isdir(currentPath):
        # List directory contents
        contents = os.listdir(currentPath)
        directories = {d: DisplayTree(os.path.join(currentPath, d), stringRep=True, showHidden=True, maxDepth=2).replace('\n', '<br>')
                       for d in contents if
                       os.path.isdir(os.path.join(currentPath, d))}  
        files = [f for f in contents if os.path.isfile(os.path.join(currentPath, f))]
        # change the file system current path to the web displayed current path format.
        currentPath = currentPath.replace(gv.ROOT_DIR, '')
        if currentPath.startswith(slashCar): currentPath = currentPath[1:] # remove the first empty slash.
        posts = {
                 'page': 2,
                 'agentInfoDict': agentInfo,
                 'crtPathStr': currentPath.replace(slashCar, '/'),
                 'dirDict': directories,
                 'filesList': files
                 }
        return render_template('agents.html', posts=posts)
    else:
        # Serve a file for user to download
        return send_from_directory(gv.ROOT_DIR, subpath)

#-----------------------------------------------------------------------------
@app.route('/clients')
def clients():
    posts = {
             'page': 3,
             'clients': gv.gClientInfo
             }
    return render_template('clients.html', posts=posts)

#-----------------------------------------------------------------------------
@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST' and 'addUserSubmit' in request.form:
        username = request.form.get('addUser')
        passwd = request.form.get('addPassword')
        perm = request.form.get('addPerms')
        try:
            gv.iDataMgr.createNewUser(username, passwd, perm)
            session['message'] = f"User '{username}' added successfully!"
            session['category'] = 'success'
        except ValueError as e:
            session['message'] = str(e)
            session['category'] = 'warning'
        return redirect(url_for('users'))

    elif request.method == 'POST' and 'delUserSubmit' in request.form:
        username = request.form.get('delUser')
        passwd = request.form.get('delPassword')
        try:
            gv.iDataMgr.deleteUser(username, passwd)
            session['message'] = f"User '{username}' deleted successfully!"
            session['category'] = 'info'
        except ValueError as e:
            session['message'] = str(e)
            session['category'] = 'warning'
        return redirect(url_for('users'))

    posts = {
             'page': 4,
             'users': gv.iDataMgr.getAllUserInfo(),
             'message': session.pop('message', None),
             'category': session.pop('category', None)
             }

    return render_template('users.html', posts=posts)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=5000,  debug=False, threaded=True)
    app.run(host="0.0.0.0",
        port=int(gv.CONFIG_DICT['FLASK_SER_PORT']),
        debug=gv.CONFIG_DICT['FLASK_DEBUG_MD'],
        threaded=gv.CONFIG_DICT['FLASK_MULTI_TH'])
