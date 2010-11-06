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

import pickle
from time import strftime, localtime

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

def push(screenlet, selfdestruct=False):
    if selfdestruct: # pop the caller
        view_stack.pop()
    if screenlet.__class__.__name__ in view_cache:
        view_stack.append(view_cache[screenlet.__class__.__name__])
    else:
        view_stack.append(screenlet())
    view_stack[len(view_stack)-1].update()

def pop(show=True):
    view_cache[view_stack[len(view_stack)-1].__class__.__name__] = view_stack.pop()
    if pop:
        view_stack[len(view_stack)-1].update()
    
    
    
# ------------------------------------------
# below are functions for screenlets to db


def user_lookup(userid, password):
    print 'looking up account for this guy', me
    
    if userid == "guest":
        db.instance.cursor.execute('select * from users where UId=?', (userid,))
        for row in db.instance.cursor:
            print repr(row[2])
            if row[2] == None:
                tmp = [(strftime("%a, %d %b %Y %H:%M:%S", localtime()),me)]
                dict = (pickle.dumps(tmp),userid,)
            else:
                tmp = pickle.loads(str(row[2]))
                tmp.append((strftime("%a, %d %b %Y %H:%M:%S", localtime()),me))
                dict = (pickle.dumps(tmp),userid,)
            print dict
            db.instance.cursor.execute('update users set IPs=? where UId=?', dict)
        
        # update acl
        acl = 0
    else:
        # Do this instead
        t = (userid,password,)
        db.instance.cursor.execute('select * from users where UId=? and PW=?', t)
        for row in db.instance.cursor:
            print row
        
        # update acl
        acl = 0
    db.instance.commit()
    
    return 0