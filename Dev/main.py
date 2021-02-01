# ====================
# Python chat program
# ====================
# 
# Author: Edren Dacaymat
# 
# Description:
# A simple chat program.
# 
# -----------------------------------
# Commands list:
# /behost - hosts a chat server
# usage: /behost [server name] [port]
# advanced setup:
# /behost [server name] [port] [number of clients] [ip address to use]
# 
# /join - joins a chat server
# usage: /join [server ip] [port]
# 
# /end - ends connection
# usage: /end
# 
# /help - shows a list of commands and their uses.
# usage: /help
# 
# /username - change your username
# usage /username [new username]
# **note that your username should not have any spaces**
# 
# /exit - terminates application
# usage: /terminate
# **note that existing connections would be closed**
# -----------------------------------
# 
# This application support multiple clients up to a 
# default max of 30 clients. You can change the number
# of clients with the "/behost" command by typing:
# /behost [server name] [port] [number of clients] [ip address to use]
# 
# Application does not automatically perform any port
# forwarding so trying to make two clients run in a
# nested network will not work. Both clients should be
# present in the same network to avoid connection problems.
# 
# Designed and tested using Python 2.7.8 release version.
# GUI created using wxPython 3.0-msw. Socket and threading 
# classes are python standard libraries.
# 
# Works in Windows 7 x64 and Windows 8.1 Pro x64. Not tested
# in other platforms but should still theoretically work.
# Bugs in the code may be present, but most of the easily
# recognizable bugs should have been dealt with already.
# 
# To run without spawning a command prompt use run.cmd or
# enter in command line: "pythonw.exe main.py". Make sure
# your python bin directory is present in your system
# PATH environment variable. That should make it easy to
# run python programs in the command prompt.
# 
# Set variable debugMode to True to see debugging messages.
# Set printToHistory to True to see debugging messages
# printed in the chat history text box.


# ==================================================

# ==========
# To-do list
# ==========
# 
# *user friendliness:
#  - make port default to 24443
#  - make commands need less params
#  - input history
# *SSL: implement method to get certificate of peer and verify it during handshake
# *SSL: system to auto generate certificates
#
# *implement a state system to remove dependence on global vars
# *state system would allow for multiple chat lobbies
# *update functions to use state system (functions should not modify any vars outside function)
# *update classes to use state system (classes should not modify any vars outside of it scope)

# ==================================================

# User Friendliness Outline
#
# *unify join and host commands
# /join [ip addr] [name of lobby]
# /behost [name of lobby]

# ==================================================

# =======
# Imports
# =======
# import all the dependencies
import sys

# before continuing we should check if application is compatible
# with the current python version.
if (sys.version_info < (3,6,6)):
    print('This application requires Python 3.6.6 or greater')

# Import the rest of the dependencies
import socket
import threading
import time
import random
import string

# Try import SSL
try: import ssl
except ImportError: # import failed, show error.
    print('This application requires the SSL module to run.')
    sys.exit(11)

# Import wxPython Module
try: import wx # import the wxPython module.
except ImportError: # import failed, show error.
    print('This application requires the wxPython module to run.')
    sys.exit(10)

# ================
# Global Variables
# ================

# ==================== To be replaced ====================
# Holds the pointer to the history textctrl
historyData = ''
# Holds the pointer to the users textctrl
userlistData = ''
# Stores user's username
username = 'User_'+''.join(random.choice(string.digits) for i in range(5)) # generate a default username
# Status variable that determines whether it is host or not
isHost = False
# Array that stores all the client handler threads
# Only the host make use of this
serverclients = []
# ==================== To be replaced ====================

# Debugging
debugMode = True
sslEnable = True
printToHistory = True

# ===============
# Connection Data
# ===============

# state() : Object
# Desc: Connection data
class ConData():
    # __init__()
    # Desc: class init function
    def __init__(self):
        # Holds the pointer to the history textctrl
        self.historyData = ''
        # Holds the pointer to the users textctrl
        self.userlistData = ''
        # Stores user's username (default username is generated)
        self.username = 'User_'+''.join(random.choice(string.digits) for i in range(5))
        # Status variable that determines whether it is host or not
        self.isHost = False
        # Array that stores all the client handler threads (Only the host make use of this)
        self.serverclients = []

