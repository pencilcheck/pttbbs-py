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


class BBS:

    def __init__(self, t, d):
        self.term = t
        self.db = d
        
        self.view_stack = []
        self.view_cache = []
        
        lookup = [{}]
    
    # need a method to put into event loop in interval for animation stuff
    def update(self):
        return
    
    def cleanup(self, ip):
        return
    
    def dataReceived(self, data):
        self.view_stack[-1].update(data)
    
    def loadExtScreenlets(self):
        return
    
    def push(self, screenlet):
        inst = screenlet(self.term)
        if inst.__class__.__name__ in self.view_cache:
            self.view_stack.append(self.view_cache[inst.__class__.__name__])
        else:
            self.view_stack.append(inst)
        self.view_stack[len(self.view_stack)-1].update()
    
    def pop(self):
        self.view_cache[self.view_stack[len(self.view_stack)-1].__class__.__name__] = self.view_stack.pop()
        self.view_stack[len(self.view_stack)-1].update()
    
    
    
    # ------------------------------------------
    # below are functions for screenlets to db
    
    
def check_userid(userid):
    return