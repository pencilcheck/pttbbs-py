# -*- encoding: BIG5 -*-

## Ptt BBS python rewrite
##
## This is the view of MVC architecture extended from term
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

import struct

from twisted.internet import reactor, defer

from time import localtime
from time import sleep
from time import clock

from term import Term
from term import Colors
from term import Align

import bbs # controller

class screenlet(object):
    def __init__(self, t):
        self.state = 0
        self.billboard = []
        self.header = []
        self.content = []
        self.footer = []
        self.term = t

    def update(self, data=''):
        # turn off line buffer mode
        self.term.setLineMode(False)


class login(screenlet):
    def __init__(self, t):    
        self.id = ''
        self.pw = '' 
        
        self.state = 0
        self.maxLen = 13
        
        super(login, self).__init__(t)
    
    def drawScr(self, dir):
        self.term.clr_scr()
        for i, line in enumerate(open(dir).readlines()):
            self.term.put(i+1, 0, line)
    
    def drawWelcomeScr(self, n):
        self.term.clr_scr()
        for line in open("../res/Welcome").readlines():
            self.put((22, 0, line))
            
    def drawRegisteredScr(self, n):
        self.term.clr_scr()
        for i, line in enumerate(open("../res/registered").readlines()):
            self.put((i+1, 0, line))
            
    def drawRegisterScr(self, n):
        self.term.clr_scr()
        for line in open("../res/register").readlines():
            self.put((22, 0, line))
            
    def drawBirthScr(self, n):
        self.term.clr_scr()
        for line in open("../res/Welcome_birth." + n).readlines():
            self.put((24, 0, line))
            
    def drawLoginScr(self, n):
        self.term.clr_scr()
        for line in open("../res/Welcome_login").readlines():
            self.term.put(24, 0, line)
    
    
    # the methodology behind this is always static first, always the lowest layer first, think of layers, paint the least
    # dynamic layer first
    def update(self, data=''):
        
        # clear the screen
        self.drawScr("../res/Welcome_birth.12")
        
        # quote of the day
        self.term.put(22, 0, "Quote of the Day - Blah Balh!?")
    
        # draw user input field
        self.term.put(21, 0, "請輸入代號，或以 guest 參觀，或以 new 註冊: ")
        
        if data == '\r': # return pressed
            if self.state == 0: # user id
                if bbs.check_userid(self.id) == 0: # 0 success
                    self.state = 1 # now check password
            else: # password
                if bbs.check_pw(self.pw) == 0:
                    #bbs.BBS.push() # push in next screenlet 
                    return
        elif len(data) == 1 and struct.pack("c", data) == '\x7f': # backspace pressed
            if self.state == 0: # user id
                self.id = self.id[:-1]
        else:
             if self.state == 0: # user id
                 if len(self.id) < self.maxLen:
                     self.id = self.id + data
                 else:
                     self.id = self.id
   
        if self.state == 0: # user id
            self.term.hide_cursor();
            self.term.format_put_on_cursor(self.id, self.maxLen+1, False, Colors.White, Colors.White, Align.Left)
            self.term.move_cursor_left(self.maxLen+1 - len(self.id))
   
        #mon = str(localtime().tm_mon)
        #reactor.callLater(1, self.drawBirthScr(str(i)), 0)


        #self.term.format_put(0, 0, passwd, True, Colors.White, Colors.Cyan, Align.Center)
        
        #self.term.form(False, Colors.White, Colors.Cyan, form, inputLen, Align.Center)
        #self.term.move_cursor_up(len(rows))
        #self.term.move_cursor_right(rows[0].find(':') + 1 - len(term.escape_sequence(False, Colors.White, Colors.Cyan)))