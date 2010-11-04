# -*- encoding: BIG5 -*-

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

from twisted.internet import protocol, reactor
from twisted.conch import telnet

import colors 
from colors import Colors
from colors import Align
import terminfo
import screens



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


class BBS(telnet.Telnet):
    
    def setLineMode(self, enable):
        if enable:
            self.requestNegotiation(telnet.LINEMODE, telnet.LINEMODE_EDIT + '\x01') # enable line buffer mode
        else:
            self.requestNegotiation(telnet.LINEMODE, telnet.LINEMODE_EDIT + '\x00') # disable line buffer mode
            
    def connectionMade(self):
        #self.do(telnet.LINEMODE) # disable line buffer mode
        self.factory.connections = self.factory.connections + 1
        
        screens.loginScr(self)
        
    def enableRemote(self, option):
        print 'enableRemote', repr(option)
        return option == telnet.LINEMODE

    def disableRemote(self, option):
        print 'disableRemote', repr(option)
        
    def applicationDataReceived(self, data):
        print "data:", repr(data)
            
        
    def connectionLost(self, reason):
        print reason
        self.factory.connections = self.factory.connections - 1
        
class BBSFactory(protocol.ServerFactory):
    
    protocol = BBS
    
    def __init__(self):
        self.connections = 0
    

reactor.listenTCP(args.port, BBSFactory())
reactor.run()
 