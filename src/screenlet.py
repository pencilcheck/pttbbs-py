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
from chardet.universaldetector import UniversalDetector
from twisted.internet import reactor, defer
from time import localtime
import codecs


from term import Colors
from term import Align

import bbs # controller

return_key = '\r'
backspace_key = '\x7f'
arrow_up_key = '\x1bOA'
arrow_down_key = '\x1bOB'
arrow_right_key = '\x1bOC'
arrow_left_key = '\x1bOD'
tab_key = '\t'
shift_key = '' # it doesn't send

class screenlet(object):
    def __init__(self, t):
        self.state = 0
        self.billboard = []
        self.header = []
        self.content = []
        self.footer = []
        self.term = t
        
    def changeState(self, to):
        self.state = to
        self.calls = 0
        self.term.clr_scr()

    def update(self, data=''):
        # turn off line buffer mode
        self.term.setLineMode(False)

    def isKey(self, input, key):
        return len(input) == len(key) and input == key
        
    def drawScr(self, dir):
        self.term.clr_scr()
        detect = UniversalDetector()
        """
        for line in open(dir).readlines():
            detect.feed(line)
            if detect.done:
                break
        detect.close()
        print detect.result
        """
        #codecs.open(dir, 'r', 'cp437')
        for i, line in enumerate(open(dir)):
            self.term.put(i+1, 0, line)


class login(screenlet):
    def __init__(self, t):    
        self.id = ''
        self.pw = '' 
        
        self.state = 0
        self.calls = 0
        
        super(login, self).__init__(t)
    
    # the methodology behind this is always static first, always the lowest layer first, think of layers, paint the least
    # dynamic layer first
    def update(self, data=''):
        
        # draw background
        if self.calls == 0:
            self.drawScr("../res/Welcome_login")
    
        #mon = str(localtime().tm_mon)
        #reactor.callLater(1, fn, 0)
   
        self.term.put(22, 0, "觀光局邀您分享遊記、相片，福斯汽車、百萬獎勵讓您玩遍台灣!http://ppt.cc/w4vV")
        if self.state == 1:
                self.term.put(22, 0, "請輸入密碼： ")
        
        self.term.put(21, 0, "請輸入代號，或以 guest 參觀，或以 new 註冊： ") # offset 45
        
        
        
        if self.state == 0:
            self.term.ready_for_input(13, 21, 45)
        elif self.state == 1:
            self.term.ready_for_input(20, 22, 13, False)
        
        if self.isKey(data, return_key): # return pressed
            if self.state == 0: # user id
                self.id = self.term.input
                if bbs.check_userid(self.id) == 0: # 0 success
                    self.changeState(1) # now check password
                    self.term.finish_for_input()
                    self.update()
                else:
                    pass # have to show warning somehow
            else: # password
                self.pw = self.term.input
                if bbs.check_pw(self.pw) == 0:
                    self.term.print_input()
                    self.term.finish_for_input()
                    bbs.push(welcome, self.term) 
                    return
                else:
                    self.changeState(0)
                    self.term.finish_for_input()
                    self.update()
        elif self.isKey(data, backspace_key): # backspace pressed 
            print repr(self.id)
            self.term.backspace_input()
        elif self.isKey(data, arrow_up_key):
            pass
        elif self.isKey(data, arrow_down_key):
            pass
        elif self.isKey(data, arrow_right_key):
            self.term.move_right_input()
        elif self.isKey(data, arrow_left_key):
            self.term.move_left_input()
        else:
            self.term.add_to_input(data)

        self.term.hide_cursor() # doesn't work QQ
        self.term.print_input()
        
        self.calls = self.calls + 1
        
class welcome(screenlet):
    def update(self, data=''):
        # clear the screen
        self.drawScr("../res/whitemail")