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
import inspect

from twisted.internet import protocol, reactor
from twisted.conch import telnet

import bbs
import db
import term
import screenlet


# Parse program arguments
parser = argparse.ArgumentParser(description='ptt BBS server daemon.')

parser.add_argument('-d', '--daemon', action='store_true', help='Launch in Daemon mode')
parser.add_argument('-t', '--tunnel', help='Tunnel Mode', default='telnet')
parser.add_argument('-p', '--port', help='Listen port', type=int, default='9090')
parser.add_argument('-b', '--base', help='Host url', default='127.0.0.1')
parser.add_argument('-e', '--encode', help='Character Encoding', default='big5')

args = parser.parse_args()

print args
print args.base

# Database connection
db.load()

# Set up server protocol
class Protocol(telnet.Telnet):
        
    def setLineMode(self, enable):
        if enable:
            self.requestNegotiation(telnet.LINEMODE, telnet.LINEMODE_EDIT + '\x01') # enable line buffer mode
        else:
            self.requestNegotiation(telnet.LINEMODE, telnet.LINEMODE_EDIT + '\x00') # disable line buffer mode
            
    def connectionMade(self):
        #self.do(telnet.LINEMODE) # disable line buffer mode
        
        self.factory.connections = self.factory.connections + 1    
        
        self.b = bbs.BBS(term.Term(self), db)
        
        # BBS load external templates
        self.b.loadExtScreenlets()
        
        self.b.push(screenlet.login) # push the login screenlet
        
    def enableRemote(self, option):
        print 'enableRemote', repr(option)
        return option == telnet.LINEMODE

    def disableRemote(self, option):
        print 'disableRemote', repr(option)
        
    def applicationDataReceived(self, data):
        print "data:", repr(data)
        #bbs.dataReceived(data)
            
        
    def connectionLost(self, reason):
        print reason
        self.factory.connections = self.factory.connections - 1
        #bbs.cleanup(self.transport.getHost().host)

class BBSFactory(protocol.ServerFactory):
    
    protocol = Protocol
    
    def __init__(self):
        self.connections = 0
    

# run the server
factory = BBSFactory()

reactor.listenTCP(args.port, factory)
reactor.run()
 