# =========
# Functions
# =========

# Debug output function.
def dbg(msg,type='Status'):
    if debugMode:
        print('*['+type+']: '+msg)
        if printToHistory:
            historyData.AppendText('*['+type+']: '+msg+'\n')

# sendToAll()
# Params: msg - send message
# Desc: facilitates sending a message to all clients
def sendToAll(msg,notclients=[]):
    if isHost:
        dbg('sending to all clients: '+str(msg))
        for tc in serverclients:
            if tc.username in notclients:
                continue
            if tc.is_alive() and (not tc.term):
                try:
                    tc.send(str(msg))
                except socket.error as err:
                    tc.stop()
                    tc = None
                    continue

# updateUSersList()
# Params: none
# Desc: updates the users list textctrl
def updateUsersList(sendupdate=False):
    global username
    global userlistData
    dbg('updating user list')
    if userlistData != '':
        userlistData.Clear()
        userlistData.AppendText('#['+str(username)+']\n')
        for tc in serverclients:
            if tc.is_alive() and (not tc.term):
                userlistData.AppendText('#'+tc.username+'\n')
    if sendupdate and isHost:
        for tc in serverclients:
            if tc.is_alive() and (not tc.term):
                try:
                    tc.send('0ulist_update '+userlistData.GetValue())
                except socket.error as err:
                    continue

# serverSocket()
# Params: port - Port number, cnum - Number of clients to listen
# Desc: creates a server socket object with the supplied port
# and listener number
def serverSocket(port,cnum,iph):
    servsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # create socket object
    servsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # set some options
    # get ip address
    hostaddr = ''
    ifaces = socket.getaddrinfo(socket.gethostname(), int(port)) # get all possible ip addresses
    for ifc in ifaces:
        if ifc[0] == 2: # we will use ipv4 only to make life easier
            if ifc[4][0] in ['127.0.0.1','127.0.1.1']: # ignore localhost
                continue
            hostaddr = ifc[4]
    if iph != None: # override ip address with supplied ip
        hostaddr = (str(iph),int(port))
    dbg('using '+str(hostaddr)) # debug
    try:
        dbg('binding to socket')
        servsock.bind(hostaddr) # bind to socket
        dbg('listening for connections')
        servsock.listen(cnum) # listen for connections
        
        dbg('server socket created and now listening. cnum: '+str(cnum)) # debug
        return (servsock,hostaddr) # return socket object
    except socket.error as err:
        dbg('server socket could not be created! :'+str(err),'error') # debug
        historyData.AppendText('Server socket could not be created on '+str(hostaddr)+':'+str(port)+'!\n'+str(err)+'\n')
        return None
    except Exception as err:
        dbg('error encountered trying to create a server socket! :'+str(err), 'error') # debug
        historyData.AppendText('Server Socket encountered an error!')
        return None

# clientSocket()
# Params: port - Port number, hostip - The host to connect to,
# username - the user's username
# Desc: creates a client socket object using the supplied parameters
def clientSocket(port,hostip,username):
    clisock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket object
    
    try:
        if sslEnable:
            # SSL ##########
            dbg('ssl setup...','SSL')
            sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            sslctx.check_hostname = False
            sslctx.verify_mode = ssl.CERT_REQUIRED
            dbg('load default cert','SSL')
            sslctx.load_default_certs()
            sslctx.load_verify_locations('./srv/certificate.pem')
            dbg('load cert chain', 'SSL')
            sslctx.load_cert_chain(certfile='./cli/certificate.pem', keyfile='./cli/key.pem')
            dbg('wrap socket','SSL')
            clisock = sslctx.wrap_socket(clisock)
            dbg('ssl socket created!','SSL')
            # SSL ##########
        
        dbg('connecting to host')
        clisock.connect((hostip,port)) # connect to host
        dbg('enabling keepalive')
        if clisock.getsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE) == 0:
            clisock.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1) # enable keepalive
        dbg('client connected') # debug
        return clisock #return socket object
    except socket.error as err:
        dbg('could not connect to server! :'+str(err),'error') # debug
        historyData.AppendText('Could not connect to server!\n'+str(err)+'\n') # print to history textctrl
        return None
    except ssl.SSLError as err:
        dbg('client ssl error! :'+str(err), 'error') # debug
        historyData.AppendText('Client SSL error!\n')
        return None
    except Exception as err:
        dbg('error encountered trying to create a client socket! :'+str(err), 'error') # debug
        historyData.AppendText('Client Socket encountered an error!')
        return None

