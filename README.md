
# Simple File Transfer System

## Overview
This system consists of a server and client component designed to facilitate basic file transfer operations, including uploading and downloading files between a client and server over a network.

## Features
- **Server**: Handles incoming connections, processes commands for file retrieval (download) and storage (upload), and manages data transmission.
- **Client**: Initiates requests for file operations, receives server responses, and handles file download or upload procedures.

## Requirements
- Python 3.x
- Basic understanding of network programming and socket API

## Installation
1. Clone or download the repository containing the server and client code.
2. Ensure Python 3.x is installed on both the server and client machines.

## Usage

### Server
To start the server, run the following command in a terminal:
```
python server.py
```
The server will listen for incoming connections and respond to client requests.

### Client
To interact with the server, run the client script from another terminal:
```
python client.py
```
Upon starting, the client will connect to the server and present an interface for sending commands.

#### Supported Commands

1. **USER**: Sets the username for authentication, preparing the system for user login.
2. **PASS**: Provides the password for the specified user, used in conjunction with `USER` for authentication.
3. **LIST** or **LS**: Lists the contents of the current or specified directory, showing files and directories.
4. **RETR**: Downloads a file from the server to the client.
5. **STOR**: Uploads a file from the client to the server.
6. **MKD** or **MKDIR**: Creates a new directory in the current working directory.
7. **RMD** or **RMDIR**: Removes a directory if it is empty.
8. **PWD**: Displays the current working directory of the server.
9. **CDUP**: Moves the current working directory to the parent directory.
10. **CWD** or **CD**: Changes the current working directory to a specified path.
11. **DELE** or **RM**: Deletes a file from the server.
12. **QUIT**: Closes the connection and ends the session.
13. **REPORT**: Generates a report of server activity, useful for administrative purposes.
14. **HELP**: Provides information on available commands and their usage.


## Configuration
- The server and client IP addresses and port numbers can be configured in the respective scripts.
- Ensure the server script is running before attempting to connect with the client.

