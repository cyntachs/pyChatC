# Python chat program

A simple chat program.


## Commands list

/behost - hosts a chat server

usage: `/behost [server name] [port]`

advanced setup:

`/behost [server name] [port] [number of clients] [ip address to use]`

/join - joins a chat server

usage: `/join [server ip] [port]`

/end - ends connection

usage: `/end`

/help - shows a list of commands and their uses.

usage: `/help`

/username - change your username

usage `/username [new username]`

 *(Note that your username should not have any spaces)*

/exit - terminates application

usage: `/terminate`

 *(Note that existing connections would be closed)*


*Note: Instructions are assuming a Windows operating system. For other OS, please adapt as needed.*


## Pre-Execution

This application was coded in Python version 3.6.6 release.

Your machine needs to have Python 3.6.6 installed, you can
[get Python here](https://www.python.org/). Make sure to
download the 3.X versions of Python.
Instructions on how to install: <https://docs.python.org/2/using/>

Install the Python interpreter wherever you like. Make sure
to remember where it is installed since it would be useful
when you need to run Python in the command prompt. If during
the installation the installer asks to add Python to the PATH
environmental variable please do so. If not then you can add
the Python interpreter directory manually:
https://www.google.com/?gws_rd=ssl#q=add+a+directory+to+path

Once Python is installed you would need to install the
wxPython module which can be found here: 
http://www.wxpython.org/
A 64 bit wxPython for Python 3.6.6 is required.

The installer should easily guide you through the
installation. Just tell it where Python is installed and
it should be able to handle the rest.


## Running the application

You can run the application using the provided run.cmd file
or by entering `pythonw.exe main.py` in the command prompt.
If *.py files are associated to your python interpreter you
could also run the application by double clicking the main.py
file.


## Starting a server

To start a server, type:

`/behost [a name for the server] [port to use]`

ex:

`/behost chatserver 9200`

The port provided must not be already used or the server will fail
to bind to the port.
The application will say when the server has been created.

To join a server, type:

`/join [the server's ip address] [port number]`

ex:

`/join 64.187.254.20 9200`

The client will attempt to connect to the server. If the connection
fails it will show the reason why. Note that you cannot use this 
if you are already connected or is hosting the server. 

To end the connection type:

`/end`

This will close the server if you are a server or disconnect from
the server if you are a client. This will now allow you to use 
`/join` and `/behost` again.

To terminate the application you can type:

`/exit`


## Once in a chat session

Message exchange is the same as any other chat program. Just type in
a message in the input box and press enter. Everyone connected will 
receive the message. You can change your username by typing:

`/username [your new username]`


## Other Blurbs

The application was previously developed in Eclipse with pyDev.

Eclipse:    https://eclipse.org/
pyDev:      http://marketplace.eclipse.org/node/114

Current application development is done with Visual Studio Code with the VS Code Python Extension by Microsoft.

VS Code:    https://code.visualstudio.com/

This application support multiple clients up to a 
default max of 30 clients. You can change the number
of clients with the `/behost` command by typing:
`/behost [server name] [port] [number of clients] [ip address to use]`

Application does not automatically perform any port
forwarding so trying to make two clients run in a
nested network will not work. Both clients should be
present in the same network to avoid connection problems.

Designed and tested using Python 3.6.6 release version.
GUI created using wxPython 3.0-msw. Socket and threading 
classes are python standard libraries.

Tested in Windows 10 x64. Not tested in other platforms 
but should still theoretically work. Bugs in the code 
may be present, but most of the easily recognizable bugs
should have been dealt with already.

To run without spawning a command prompt use run.cmd or
enter in command line: `pythonw.exe main.py`. Make sure
your python bin directory is present in your system
PATH environment variable. That should make it easy to
run python programs in the command prompt.

Set variable debugMode to True to see debugging messages.
Set printToHistory to True to see debugging messages
printed in the chat history text box.

Q: How did the name came to be?
A: pychat -> yChat -> Chaty -> Chatsy -> ChatC


```txt
   If you have read all the Terms and Agreements and accept it
   choose YES below.
-----------------------------------------------------------------
|        I Accept the Terms and Agreements:  [ ] Yes   [ ] No   |
-----------------------------------------------------------------
```