# closeSocket()
# Params: sock - teh socket object, noshut - whether we should
# call shutdown or not (default FALSE)
# Desc: closes and shuts down a socket connection
def closeSocket(sock,noshut = False):
    if sock == None: # we only attempt to close socket if it exist
        return
    if not noshut:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except socket.error as err:
            dbg('socket shutdown error: '+str(err))
    sock.close()

# ==============
# Thread Classes
# ==============

# clientHandlerThread() : THREAD
# threading.Thread
# Desc: thread that handles the connection to a client
class clientHandlerThread(threading.Thread):
    # __init__()
    # Desc: class init function
    def __init__(self,ip,port,sock):
        threading.Thread.__init__(self) # initialize thread class
        self.ip = ip # store ip 
        self.port = port # store port
        self.sock = sock # store socket
        self.username = '?' # store client username
        self.daemon = True # make thread daemon
        self.term = False # terminate status
        dbg('client handler thread created!') # debug
    
    # stop()
    # Params: self
    # Desc: terminated the thread
    def stop(self):
        dbg('thread terminate requested') # debug
        self.term = True # terminate thread
    
    # run()
    # Params: self
    # Desc: main thread routine
    def run(self):
        dbg('client handler thread started!') # debug
        
        # main thread loop
        while not self.term:
            global historyData # access global variable historyData
            global userlistData # access global variable userlistData
            global isHost # access global variable isHost
            try:
                self.buffer = str(self.sock.recv(512).decode('utf-8')) # retrieve message sent by client
                if len(self.buffer) > 0: # check if len is not 0
                    dbg('received data from client: '+self.buffer) # debug
                    lock = threading.RLock() # create thread lock
                    lock.acquire(True) # get lock
                    try:
                        # interpret received message
                        # 0 - command message, 1 - regular message
                        # usern_update - update client username
                        # ulist_update - update user names list
                        # ulist_asknew - ask for user list update
                        dbg('interpreting data from client: '+self.buffer) # debug
                        if self.buffer[:1] =='0': # command message
                            dbg('command message') # debug
                            params = self.buffer[1:].split(' ') # split message into keywords
                            if params[0] == 'usern_update': # a username update command
                                dbg('username update') # debug
                                self.username = str(params[1]) # change username
                                updateUsersList(True) # update users list
                            elif params[0] == 'ulist_update': # users list update command
                                dbg('users list update') # debug
                                userlistData.SetValue(str(params[1])) # change users list value
                            elif params[0] == 'ulist_asknew': # ask for a user list update
                                dbg('asking for a user list update') # debug
                                updateUsersList(True) # send users list
                            elif params[0] == 'sock_shutreq': # socket shutdown request
                                if not isHost: # if we are a client
                                    dbg('server requested to close connection') # debug
                                    global frame # access global variable frame
                                    frame.cmdExecute(['/end']) # send a '/end' command to console
                                    dbg('client handler thread terminated.') # debug
                                    return # end thread
                            else: # command does not exist
                                dbg('unknown command','warn') # debug
                        elif self.buffer[:1] == '1': # regular message
                            dbg('regular message') # debug
                            if historyData != '': # if historyData pointer is not empty
                                historyData.AppendText(self.buffer[1:]) # show msg to chat history
                            sendToAll(self.buffer,[self.username]) # echo to other clients
                        else: # invalid message type
                            dbg('unknown message','warn') # debug
                    finally: # release lock
                        lock.release() # release lock
                else: # socket closed
                    break # break out of loop
            except socket.error as err:
                if self.term: # check if we are not asked to terminate
                    break # if yes then break out of loop
        closeSocket(self.sock,isHost) # close client socket
        self.sock = None # clear socket
        self.term = True # set termination to True
        dbg('client handler thread terminated.') # debug
        historyData.AppendText(''+str(self.username)+' disconnected!\n') # show disconnect status
        sendToAll('1'+str(self.username)+' disconnected!\n', [self.username]) # send status to other clients
        updateUsersList(True) # update users list
        return # terminate thread
    
    # send()
    # Params: self
    # Desc: send message to client
    def send(self,data):
        if self.sock != None: # is socket variable is not empty
            dbg('sending to client: '+str(data)) # debug
            try:
                self.sock.send(bytes(str(data), encoding='utf-8')) # send message to client
            except socket.error as err: # could not send message to client
                dbg('could not send message!\n'+str(err),'error') # debug
                # show send error message to chat history
                historyData.AppendText('Cannot send message to '+str(self.username)+'!\n'+str(err)+'\n')
                # client is assumed to be dead so we close connections and terminate thread
                self.stop()

