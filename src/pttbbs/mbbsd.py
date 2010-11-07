# -*- encoding: UTF8 -*-

## Ptt BBS python rewrite
##
## Author: Penn Su <pennsu@gmail.com>
## 
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import sys
import bbs
import db
import term
import screenlet

import gevent
from gevent import socket

#import mbbsd

# Parse program arguments
parser = argparse.ArgumentParser(description='ptt BBS server daemon.')

parser.add_argument('-d', '--daemon', action='store_true', help='Launch in Daemon mode')
parser.add_argument('-t', '--tunnel', help='Tunnel Mode', default='telnet')
parser.add_argument('-p', '--port', help='Listen port', type=int, default='9090')
parser.add_argument('-b', '--base', help='Host url', default='127.0.0.1')
#parser.add_argument('-e', '--encode', help='Character Encoding', default='big5')

args = parser.parse_args()

## Telnet Commands (not complete)
NULL    =   chr(0)      # No operation.
BEL     =   chr(7)      # Produces an audible or visible signal (which does NOT move the print head).
BS      =   chr(8)      # Moves the print head one character position towards the left margin.
HT      =   chr(9)      # Moves the printer to the next horizontal tab stop. It remains unspecified how either party determines or
                        # establishes where such tab stops are located.
#chr(10):'LF',       # Moves the printer to the next print line, keeping the same horizontal position.
#chr(11):'VT',       # Moves the printer to the next vertical tab stop.  It remains unspecified how either party determines or
                    # establishes where such tab stops are located.
#chr(12):'FF',       # Moves the printer to the top of the next page, keeping the same horizontal position.
#chr(13):'CR',       # Moves the printer to the left margin of the current line.
ECHO    =   chr(1)      # User-to-Server:  Asks the server to send Echos of the transmitted data.
#chr(3):'SGA',       # Suppress Go Ahead.  Go Ahead is silly and most modern servers should suppress it.
NAWS    =   chr(31)     # Negotiate About Window Size.  Indicate that information about the size of the terminal can be communicated.
LINEMODE=   chr(34)     # Allow line buffering to be negotiated about.
#chr(240):'SE',      # End of subnegotiation parameters.
#chr(241):'NOP',     # No operation.
#chr(242):'DM',      # "Data Mark": The data stream portion of a Synch.  This should always be accompanied by a TCP Urgent notification.
#chr(243):'BRK',     # NVT character Break.
#chr(244):'IP',      # The function Interrupt Process.
#chr(245):'AO',      # The function Abort Output
#chr(246):'AYT',     # The function Are You There.
#chr(247):'EC',      # The function Erase Character.
#chr(248):'EL',      # The function Erase Line
#chr(249):'GA',      # The Go Ahead signal.
SB      =   chr(250)    # Indicates that what follows is subnegotiation of the indicated option.
WILL    =   chr(251)    # Indicates the desire to begin performing, or confirmation that you are now performing, the indicated option.
WONT    =   chr(252)    # Indicates the refusal to perform, or continue performing, the indicated option.
DO      =   chr(253)    # Indicates the request that the other party perform, or confirmation that you are expecting the other party to perform, the indicated option.
DONT    =   chr(254)    # Indicates the demand that the other party stop performing, or confirmation that you are no longer expecting the other party to perform, the indicated option.
IAC     =   chr(255)    # Data Byte 255.  Introduces a telnet command.

def filter(data):        
    if chr(255) == data[0]:
        print 'probably IAC'
        data = ""
    elif chr(255) in data:
        data.replace('\xff', '')
    
    return data

def handle_socket(sock):
    try:
        sock.send(IAC + DO + LINEMODE) # tell client to disable linemode
        sock.send(IAC + WILL + ECHO) # tell client to not echo
        sock.sendall("Connecting...")
        
        conn = bbs.BBS(sock.getpeername())
        
        # push the login screenlet
        conn.push(screenlet.login, term.Term(sock))
        
        sock.recv(4096)

        
        while True:
            data = sock.recv(3) # 4096 bytes buffer
            if not data:
                break
            
            conn.dataReceived(data)
            print "sending from client", sock, repr(data)
            #sock.sendall(data) # this is a simple echo sock :)
    except:
        pass
    sock.close()
 
print "setting up socket"
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
server.bind(('', 9090))
server.listen(500)
print "listening for backlog 500"
while True:
    try:
        new_sock, address = server.accept()
    except KeyboardInterrupt:
        break

    # handle every new connection with a new coroutine
    gevent.spawn(handle_socket, new_sock)