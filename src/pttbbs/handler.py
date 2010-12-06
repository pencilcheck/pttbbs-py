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

    def time(self, time):
        #print strftime("%m/%d %a %Y %H:%M", time)
        return time.strftime("%m/%d %a %Y %H:%M")

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

    # loads boards with given cwd
    def loadBoards(self, id):
        print "loadBoards", id
        query = (id,)
        try:
            if id == None:
                db.instance.cursor.execute("select rowid, Title from Boards where BoardId IS NULL")
            else:
                db.instance.cursor.execute("select rowid, Title from Boards where BoardId = ?", query)
            tmp = []
            for record in db.instance.cursor:
                print record
                tmp.append((record[0], record[1]))
            return tmp
        except Exception as e:
            print "exception:", e
            return []

    def addBoard(self, id, title):
        print "adding board", title

        board = (id, title, self.id, datetime.datetime.today(),)
        try:
            db.instance.cursor.execute('insert into Boards (BoardId, Title, CreatorId, CreationDate) VALUES (?, ?, ?, ?)', board)
            db.instance.commit()
        except Exception as e:
            print "exception:", e
            return 0
        return 1

    # loads threads with given boardid
    def loadThreads(self, id):
        print "loadThreads"
        #query = (cwd + '%',)
        query = (id,)
        try:
            db.instance.cursor.execute("select rowid, Title from Threads where BoardId = ?", query)
            tmp = []
            for record in db.instance.cursor:
                print record
                tmp.append((record[0], record[1]))
            return tmp
        except Exception as e:
            print "exception:", e
            return []

    def addThread(self, id, title, content):
        print "adding thread", title, repr(content)

        thread = (id, title, self.id, content, datetime.datetime.now(),)
        try:
            db.instance.cursor.execute('insert into Threads (BoardId, Title, AuthorId, Content, CreationDate) VALUES (?, ?, ?, ?, ?)', thread)
            db.instance.commit()
        except Exception as e:
            print "exception:", e
            return 0
        return 1

    def loadThread(self, id):
        print "load thread id:", id

        query = (id,)
        try:
            db.instance.cursor.execute("select * from Threads where rowid = ?", query)
            fetch = db.instance.cursor.fetchone()
            print fetch
            header = [u"標題：" + fetch[1].strip("\n") + "\n" + u"作者：" + fetch[2].strip("\n") + "\n" + u"時間：" + self.time(fetch[5])]
            print "header", header

            content = [fetch[3]]
            print "content", content

            db.instance.cursor.execute("select * from Replies where ThreadId = ?", query)
            print "replies"
            replies = []
            for record in db.instance.cursor:
                replies.append(u"推 " + record[1].strip("\n") + "：" + record[2].strip("\n"))

            user = (self.id,)
            db.instance.cursor.execute("select Signature from Users where UId = ?", user)
            user = db.instance.cursor.fetchone()
            print "user", user
            footer = [user[0] if user[0] != None else ""]
            sep = ["----------------------------\n"]
            return "\n".join(header + sep + content + sep + replies + footer)
        except Exception as e:
            print "exception:", e
            return ""

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