# connectionHandlerThread() : THREAD
# threading.Thread
# Desc: thread handles accepting connections
class connectionHandlerThread(threading.Thread):
    # __init__()
    # Desc: class init function
    def __init__(self,sock):
        threading.Thread.__init__(self) # initialize thread
        self.sock = sock # store sock param
        self.sock.setblocking(0) # set socket to nonblocking
        self.daemon = True # make this thread daemon
        self.term = False # termination status
        dbg('connection handler thread created!') # debug
    
    # stop()
    # Params: self
    # Desc: terminates thread
    def stop(self):
        self.term = True
    
    # run()
    # Params: self
    # Desc: main thread routine
    def run(self):
        dbg('connection handler thread started!') # debug
        clsock,ip,port,user = None,None,None,None # init variables
        global serverclients # access global variable serverclients
        
        # routine loop
        while not self.term: # while not terminating
            # accept connection loop
            while not self.term: # while not terminating
                try:
                    (clsock,(ip,port)) = self.sock.accept() # accept connections
                    dbg('accepted a connection') # debug
        
                    if sslEnable:
                        # SSL ##########
                        dbg('ssl setup...','SSL')
                        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                        sslctx.check_hostname = False
                        sslctx.verify_mode = ssl.CERT_REQUIRED
                        dbg('load default certs', 'SSL')
                        sslctx.load_default_certs()
                        sslctx.load_verify_locations('./cli/certificate.pem')
                        dbg('load cert chain','SSL')
                        sslctx.load_cert_chain(certfile='./srv/certificate.pem', keyfile='./srv/key.pem')
                        dbg('wrap socket','SSL')
                        clsock = sslctx.wrap_socket(clsock, server_side=True)
                        dbg('ssl socket created!','SSL')
                        # SSL ##########
                    
                    break # break loop
                except socket.error as err: # handle socket error
                    if self.term: # if terminating
                        closeSocket(clsock) # close socket
                        dbg('connection handler thread terminated.') # debug
                        return # terminate thread
                except ssl.SSLError as err:
                    dbg('ssl error on connection accept :'+str(err), 'error')
                    historyData.AppendText('SSL error on client connect!\n')
                    return
                except Exception as err:
                    dbg('error on accept :'+str(err), 'error')
                    historyData.AppendText('Error on connection attempt!\n')
                    return # terminate thread
            clsock.setblocking(1) # temporarily set client socket to be blocking
            user = str(clsock.recv(512).decode('utf-8')) # receive initial command from client
            if user[:1] == '0': # if msg is command
                params = user[1:].split(' ') # split text with space as delimiters
                if params[0] == 'usern_update': # if username update command
                    nusername = params[1] # store username
                    clsock.send(bytes('1Welcome '+str(nusername)+'!\n', encoding='utf-8')) # send a welcome message to client
                    if historyData != '': # if historyData pointer is not empty
                        # print status
                        historyData.AppendText(''+str(nusername)+' has joined the chat.\n')
                        sendToAll('1'+str(nusername)+' has joined the chat.\n', [str(nusername)])
                    dbg('connection accepted!') # debug
                    clsock.setblocking(0) # make socket nonblocking
                    if clsock.getsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE) == 0:
                        clsock.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1) # enable keepalive
                    cthread = clientHandlerThread(ip,port,clsock) # create new handler thread
                    cthread.username = nusername # set username for client
                    cthread.start() # start client handler thread
                    lock = threading.RLock() # create lock
                    lock.acquire(True) # get a lock
                    try:
                        serverclients.append(cthread) # add client thread to serverclients array
                    finally:
                        lock.release() # release lock
                else:
                    closeSocket(clsock) # close connection
                    dbg('connection declined! - wrong operation','warn') # debug
            else:
                closeSocket(clsock) # close connection
                dbg('connection declined! - wrong message type','warn') # debug
                dbg(user, 'warn')
        closeSocket(clsock) # close client connection
        dbg('connection handler thread terminated.') # debug
        return # terminate thread 

