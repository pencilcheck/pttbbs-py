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

class BBS:
    
    def __init__(self, ip):
        self.view_stack = []
        self.view_cache = []
        self.me = ip
        self.id = ""
        
    # need a method to put into event loop in interval for animation stuff
    def update(self):
        return
    
    def cleanup(self):
        return
    
    def dataReceived(self, data):
        self.view_stack[-1].update(data)
    
    def push(self, screenlet, term, selfdestruct=False):
        if selfdestruct: # pop the caller
            self.view_stack.pop(False)
        """
        if screenlet.__class__.__name__ in self.view_cache:
            self.view_stack.append(self.view_cache[screenlet.__class__.__name__])
        else:
            self.view_stack.append(screenlet())
        """
        term.clr_scr()
        self.view_stack.append(screenlet(term, self))
        self.view_stack[len(self.view_stack)-1].update()
    
    def pop(self, show=True):
        self.view_stack.pop(False)
        #self.view_cache[self.view_stack[len(self.view_stack)-1].__class__.__name__] = self.view_stack.pop()
        if show:
            self.view_stack[len(self.view_stack)-1].buff.clr_scr()
            self.view_stack[len(self.view_stack)-1].update()
        
        
        
    # ------------------------------------------
    # below are functions for screenlets to db
    
    
    def user_lookup(self, userid, password):
        print 'looking up account for this guy', self.me
        
        if userid == "guest":
            db.instance.cursor.execute('select * from users where UId=?', (userid,))
            for row in db.instance.cursor:
                print repr(row[2])
                if row[2] == None:
                    tmp = [(strftime("%a, %d %b %Y %H:%M:%S", localtime()),self.me[0])]
                    dict = (pickle.dumps(tmp),userid,)
                else:
                    tmp = pickle.loads(str(row[2]))
                    tmp.append((strftime("%a, %d %b %Y %H:%M:%S", localtime()),self.me[0]))
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