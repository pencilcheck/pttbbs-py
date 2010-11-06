# -*- encoding: UTF8 -*-

## Ptt BBS python rewrite
##
## This is the controller of MVC architecture
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

from time import sleep
from time import clock

import db

me = '127.0.0.1'

view_stack = []
view_cache = []
        
lookup = [{}]
    
# need a method to put into event loop in interval for animation stuff
def update():
    return

def cleanup():
    return

def dataReceived(data):
    view_stack[-1].update(data)

def setMe(ip):
    me = ip

def push(screenlet):
    if screenlet.__class__.__name__ in view_cache:
        view_stack.append(view_cache[screenlet.__class__.__name__])
    else:
        view_stack.append(screenlet())
    view_stack[len(view_stack)-1].update()

def pop():
    view_cache[view_stack[len(view_stack)-1].__class__.__name__] = view_stack.pop()
    view_stack[len(view_stack)-1].update()
    
    
    
# ------------------------------------------
# below are functions for screenlets to db


def user_lookup(userid, password):
    print 'looking up account for this guy', me
    
    db.instance
    
    return 0