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
import screenlets

class Routine:
    
    def __init__(self):
        self.stack = ViewStack()
        self.encoding = 'utf8'
        self.width = 80
        self.height = 24
        
    def initialize(self):
        print "Routine initializing"
        #encoding = screenlets.encoding(self, 0, 0)
        
        self.stack.push(screenlets.login(self, 0, 0, self.width, self.height))
        self.stack.push(screenlets.encoding(self, self.height / 2 - 3, 0, self.width, self.height))
        #self.stack.push(screenlets.resolution(self, self.height / 2 - 3, 0, self.width, self.height))
    
    # if update return 1 needs to clear screen
    def update(self, data=''):
        print "Routine updating"
        # update self.buffer and return it
        return self.stack.peek().update(data)
            
    def draw(self):
        print "Routine drawing"
        return self.stack.peek().draw().encode(self.encoding)
    
    def setWidth(self, width):
        self.width = width
    
    def setHeight(self, height):
        self.height = height
    
    def getOnlineCount(self):
        return 0
    
    def getTime(self):
        #print strftime("%m/%d %a %Y %H:%M", localtime())
        return strftime("%m/%d %a %Y %H:%M", localtime())
    
    def user_lookup(self, userid, password):
        print 'looking up account for this guy', self.me
        
        self.id = userid
        
        if userid == "guest":
            db.instance.cursor.execute('select * from Users where UId=?', (userid,))
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
                db.instance.cursor.execute('update Users set IPs=? where UId=?', dict)
                db.instance.commit()
                return 0
        else:
            # Do this instead
            t = (userid,password,)
            db.instance.cursor.execute('select * from Users where UId=? and PW=?', t)
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
                db.instance.cursor.execute('update Users set IPs=? where UId=?', dict)
                db.instance.commit()
                return 0
        return -1
    
    def loadPathFunction(self):
        print "loadPathFunction"
        print "path", self.path
        query = (self.path,)
        try:
            db.instance.cursor.execute('select * from BoardFileSystem where Path = ?', query)
            tmp = []
            
            for line in db.instance.cursor:
                print line
                tmp.append(line)
                
            function = str(tmp[0][3])
            print function
            return function
        except:
            pass
    
    # loads board content at given level and index, either board list or thread list or threads
    def loadBoardList(self):
        print "loadBoardList"
        if self.path == None or self.path == "":
            query = (0,)
            try:
                '''
                db.instance.cursor.execute("select * from BoardFileSystem")
                for line in db.instance.cursor:
                    print line
                '''
                db.instance.cursor.execute("select * from BoardFileSystem where Path LIKE \'_\' and Type = ?", query)
                tmp = []
                for line in db.instance.cursor:
                    #print line
                    tmp.append(line)
                    
                result = [item[4].encode('BIG5') for item in tmp]
                #print result
                return result
            except:
                print "db execute error"

        else:
            print "path", self.path
            query = (self.path + '-' + '%', 0,)
            try:
                db.instance.cursor.execute("select * from BoardFileSystem where Path LIKE ? and Type = ?", query)
                tmp = []
                for line in db.instance.cursor:
                    print line
                    tmp.append(line)
                    
                result = [item[4].encode('BIG5') for item in tmp]
                print result
                return result
            except:
                print "db execute error"

class ViewStack:
    # each element in the stack is a tuple ((x, y, width, height), screenlet)
    # the size is set by Routine
    def __init__(self):
        self.view_stack = []
        self.view_cache = []
    
    def peek(self):
        print "peek", self.view_stack[-1]
        return self.view_stack[-1]
    
    def push(self, screen):
        print "pushing", screen, "to the stack"
        """
        if screenlet.__class__.__name__ in self.view_cache:
            self.view_stack.append(self.view_cache[screenlet.__class__.__name__])
        else:
            self.view_stack.append(screenlet())
        
        
        if screen == None: # pushing predefined in the db
            screen = screenlets.evalString(self.loadPathFunction())
        """
        self.view_stack.append(screen)
    
    def pop(self):
        if len(self.view_stack) > 0:
            return self.view_stack.pop()
            #self.view_cache[self.view_stack[len(self.view_stack)-1].__class__.__name__] = self.view_stack.pop()
        return None