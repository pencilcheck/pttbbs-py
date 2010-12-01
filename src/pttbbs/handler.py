# -*- encoding: UTF-8 -*-

import pickle
import datetime
from time import strftime, localtime
import codecs

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

    def initialize(self):
        print "Routine initializing"
        self.stack.push(screenlets.login(self, Dimension(0, 0, self.width, self.height)))
        '''
        # testing
        self.stack.push(screenlets.boardlist(self, Dimension(0, 0, self.width, self.height), '/boards'))
        '''

    # update screenlets and return 1 if needed clear screen (e.g. screenlet switching)
    def update(self, data=''):
        return self.stack.peek().update(data)

    # force will redraw all
    def draw(self, force=False):
        return self.stack.peek().draw(force).encode(self.encoding)

    def setWidth(self, width):
        self.width = width

    def setHeight(self, height):
        self.height = height

    def disconnect(self):
        # record before leaving

        self.stillAlive = False

    def getOnlineCount(self):
        return 0

    def time(self, time=localtime()):
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

        for line in codecs.open('announce.txt', 'r', 'utf-8'):
            print line, repr(line)
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

    # loads boards with given cwd
    def loadBoards(self, cwd):
        print "loadBoards", cwd
        if cwd == "":
            return []

        query = (cwd + '%',)
        try:
            db.instance.cursor.execute("select * from Boards where Path LIKE ?", query)
            tmp = []
            for record in db.instance.cursor:
                print record
                tmp.append(record[1])
            return tmp
        except:
            print "db execution error"
            return []

    def addBoard(self, path, title):
        print "adding board", title, "to", path

        board = (path, title, self.id, datetime.datetime.today(),)
        try:
            db.instance.cursor.execute('insert into Boards (Path, Title, CreatorId, CreationDate) VALUES (?, ?, ?, ?)', board)
            db.instance.commit()
        except Exception as e:
            print "exception:", e
            return 0
        return 1

    # loads threads with given cwd
    def loadThreads(self, cwd):
        print "loadThreads", cwd
        if cwd == "":
            return []

        query = (cwd + '%',)
        try:
            db.instance.cursor.execute("select * from Threads where Path LIKE ?", query)
            tmp = []
            for record in db.instance.cursor:
                print record
                tmp.append(record[1])
            return tmp
        except Exception as e:
            print "exception:", e
            return []

    def addThread(self, path, title, content):
        print "adding thread", title, "to", path, "with", repr(content)

        thread = (path, title, self.id, content, datetime.datetime.today(),)
        try:
            db.instance.cursor.execute('insert into Threads (Path, Title, AuthorId, Content, CreationDate) VALUES (?, ?, ?, ?, ?)', thread)
            db.instance.commit()
        except Exception as e:
            print "exception:", e
            return 0
        return 1

    def loadThread(self, cwd):
        print "loadThread", cwd
        if cwd == "":
            return []

        query = (cwd,)
        try:
            db.instance.cursor.execute("select * from Threads where Path = ?", query)

            return db.instance.cursor.fetchone()[3] #content
        except Exception as e:
            print "exception:", e
            return []

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
