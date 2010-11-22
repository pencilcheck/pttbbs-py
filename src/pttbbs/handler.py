# -*- encoding: UTF-8 -*-

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
import datetime
from time import strftime, localtime

import db
import screen
import screenlets
from utility import Dimension


class Routine:
    def __init__(self, address):
        self.id = ""
        self.address = address
        self.acl = 0

        self.stillAlive = True
        self.stack = ViewStack()
        self.encoding = u'big5'
        self.width = 80
        self.height = 24
        self.focusLine = 0
        self.focusColn = 0

    def initialize(self):
        print "Routine initializing"
        self.stack.push(screenlets.login(self, Dimension(0, 0, self.width, self.height)))

        #self.stack.push(screenlets.encoding(self, Dimension(self.height / 2 - 3, 0, self.width, self.height)))
        #dimension = Dimension(line=self.height / 2 - 3, coln=0, width=self.width, height=self.height)
        #self.stack.push(screenlets.resolution(self, dimension))

    # update screenlets and return 1 if needed clear screen (e.g. screenlet switching)
    def update(self, data=''):
        return self.stack.peek().update(data)

    # force will redraw all
    def draw(self, force=False):
        return self.stack.peek().draw(force).encode(self.encoding) + screen.move_cursor(self.focusLine, self.focusColn)

    def resetFocus(self):
        self.focusLine = -1
        self.focusColn = -1

    def setWidth(self, width):
        self.width = width

    def setHeight(self, height):
        self.height = height

    def disconnect(self):
        # record before leaving

        self.stillAlive = False

    def getOnlineCount(self):
        return 0

    def getTime(self, time=localtime()):
        #print strftime("%m/%d %a %Y %H:%M", time)
        return strftime("%m/%d %a %Y %H:%M", time)

    def createSession(self):
        print "creating session at", datetime.datetime.today() 
        t = (self.id, self.address[0], self.address[1], datetime.datetime.today())
        db.instance.cursor.execute('update Sessions set UId=?, IP=?, Port=?, LoginTime=?', t)
        db.instance.commit()
        """
        tmp = [(strftime("%a, %d %b %Y %H:%M:%S", localtime()),self.me[0])]
        dict = (pickle.dumps(tmp),userid,)
        tmp = pickle.loads(str(row[2]))
        tmp.append((strftime("%a, %d %b %Y %H:%M:%S", localtime()),self.me[0]))
        dict = (pickle.dumps(tmp),userid,)
        db.instance.cursor.execute('update Users set IPs=? where UId=?', dict)
        db.instance.commit()
        """

    # return True means good, False means bad
    def userLookup(self, userid, password):
        print 'looking up account for', userid, password
        """
        if self.id == "guest":
            db.instance.cursor.execute('select * from Users where UId=?', (self.id,))
            for row in db.instance.cursor:
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
        """
        db.instance.cursor.execute('select * from Users')
        for row in db.instance.cursor:
            print row

        t = (userid,password,)
        db.instance.cursor.execute('select * from Users where UId=? and PW=?', t)
        for row in db.instance.cursor:
            return True
        return False

    def loadAnnouncement(self):
        print "load Announcement"

        l = []

        for line in open('announce.txt'):
            print line
            l.append(line)

        return l

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
        try:
            print "popping", self.view_stack[-1]
            return self.view_stack.pop()
        except:
            return None
