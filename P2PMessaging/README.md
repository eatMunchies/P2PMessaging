# P2PMessaging
P2P Messaging App made via Python (socket, threading, and other libraries) for CPE 400 (UNR S24)

# Description
This repository contains the code for a P2P messaging app. It was created in an object oriented fashion to encapsulate various functionalities of the app within classes. 

The main workhorse of the application is in client.py, which handles client communications via the socket and threading library. Since it is a P2P app, this client essentially works as a mini server that receives messages from outside requests and as a regular client that allows the user to send message requests to other places. 

Conversation histories are stored both within a live conversation via the LiveConnection class and persistently in memory between conversations via the HashTable class. I plan to add local saving and loading of conversation histories so that clients can remember conversations with people just like a regular non-P2P messaging application. 

The user interface is a CLI for development purposes. Further versions of the project will replace the CLI with a dedicated GUI. 

# How to Use
Ensure you have python installed. All relevant libraries should be included in the Python Standard Library, so I do not think you should have to install anything extra. 

Once you have the repository cloned or you copied the files, you can just run the following command in the /src directory to run the application:

python3 runner.py

You now have access to the CLI for the application!

# Author
Anthony Silva
UNR