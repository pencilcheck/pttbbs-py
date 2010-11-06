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

import term
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
    def __init__(self):
        self.state = 0
        self.calls = 0
        self.billboard = []
        self.header = []
        self.content = []
        self.footer = []
        
    def changeState(self, to):
        self.state = to
        self.calls = 0
        term.instance.clr_scr()
        self.update()

    def update(self, data=''):
        # turn off line buffer mode
        term.instance.setLineMode(False)

    def isKey(self, input, key):
        return len(input) == len(key) and input == key
        
    def drawScr(self, dir, force=False):
        if self.calls == 0 or force:
            term.instance.clr_scr()
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
                term.instance.put(i+1, 0, line)


class login(screenlet):
    def __init__(self):    
        self.id = ''
        self.pw = '' 
        
        self.state = 0
        self.calls = 0
        
        super(login, self).__init__()
    
    # the methodology behind this is always static first, always the lowest layer first, think of layers, paint the least
    # dynamic layer first
    def update(self, data=''):
        
        # draw background
        self.drawScr("../res/Welcome_login")
    
        #mon = str(localtime().tm_mon)
        #reactor.callLater(1, fn, 0)
   
        term.instance.put(23, 0, "�[�����ܱz���ɹC�O�B�ۤ��A�ִ��T���B�ʸU���y���z���M�x�W!http://ppt.cc/w4vV")
        if self.state == 1:
                term.instance.put(22, 0, "�п�J�K�X�G ")
        
        term.instance.put(21, 0, "�п�J�b���A�ΥH guest ���[�A�ΥH new ���U�G ") # offset 45
        
        
        
        if self.state == 0:
            term.instance.ready_for_input(13, 21, 45)
        elif self.state == 1:
            term.instance.ready_for_input(20, 22, 13, False)
        
        if self.isKey(data, return_key): # return pressed
            if self.state == 0: # user id
                self.id = term.instance.input
                if self.id == "new":
                    bbs.push(registration)
                    return
                term.instance.finish_for_input()
                self.changeState(1)
                
            else: # password
                self.pw = term.instance.input
                if bbs.user_lookup(self.id, self.pw) == 0: # 0 success
                    term.instance.print_input()
                    term.instance.finish_for_input()
                    bbs.push(welcome)
                    return
                else:
                    term.instance.finish_for_input()
                    self.changeState(0)
                    term.instance.put(22, 0, "�b���αK�X�����~�A�Э��s��J�C")
        elif self.isKey(data, backspace_key): # backspace pressed 
            print repr(self.id)
            term.instance.backspace_input()
        elif self.isKey(data, arrow_up_key):
            pass
        elif self.isKey(data, arrow_down_key):
            pass
        elif self.isKey(data, arrow_right_key):
            term.instance.move_right_input()
        elif self.isKey(data, arrow_left_key):
            term.instance.move_left_input()
        else:
            term.instance.add_to_input(data)

        term.instance.hide_cursor() # doesn't work QQ
        term.instance.print_input()
        
        self.calls = self.calls + 1
        
class welcome(screenlet):
    def update(self, data=''):
        # draw background
        self.drawScr("../res/whitemail")
        
class registration(screenlet):
    def update(self, data=''):
        # draw background
        self.drawScr("../res/register")