# ======================
# Main Application Frame
# ======================

# appFrame() : wxFRAME
# wx.Frame
# Desc: application frame class
class appFrame(wx.Frame):
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(500,450)) # create app frame
        
        # application variables
        self.conhandler = None # connections handler thread
        self.servername = 'Debug' # chat server name (only if this is host)
        self.userslist = [] # list of users
        self.socket = None # socket object
        
        # create text boxes
        self.history = wx.TextCtrl(self,style=(wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP)) # history textctrl
        self.users = wx.TextCtrl(self,style=(wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP)) # users textctrl
        self.input = wx.TextCtrl(self,style=(wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB|wx.TE_WORDWRAP)) # input textctrl
        self.input.SetFocus() # set initial focus to input box
        
        # assign pointers to textboxes
        global historyData # access global variable historyData
        global userlistData # access global variable userlistData
        historyData = self.history # set pointer
        userlistData = self.users # set pointer
        
        # create the sizer for the top half of frame
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL) # create sizer
        self.topsizer.Add(self.history,5,wx.EXPAND) # add chat history to top left half of frame
        self.topsizer.Add(self.users,1,wx.EXPAND) # add users list to top right half of frame
        
        #create sizer for the the whole frame
        self.appsizer = wx.BoxSizer(wx.VERTICAL) # create sizer
        self.appsizer.Add(self.topsizer,10, wx.EXPAND) # add top half of frame to main frame sizer
        self.appsizer.Add(self.input,1,wx.EXPAND) # add input box to bottom half of frame
        
        # set event handlers
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter,self.input) # bind OnEnter function to EVT_TEXT_ENTER event
        self.Bind(wx.EVT_CLOSE, self.OnTerminate) # bind OnTerminate function to EVT_CLOSE event
        
        # start help
        self.starthelp = ('Welcome to ChatC!\n\n'
                          'To connect to a server type\n"/join [server ip] [port number]"\n\n'
                          'To host a chat session type\n"/behost [server name] [port number]"\n\n'
                          'Change your username by typing "/username [new username]"\n\n'
                          'For more info about the commands type "/help"\n\n'
                          )
        self.history.AppendText(self.starthelp) # display initial help text to history textctrl
        
        # commands list
        self.cmdlist = ['/help','/join','/behost','/username','/exit','/end']
        if debugMode:
            self.cmdlist = self.cmdlist + ['/dbghost','/dbgjoin']
        
        # init done
        self.SetSizer(self.appsizer) # set the app's sizer
        self.SetAutoLayout(True) # enable automatic layout
        self.Show(True) # show app
        dbg('application started') # debug
        dbg('version info: '+str(sys.version_info))
        if (sys.version_info < (3,6,6)):
            dbg('This application requires Python 3.6.6 or greater', 'warning')
            self.history.AppendText('This application requires Python 3.6.6 or greater\n\n')
    
    # OnTerminate()
    # Params: self, event - provided by event
    # Desc: executes routine for application termination
    def OnTerminate(self,event):
        global isHost # access global variable isHost
        
        # terminate clientHandlerThread threads
        for tc in serverclients: # loop through array
            if isHost:
                tc.send('0sock_shutreq') # send a connection shutdown command
            tc.stop() # stop connection
        
        # terminate connectionHandlerThread thread
        if self.conhandler != None: # if conhandler exist
            self.conhandler.stop() # stop connectionHandlerThread thread
        
        # close socket
        closeSocket(self.socket,isHost) # close the socket
        
        # termination done.
        dbg('exiting...') # debug
        self.Destroy() # destroy application
    
    # cmdExecute()
    # Params: self,keys - array of keywords
    # # Desc: interprets input and executes specified command
    def cmdExecute(self,keys):
        global username # access global variable username
        global isHost # access global variable isHost
        global serverclients # access global variab;e serverclients
        
        dbg(keys[0]) # debug - print keys
        
        if keys[0] == '/help': # display help
            helptext = ("/help - display this help.\n"
                        "/join [server ip] [port] - joins a server.\n"
                        "/behost [server name] [port] - start a chat session.\n"
                        "/behost [server name] [port] [# of clients] [ip to use] - advanced server setup. Useful in case of socket creation errors.\n"
                        "/end - ends a connection or closes the chat session.\n"
                        "/username [username] - change username.\n"
                        "/exit - terminate application.\n"
                        )
            self.history.AppendText(helptext) # write help text to history textctrl
            
        elif keys[0] == '/exit': # exit application
            self.Close() # terminate application
            
        elif keys[0] == '/end': # end chat
            self.history.AppendText('Terminating connection...\n')
            
            # terminate client threads
            for tc in serverclients:
                if isHost:
                    tc.send('0sock_shutreq') # send connection shutdown comand
                tc.stop() # close socket
            # terminate connection handler
            if self.conhandler != None: # if conhandler thread exist
                self.conhandler.stop() # terminate connection handler thread
            # close sockets
            closeSocket(self.socket,isHost) # close socket
            
            # connection close routine done
            time.sleep(0.5) # making sure that timeouts have passed
            self.socket = None # remove socket object
            self.history.AppendText('Connection closed.\n') # print status to history textctrl
            serverclients = [] # clear all client handler threads
            self.conhandler = None # remove conhandler object
            
        elif keys[0] == '/username': # change you username
            if len(keys) == 2: # check if amount of parameters are sufficient
                username = str(keys[1]) # store parameter 1 to variable username
                self.history.AppendText('Your username is now "'+username+'"\n') # print status
                if self.socket != None: # if socket exist
                    if isHost: # if this is host
                        dbg('sending updated userlist to clients') # debug
                        updateUsersList(True) # update the users list
                    else: # we are not host
                        dbg('sending new username to server') # debug
                        self.socket.send(bytes('0usern_update '+username, encoding='utf-8')) # send new username to server
            else:
                # print an error message
                self.history.AppendText('[Info]: New username not provided. Username not changed.\n')
            
        elif keys[0] == '/join' and (self.socket == None): # join a chat session
            if len(keys) == 3: # check if parameters are sufficient
                dbg('joining server...') # debug
                hostip = str(keys[1]) # store parameter 1 to hostname
                port = int(keys[2]) # store parameter 2 to port

                self.socket = clientSocket(port, hostip,username) # create a client socket object
                if self.socket == None: # if socket creation failed
                    dbg('Socket creation failed!','Error')
                    return # return function
                isHost = False # we are not host
                
                dbg('asking to update username')
                self.socket.send(bytes('0usern_update '+str(username), encoding='utf8')) # send a username update command
                
                clihandler = clientHandlerThread(None,None,self.socket) # create a client handler thread to listen to server
                clihandler.username = 'Host'
                clihandler.start() # start thread

                serverclients.append(clihandler) # place in serverclients array - this will be the only thread in the array
                self.socket.send(bytes('0ulist_asknew', encoding='utf-8')) # ask for an updated users list
            else:
                # print error message
                self.history.AppendText('[Error]: Command requires 2 parameters: [host ip] [port]\n')
            
        elif keys[0] == '/behost' and (self.socket == None): # start a chat session
            if len(keys) in [3,4,5]: # check if parameters are sufficient
                dbg('hosting a chat session...') # debug
                self.servername = str(keys[1]) # set servername to parameter 1
                port = int(keys[2]) # store param 2 to port 
                if len(keys) >= 4: # if number of parameters are 3 or more
                    cnum = int(keys[3]) # set param 3 as cnum
                else:
                    cnum = 30 # set default value for cnunm
                if len(keys) == 5:
                    hostip = str(keys[4])
                else:
                    hostip = None
                dbg('starting '+self.servername+' with port '+str(port)+' and max members of '+ str(cnum)) # debug
                self.socket,sockaddr = serverSocket(port,cnum,hostip) # create server socket object
                if self.socket == None: # if socket creation failed
                    return # return function
                self.conhandler = connectionHandlerThread(self.socket) # create connection handler thread
                self.conhandler.start() # start conhandler thread
                # print status
                self.history.AppendText('Chat session "'+self.servername+'" started on '+str(sockaddr[0])+' port '+str(sockaddr[1])+'.\n')
                isHost = True # we are host
            else:
                # print error message
                self.history.AppendText(('[Error]: Command requires at least 2 parameters: "/behost [servername] [port]"\n'
                                         'Advanced setup: "/behost [servername] [port] [number of clients] [host ip]"\n'
                                         ))
        
        elif keys[0] == '/dbghost' and (self.socket == None): # debug host
            dbg('hosting a chat session...')
            dbg('starting debugserver with port 24000 and max members of 30') # debug
            self.socket,sockaddr = serverSocket(24000,30,"localhost") # create server socket object
            if self.socket == None: # if socket creation failed
                    return # return function
            self.conhandler = connectionHandlerThread(self.socket) # create connection handler thread
            self.conhandler.start() # start conhandler thread
            # print status
            self.history.AppendText('Chat session "'+self.servername+'" started on '+str(sockaddr[0])+' port '+str(sockaddr[1])+'.\n')
            isHost = True # we are host

        elif keys[0] == '/dbgjoin' and (self.socket == None): # debug join
            dbg('joining server...') # debug
            self.socket = clientSocket(24000, "localhost",username) # create a client socket object
            if self.socket == None: # if socket creation failed
                dbg('Socket creation failed!','Error')
                return # return function
            isHost = False # we are not host

            dbg('asking to update username')
            self.socket.send(bytes('0usern_update '+str(username), encoding='utf8')) # send a username update command

            clihandler = clientHandlerThread(None,None,self.socket) # create a client handler thread to listen to server
            clihandler.username = 'Host'
            clihandler.start() # start thread

            serverclients.append(clihandler) # place in serverclients array - this will be the only thread in the array
            self.socket.send(bytes('0ulist_asknew', encoding='utf-8')) # ask for an updated users list

        else:
            # print error message
            self.history.AppendText('[Error]: Unknown command\n')
                    
        dbg('op done.') # debug
        return # return function
    
    # OnEnter()
    # Params: self,event - provided by event
    # Desc: handles event when enter is pressed
    def OnEnter(self,event):
        global isHost # access global variable isHost
        
        # enter has been pressed
        inp = self.input.GetValue().lstrip() # strip trailing whitespace from input
        out = '[' + username + ']: ' + inp + '\n' # prepare output
        self.input.Clear() # clear input box
        
        # check if input is command
        if inp[:1] == '/':
            # treat as command
            keys = inp.split(' ') # split text with space as delimeter
            if keys[0] in self.cmdlist: # checks if command is valid
                self.cmdExecute(keys) # executes command
            else: # command is invalid
                #print error message
                self.history.AppendText('[ERROR]: Unknown command.\n')
                dbg('Unknown command.','error') # debug
        else:
            # treat as regular text
            if self.socket == None: # if socket does not exist
                # print error message
                self.history.AppendText('Not in a session and not hosting session.\n')
            else: # if socket exist
                self.history.AppendText(out) # print output to history textctrl
                dbg('sending '+str(out)) # debug
                if isHost: # if host
                    # send to all clients
                    for tc in serverclients:
                        if tc.is_alive(): # if thread is not dead
                            tc.send('1'+str(out)) # send to client
                        else: # do some cleanup
                            tc = None # remove thread
                else: # we are client
                    self.socket.send(bytes('1'+str(out), encoding='utf-8')) # send to server

# ==========================
# Application init and start
# ==========================

# Create and start application and frame
app = wx.App() # create application
frame = appFrame(None,'ChatC') # set frame
app.MainLoop() # run main loop 