# -*- encoding: BIG5 -*-

## Ptt BBS python rewrite
##
## This is the view controller of MVC architecture for term
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
        self.term = term
        self.bbs = bb
        
    def changeState(self, to):
        self.state = to
        self.calls = 0
        self.term.clr_scr()
        self.update()

    def header(self, data=''):
        pass

    def content(self, data=''):
        pass
    
    def footer(self, data=''):
        pass
    

    def update(self, data=''):
        # turn off line buffer mode
        #self.term.setLineMode(False)
        self.header(data)
        self.footer(data)
        self.content(data)

    def anyKey(self, data, screen):
        self.term.format_put(term.height, 0, "按隨意鍵跳出", term.width,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        
        if len(data) > 0:
            if screen == 'prev':
                self.bbs.pop()
                return
            else:
                self.bbs.push(screen, self.term, True) # don't need to keep this screen
                return

    def isKey(self, input, key):
        return repr(input) == repr(key)
    
    def drawScr(self, strings, force=False):
        if self.calls == 0 or force:
            self.term.clr_scr()
            #codecs.open(dir, 'r', 'cp437')
            for i, line in enumerate(strings):
                self.term.put(i+1, 0, line)
        
    def drawScrFromFile(self, dir, force=False):
        if self.calls == 0 or force:
            self.term.clr_scr()
            #codecs.open(dir, 'r', 'cp437')
            for i, line in enumerate(open(dir)):
                self.term.put(i+1, 0, line)


class scrollableScreenlet(screenlet):
    def __init__(self, t, bb):
        super(scrollableScreenlet, self).__init__(t, bb)

        self.x = 0
        self.y = 0
        self.cursor = 0
        self.width = term.width # maximum allowed width
        self.height = term.height # maximum allowed height
        self.align = Align.Left
        self.offset = 0
        self.buff = []
    
    def update(self, data=''):
        # turn off line buffer mode
        #self.term.setLineMode(False)
        self.header(data)
        self.footer(data)
        self.content(data)
        self.scroll(data)
    
    def scroll(self, data=''):        
        # self.cursor can only go from 0 to self.height
        if self.isKey(data, arrow_up_key):
            if self.cursor == 0:
                if self.offset > 0:
                    self.offset = self.offset - 1
            else:
                self.cursor = self.cursor - 1
        elif self.isKey(data, arrow_down_key):
            if self.cursor == self.height-1:
                if self.offset + self.height < len(self.buff)-1:
                    self.offset = self.offset + 1
            else:
                if self.offset + self.cursor < len(self.buff)-1:
                    self.cursor = self.cursor + 1
        
        print self.cursor, self.offset
        
        ind = 0
        for i, line in enumerate(self.buff):
            if i >= self.offset and ind < self.height:
                #print i, self.offset, ind, self.height
                self.term.format_put(self.y + ind, self.x, line.strip(), self.width, align=self.align, highlight=True if self.cursor == ind else False)
                ind = ind + 1


class login(screenlet):
    def __init__(self, term, bbs):
        super(login, self).__init__(term, bbs)
        self.id = ''
        self.pw = '' 
        
        
    
    # the methodology behind this is always static first, always the lowest layer first, think of layers, paint the least
    # dynamic layer first
    def content(self, data=''):
        
        # draw background
        self.drawScrFromFile("../../res/Welcome_login")
    
        #mon = str(localtime().tm_mon)
        #reactor.callLater(1, fn, 0)
   
        self.term.put(23, 0, "觀光局邀您分享遊記、相片，福斯汽車、百萬獎勵讓您玩遍台灣!http://ppt.cc/w4vV")
        if self.state == 1:
                self.term.put(22, 0, "請輸入密碼： ")
        
        self.term.put(21, 0, "請輸入帳號，或以 guest 參觀，或以 new 註冊： ") # offset 45
        
        
        
        if self.state == 0:
            self.term.ready_for_input(13, 21, 45)
        elif self.state == 1:
            self.term.ready_for_input(20, 22, 13, False)
        
        if self.isKey(data, return_key): # return pressed
            if self.state == 0: # user id
                self.id = self.term.input
                if self.id == "new":
                    self.bbs.push(registration, self.term, True)
                    return
                if self.id == "guest":
                    self.bbs.user_lookup(self.id, self.pw) # just to associate guest with IP
                    self.bbs.push(welcome, self.term, True)
                    return
                self.term.finish_for_input()
                self.changeState(1)
                
            else: # password
                self.pw = self.term.input
                if self.bbs.user_lookup(self.id, self.pw) == 0: # 0 success
                    #self.term.print_input()
                    self.term.finish_for_input()
                    self.bbs.push(welcome, self.term, True)
                    return
                else:
                    self.term.finish_for_input()
                    self.changeState(0)
                    self.term.put(22, 0, "帳號或密碼有錯誤，請重新輸入。")
        elif self.isKey(data, backspace_key): # backspace pressed 
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
            # BIG5
            # ascii
            if data and '\xa1' <= data <= '\xf9' \
            or '\x1f' < data < '\x7f' :
                self.term.add_to_input(data)

        self.term.hide_cursor() # doesn't work QQ
        self.term.print_input()
        
        self.calls = self.calls + 1
        
class welcome(screenlet):
    def content(self, data=''):
        # draw background
        self.drawScrFromFile("../../res/whitemail")
        self.anyKey(data, menus2)
        
class registration(screenlet):
    def content(self, data=''):
        # draw background
        self.drawScrFromFile("../../res/register")
        self.anyKey(data, login)
        
class menus(screenlet):
    def __init__(self, term, bbs):
        super(menus, self).__init__(term, bbs)
        self.cursor = 0
        
    
    def header(self, data=''):
        if self.state == 0:
            title = "【 主功能表 】"
        site = "批踢踢py實業坊"
        self.term.format_put(0, 0, site, term.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.term.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
        
        
    def footer(self, data=''):
        time = "現在時間"
        constellation = "星座"
        online = "線上1人"
        id = "我是" + self.bbs.id
        self.term.format_put(term.height, 0, time, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(constellation, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(online, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(id, 10,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
    
    def content(self, data=''):
        print "in content"
        # draw background
        #self.drawScrFromFile("../res/topmenu")
        
        if self.isKey(data, arrow_up_key):
            if self.cursor > 0:
                self.cursor = self.cursor - 1
        elif self.isKey(data, arrow_down_key):
            if self.cursor < 9:
                self.cursor = self.cursor + 1
        if self.isKey(data, arrow_left_key):
            pass
        elif self.isKey(data, arrow_right_key) or self.isKey(data, return_key):
            if self.cursor == 2:
                self.bbs.push(discussionboard, self.term)
            elif self.cursor == 9:
                self.bbs.push(quit, self.term)
            else:
                self.bbs.push(notfinished, self.term)
            return
        """
        self.x = 0
        self.y = 1
        self.width = term.width
        self.height = term.height - 2
        for line in open('../../res/topmenu2'):
            self.buff.append(self.term.format(None, None, None, line.strip(), self.width, Align.Center))
        print self.buff
        """

        hi = 0
        for i, line in enumerate(open('../../res/topmenu2')):
            if line.strip() == '':
                continue
            self.term.format_put(i , 0, line.strip(), term.width, align=Align.Center, highlight=True if self.cursor == hi else False)
            hi = hi + 1

        """
        self.term.format_put(5 , 0, "(A)nnouncement 【 精華公佈欄 】", term.width, align=Align.Center, highlight=True if self.cursor == 0 else False)
        self.term.format_put(6 , 0, "(F)avorites    【 我的最愛區 】", term.width, align=Align.Center, highlight=True if self.cursor == 1 else False)
        self.term.format_put(7 , 0, "(B)oard        【 分組討論區 】", term.width, align=Align.Center, highlight=True if self.cursor == 2 else False)
        self.term.format_put(8 , 0, "(M)ailbox      【 私人信件區 】", term.width, align=Align.Center, highlight=True if self.cursor == 3 else False)
        self.term.format_put(9 , 0, "(T)alk         【 休閒聊天區 】", term.width, align=Align.Center, highlight=True if self.cursor == 4 else False)
        self.term.format_put(10, 0, "(S)settings    【 個人設定區 】", term.width, align=Align.Center, highlight=True if self.cursor == 5 else False)
        self.term.format_put(11, 0, "(X)yz          【 系統資訊區 】", term.width, align=Align.Center, highlight=True if self.cursor == 6 else False)
        self.term.format_put(12, 0, "(E)ntertainment【 娛樂與休閒 】", term.width, align=Align.Center, highlight=True if self.cursor == 7 else False)
        self.term.format_put(13, 0, "(L)ist         【 編特別名單 】", term.width, align=Align.Center, highlight=True if self.cursor == 8 else False)
        self.term.format_put(14, 0, "(Q)uit            離開，再見… ", term.width, align=Align.Center, highlight=True if self.cursor == 9 else False)
        """

class menus2(scrollableScreenlet):
    def __init__(self, t, bbs):
        super(menus2, self).__init__(t, bbs)
        self.x = 0
        self.y = 6
        self.width = term.width 
        self.height = term.height - self.y - 1 
        self.align = Align.Center
        
    
    def header(self, data=''):
        if self.state == 0:
            title = "【 主功能表 】"
        site = "批踢踢py實業坊"
        self.term.format_put(0, 0, site, term.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.term.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
        
        
    def footer(self, data=''):
        time = "現在時間"
        constellation = "星座"
        online = "線上1人"
        id = "我是" + self.bbs.id
        self.term.format_put(term.height, 0, time, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(constellation, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(online, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(id, 10,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
    
    def content(self, data=''):
        self.buff = []
        
        if self.isKey(data, arrow_left_key):
            pass
        elif self.isKey(data, arrow_right_key) or self.isKey(data, return_key):
            if self.cursor == 2:
                self.bbs.push(discussionboard2, self.term)
            elif self.cursor == 9:
                self.bbs.push(quit, self.term)
            else:
                self.bbs.push(notfinished, self.term)
            return
        
        
        
        for i, line in enumerate(open('../../res/topmenu2')):
            self.buff.append(line.strip())


class quit(screenlet):
    def content(self, data=''):
        # draw background
        self.drawScrFromFile("../../res/goodbye")
        self.anyKey(data, 'prev')

class notfinished(screenlet):
    def content(self, data=''):
        # draw background
        self.drawScrFromFile("../../res/notfinished")
        self.anyKey(data, 'prev')
        
class discussionboard(screenlet):
    def __init__(self, term, bbs):
        super(discussionboard, self).__init__(term, bbs)
        self.cursor = 0 
        
        
    
    def header(self, data=''):
        if self.state == 0:
            title = "【 功能看板 】"
        site = "批踢踢py實業坊"
        self.term.format_put(0, 0, site, term.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.term.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
        
        
    def footer(self, data=''):
        time = "現在時間"
        constellation = "星座"
        online = "線上1人"
        id = "我是" + self.bbs.id
        self.term.format_put(term.height, 0, time, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(constellation, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(online, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(id, 10,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        
        
    def content(self, data=''):
        # draw background
        if self.isKey(data, arrow_up_key):
            if self.cursor > 0:
                self.cursor = self.cursor - 1
        elif self.isKey(data, arrow_down_key):
            if self.cursor < 14:
                self.cursor = self.cursor + 1
        elif self.isKey(data, arrow_left_key):
            self.bbs.pop()
            return
        elif self.isKey(data, arrow_right_key) or self.isKey(data, return_key):
            self.bbs.push(notfinished, self.term)
            return
        
        hi = 0
        for i, line in enumerate(open('../../res/boardlist')):
            if line.strip() == '':
                continue
            self.term.format_put(i , 0, line.strip(), term.width, align=Align.Center, highlight=True if self.cursor == hi else False)
            hi = hi + 1
class discussionboard2(scrollableScreenlet):
    def __init__(self, t, bbs):
        super(discussionboard2, self).__init__(t, bbs)
        
        self.x = 0
        self.y = 5
        self.width = term.width 
        self.height = term.height - self.y - 1 
        self.align = Align.Center
        
        
    
    def header(self, data=''):
        if self.state == 0:
            title = "【 功能看板 】"
        site = "批踢踢py實業坊"
        self.term.format_put(0, 0, site, term.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.term.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
        
        
    def footer(self, data=''):
        time = "現在時間"
        constellation = "星座"
        online = "線上1人"
        id = "我是" + self.bbs.id
        self.term.format_put(term.height, 0, time, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(constellation, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(online, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(id, 10,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        
        
    def content(self, data=''):
        self.buff = []
        
        if self.isKey(data, arrow_left_key):
            self.bbs.pop()    
            return
        elif self.isKey(data, arrow_right_key) or self.isKey(data, return_key):
            if self.cursor == 0:
                self.bbs.push(boardlist, self.term)
            else:
                self.bbs.push(notfinished, self.term)
            return
        
        self.buff = []
        for i, line in enumerate(open('../../res/boardlist')):
            self.buff.append(line.strip())
            
class boardlist(scrollableScreenlet):
    def __init__(self, t, bbs):
        super(boardlist, self).__init__(t, bbs)
        
        self.x = 0
        self.y = 3
        self.width = term.width 
        self.height = term.height - self.y - 1 
        self.align = Align.Center
        
    def header(self, data=''):
        if self.state == 0:
            title = "【 看板列表 】"
        site = "批踢踢py實業坊"
        self.term.format_put(0, 0, site, term.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.term.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
        
        
    def footer(self, data=''):
        time = "現在時間"
        constellation = "星座"
        online = "線上1人"
        id = "我是" + self.bbs.id
        self.term.format_put(term.height, 0, time, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(constellation, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(online, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(id, 10,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
    
    def content(self, data=''):
        self.buff = []
        
        
        

class threadlist(scrollableScreenlet):
    def header(self, data=''):
        if self.state == 0:
            title = "【 看板列表 】"
        site = "批踢踢py實業坊"
        self.term.format_put(0, 0, site, term.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.term.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
        
        
    def footer(self, data=''):
        time = "現在時間"
        constellation = "星座"
        online = "線上1人"
        id = "我是" + self.bbs.id
        self.term.format_put(term.height, 0, time, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(constellation, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(online, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(id, 10,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
    
    def content(self, data=''):
        self.y = 2;
        self.height = term.height - 3
        
class texteditor(scrollableScreenlet):
    def header(self, data=''):
        if self.state == 0:
            title = "【 看板列表 】"
        site = "批踢踢py實業坊"
        self.term.format_put(0, 0, site, term.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.term.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
        
        
    def footer(self, data=''):
        time = "現在時間"
        constellation = "星座"
        online = "線上1人"
        id = "我是" + self.bbs.id
        self.term.format_put(term.height, 0, time, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(constellation, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(online, 20,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.term.format_put_on_cursor(id, 10,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
    
    def content(self, data=''):
        self.height = term.height - 1        