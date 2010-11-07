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
    def __init__(self, term, bb):
        self.state = 0
        self.calls = 0
        self.billboard = []
        self.buff = term
        self.bbs = bb
        
    def changeState(self, to):
        self.state = to
        self.calls = 0
        self.buff.clr_scr()
        self.update()

    def header(self, data=''):
        pass

    def content(self, data=''):
        pass
    
    def footer(self, data=''):
        pass
    

    def update(self, data=''):
        # turn off line buffer mode
        #self.buff.setLineMode(False)
        
        self.header(data)
        
        self.content(data)
        
        self.footer(data)

    def anyKey(self, data, screenlet):
        self.buff.format_put(term.height, 0, "按隨意鍵跳出", term.width,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        
        if len(data) > 0:
            self.bbs.pop(False)
            self.bbs.push(screenlet, self.buff)
            return

    def isKey(self, input, key):
        return len(input) == len(key) and input == key
    
    def drawScr(self, strings, force=False):
        if self.calls == 0 or force:
            self.buff.clr_scr()
            #codecs.open(dir, 'r', 'cp437')
            for i, line in enumerate(strings):
                self.buff.put(i+1, 0, line)
        
    def drawScrFromFile(self, dir, force=False):
        if self.calls == 0 or force:
            self.buff.clr_scr()
            #codecs.open(dir, 'r', 'cp437')
            for i, line in enumerate(open(dir)):
                self.buff.put(i+1, 0, line)


class scrollableScreenlet(screenlet):
    pass


class login(screenlet):
    def __init__(self, term, bbs):    
        self.id = ''
        self.pw = '' 
        
        super(login, self).__init__(term, bbs)
    
    # the methodology behind this is always static first, always the lowest layer first, think of layers, paint the least
    # dynamic layer first
    def content(self, data=''):
        
        # draw background
        self.drawScrFromFile("../../res/Welcome_login")
    
        #mon = str(localtime().tm_mon)
        #reactor.callLater(1, fn, 0)
   
        self.buff.put(23, 0, "觀光局邀您分享遊記、相片，福斯汽車、百萬獎勵讓您玩遍台灣!http://ppt.cc/w4vV")
        if self.state == 1:
                self.buff.put(22, 0, "請輸入密碼： ")
        
        self.buff.put(21, 0, "請輸入帳號，或以 guest 參觀，或以 new 註冊： ") # offset 45
        
        
        
        if self.state == 0:
            self.buff.ready_for_input(13, 21, 45)
        elif self.state == 1:
            self.buff.ready_for_input(20, 22, 13, False)
        
        if self.isKey(data, return_key): # return pressed
            if self.state == 0: # user id
                self.id = self.buff.input
                if self.id == "new":
                    self.bbs.push(registration, self.buff)
                    return
                if self.id == "guest":
                    self.bbs.user_lookup(self.id, self.pw) # just to associate guest with IP
                    self.bbs.push(welcome, self.buff)
                    return
                self.buff.finish_for_input()
                self.changeState(1)
                
            else: # password
                self.pw = self.buff.input
                if self.bbs.user_lookup(self.id, self.pw) == 0: # 0 success
                    #self.buff.print_input()
                    self.buff.finish_for_input()
                    self.bbs.push(welcome, self.buff)
                    return
                else:
                    self.buff.finish_for_input()
                    self.changeState(0)
                    self.buff.put(22, 0, "帳號或密碼有錯誤，請重新輸入。")
        elif self.isKey(data, backspace_key): # backspace pressed 
            self.buff.backspace_input()
        elif self.isKey(data, arrow_up_key):
            pass
        elif self.isKey(data, arrow_down_key):
            pass
        elif self.isKey(data, arrow_right_key):
            self.buff.move_right_input()
        elif self.isKey(data, arrow_left_key):
            self.buff.move_left_input()
        else:
            self.buff.add_to_input(data)

        self.buff.hide_cursor() # doesn't work QQ
        self.buff.print_input()
        
        self.calls = self.calls + 1
        
class welcome(screenlet):
    def content(self, data=''):
        # draw background
        self.drawScrFromFile("../../res/whitemail")
        self.anyKey(data, menus)
        
class registration(screenlet):
    def content(self, data=''):
        # draw background
        self.drawScrFromFile("../../res/register")
        self.anyKey(data, login)
        
class menus(screenlet):
    def __init__(self, term, bbs):    
        self.cursor = 0 
        
        super(menus, self).__init__(term, bbs)
    
    def header(self, data=''):
        if self.state == 0:
            title = "【 主功能表 】"
        site = "批踢踢py實業坊"
        self.buff.format_put(0, 0, site, term.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.buff.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
        
        
    def footer(self, data=''):
        time = "現在時間"
        constellation = "星座"
        online = "線上1人"
        id = "我是" + self.bbs.id
        self.buff.format_put(term.height, 0, time, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.buff.format_put_on_cursor(constellation, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.buff.format_put_on_cursor(online, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.buff.format_put_on_cursor(id, 10,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
    
    def content(self, data=''):
        # draw background
        #self.drawScrFromFile("../res/topmenu")
        if self.isKey(data, arrow_up_key):
            if self.cursor > 0:
                self.cursor = self.cursor - 1
        elif self.isKey(data, arrow_down_key):
            if self.cursor < 9:
                self.cursor = self.cursor + 1
        elif self.isKey(data, arrow_left_key):
            pass
        elif self.isKey(data, arrow_right_key) or self.isKey(data, return_key):
            self.bbs.push(discussionboard, self.buff)
            return
        
        self.buff.format_put(5 , 0, "(A)nnouncement 【 精華公佈欄 】", term.width, align=Align.Center, highlight=True if self.cursor == 0 else False)
        self.buff.format_put(6 , 0, "(F)avorites    【 我的最愛區 】", term.width, align=Align.Center, highlight=True if self.cursor == 1 else False)
        self.buff.format_put(7 , 0, "(B)oard        【 分組討論區 】", term.width, align=Align.Center, highlight=True if self.cursor == 2 else False)
        self.buff.format_put(8 , 0, "(M)ailbox      【 私人信件區 】", term.width, align=Align.Center, highlight=True if self.cursor == 3 else False)
        self.buff.format_put(9 , 0, "(T)alk         【 休閒聊天區 】", term.width, align=Align.Center, highlight=True if self.cursor == 4 else False)
        self.buff.format_put(10, 0, "(S)settings    【 個人設定區 】", term.width, align=Align.Center, highlight=True if self.cursor == 5 else False)
        self.buff.format_put(11, 0, "(X)yz          【 系統資訊區 】", term.width, align=Align.Center, highlight=True if self.cursor == 6 else False)
        self.buff.format_put(12, 0, "(E)ntertainment【 娛樂與休閒 】", term.width, align=Align.Center, highlight=True if self.cursor == 7 else False)
        self.buff.format_put(13, 0, "(L)ist         【 編特別名單 】", term.width, align=Align.Center, highlight=True if self.cursor == 8 else False)
        self.buff.format_put(14, 0, "(Q)uit            離開，再見… ", term.width, align=Align.Center, highlight=True if self.cursor == 9 else False)
        
class discussionboard(screenlet):
    def content(self, data=''):
        # draw background
        self.drawScrFromFile("../../res/boardlist.help")
        self.anyKey(data, login)