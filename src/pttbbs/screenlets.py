# -*- encoding: UTF-8 -*-

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
import gevent

import screen
from screen import ForegroundColors, BackgroundColors
from screen import Align

return_key = '\r'
backspace_key = '\x7f'
arrow_up_key = '\x1bOA'
arrow_down_key = '\x1bOB'
arrow_right_key = '\x1bOC'
arrow_left_key = '\x1bOD'
tab_key = '\t'
shift_key = '' # it doesn't send

def mylen(input):
    count = 0
    for c in input:
        if c > '\x81':
            count = count + 1.0/2.0
        else:
            count = count + 1
    count = int(count)
    return count

def isKey(input, key):
    return repr(input) == repr(key)

class screenlet(object):
    def __init__(self, handler, line, coln, width, height):
        self.line = line
        self.coln = coln
        self.width = width
        self.height = height
        self.handler = handler
        self.buffer = ""
        self.focusable = False
        self.isFocused = False # default focus is chosen arbitrarily
        self.focusLine = self.line
        self.focusColn = self.coln
        self.visible = True
        self.subcomponents = [] # all components in the same level
        self.initialize()

    def setBuffer(self, buffer):
        self.buffer = buffer

    def initialize(self):
        pass
    
    def handleCmds(self, data=''):
        return 0

    # when overriding this remember to consume the data if anything match
    # return 1 if anything need clear screen
    def handleFocus(self, data):
        if len(self.subcomponents) == 0:
            if self.focusable:
                if self.isFocused:
                    self.isFocused = False
                    return data
                else:
                    self.isFocused = True
                    return ''
            else:
                return data
        
        for i, component in enumerate(self.subcomponents):
            data = component.handleFocus(data)
            if not data:
                break

        return data

    def getFocusCoords(self):

        if len(self.subcomponents) == 0:
            if self.focusable:
                if self.isFocused:
                    return self.focusLine, self.focusColn
            return -1, -1

        for i, component in enumerate(self.subcomponents):
            tr, tc = component.getFocusCoords()
            if tr == tc == -1:
                continue
            else:
                break

        return tr, tc


    # update is only overrided in the most base screenlet that place the cursor
    def update(self, data=''):
        print "screenlet update"
        ret = 0
        
        # tab is now a special command key to switch between components
        if isKey(data, tab_key):
            if self.handleFocus(data):
                if self.focusable:
                    self.isFocused = True
            else:
                if self.focusable:
                    self.isFocused = False
        else:
            ret = ret | self.handleCmds(data)
        
        for i, component in enumerate(self.subcomponents):
            print component
            if component.focusable and component.isFocused:
                ret = ret | component.update(data)
            else:
                ret = ret | component.update()
        
        return ret
    
    # draw in the order of a queue, so FIFD (first in first draw)
    def draw(self):
        print "screenlet draw"
        # TODO: need to figure out a way to draw and move cursor to the focused component
        
        if not self.visible:
            return ''
        
        row, coln = self.getFocusCoords()

        for component in self.subcomponents:
            print component
            #self.buffer = screen.move_cursor(self.line, self.coln) + self.buffer + component.draw()
            self.buffer = self.buffer + component.draw()
        
        print "screenlet draw end", row, coln
        if row >= 0 and coln >= 0:
            return self.buffer + screen.move_cursor(row, coln)
        else:
            return self.buffer

class scrollableScreenlet(screenlet):
    def __init__(self, handler, line, coln, width, height):
        super(scrollableScreenlet, self).__init__(handler, line, coln, width, height)
        print "scrollable init"
        self.buffs = []
        self.cursor = 0
        self.offset = 0
    
    def handleCmds(self, data=''):
        # self.cursor can only go from 0 to self.height
        if isKey(data, arrow_up_key):
            if self.cursor == 0:
                if self.offset > 0:
                    self.offset = self.offset - 1
            else:
                self.cursor = self.cursor - 1
        elif isKey(data, arrow_down_key):
            if self.cursor == self.height-1:
                if self.offset + self.height < len(self.buffs)-1:
                    self.offset = self.offset + 1
            else:
                if self.offset + self.cursor < len(self.buffs)-1:
                    self.cursor = self.cursor + 1
        
        #print self.cursor, self.offset
        
        ind = 0
        for i, line in enumerate(self.buffs):
            if i >= self.offset and ind < self.height:
                print i, self.offset, ind, self.height
                
                if self.cursor == ind:
                    self.buffer = self.buffer + screen.format_puts(self.line + ind, self.coln, line.strip(), self.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.Yellow)
                else:
                    self.buffer = self.buffer + screen.format_puts(self.line + ind, self.coln, line.strip(), self.width, Align.Center)
                ind = ind + 1
        
        return self.handleCmds2(data)
        
    def handleCmds2(self, data=''):
        return 0



class art(screenlet):
    def __init__(self, handler, line, coln, width, height, file):
        super(art, self).__init__(handler, line, coln, width, height)
        print "art init"
        self.focusable = False
        self.buffer = screen.move_cursor(self.line, self.coln)
        for i, line in enumerate(open(file)):
            self.buffer = self.buffer + line + screen.move_cursor_down(1) + screen.move_cursor_left(len(line))


# arguments for label:
#  msg
#  msg, length, align
# or arguments above with keyword arguments: fg, bg
class label(screenlet):
    def __init__(self, handler, line, coln, width, height, *args, **kwargs):
        super(label, self).__init__(handler, line, coln, width, height)
        self.focusable = False
        print "label init", args, kwargs
        if len(args) == 1:
            if len(kwargs) == 2:
                self.buffer = screen.puts(self.line, self.coln, args[0], fg=kwargs['fg'], bg=kwargs['bg'])
            else:
                self.buffer = screen.puts(self.line, self.coln, args[0])
        
        if len(args) == 3:
            if len(kwargs) == 2:
                self.buffer = screen.format_puts(self.line, self.coln, args[0], args[1], args[2], fg=kwargs['fg'], bg=kwargs['bg'])
            else:
                self.buffer = screen.format_puts(self.line, self.coln, args[0], args[1], args[2])

        print self.buffer

# arguments:
# length, concealed
class input(screenlet):
    def __init__(self, handler, line, coln, width, height, length, isconcealed):
        super(input, self).__init__(handler, line, coln, width, height)
        self.focusable = True
        print "input init"
        
        self.buffer = screen.format_puts(self.line, self.coln, 'dsafsd', length, Align.Left, fg=ForegroundColors.Black, bg=BackgroundColors.White, concealed=isconcealed)

        print self.buffer
        
    def handleCmds(self, data=''):
        print data
        """
        if isKey(data, backspace_key): # backspace pressed 
            self.handler.buffer.backspace_input()
        elif isKey(data, arrow_up_key):
            pass
        elif isKey(data, arrow_down_key):
            pass
        elif isKey(data, arrow_right_key):
            self.handler.buffer.move_right_input()
        elif isKey(data, arrow_left_key):
            self.handler.buffer.move_left_input()
        else:
            # BIG5
            # ascii
            if data and '\xa1' <= data <= '\xf9' \
            or '\x1f' < data < '\x7f' :
                self.handler.buffer.add_to_input(data)
        """
        return 0


class header(screenlet):
    def __init__(self, handler, line, coln, width, height, location, title):
        super(header, self).__init__(handler, line, coln, width, height)
        self.focusable = False
        print "header init"
        self.location = location
        self.title = title
        
        
    def initialize(self):
        print "header initialize"
        # just for testing
        self.location = "【 主功能表 】"
        self.title = "批踢踢py實業坊"
        # end
        
        #self.subcomponents.append(label(self.handler, 0, 0, self.title, self.handler.width, Align.Center, fg=ForegroundColors.Black, bg=BackgroundColors.White))
        self.subcomponents.append(label(self.handler, self.line, self.coln, self.width, self.height, self.title, self.handler.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.LightBlue))
        self.subcomponents.append(label(self.handler, self.line, self.coln, self.width, self.height, self.location, fg=ForegroundColors.Yellow, bg=BackgroundColors.LightBlue))

class footer(screenlet):
    def __init__(self, handler, line, coln, width, height):
        super(footer, self).__init__(handler, line, coln, width, height)
        self.focusable = False
        self.time = ''
        self.number = ''
        
    def initialize(self):
        pass
        '''
        time = self.handler.getTime()
        constellation = "星座"
        online = "線上" + str(self.handler.getOnlineCount()) + "人"
        id = "我是" + self.handler.id
        self.handler.buffer.format_put(screen.height, 0, time, len(time),
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.handler.buffer.format_put_on_cursor(constellation, len(constellation),
                                 True, Colors.White, Colors.Magenta, Align.Center)
        self.handler.buffer.format_put_on_cursor(online, len(online) + 10,
                                 True, Colors.Cyan, Colors.Blue)
        self.handler.buffer.format_put_on_cursor(id, len(id) + 20,
                                 True, Colors.Cyan, Colors.Blue)
        '''

class login(screenlet):
    def __init__(self, handler, line, coln, width, height):
        super(login, self).__init__(handler, line, coln, width, height)
        print "login init"
        self.id = ''
        self.pw = ''
        
    
    def initialize(self):
        print "login initializing"
        title = 'Welcome to BBS'
        enterid = '請輸入帳號'
        enterpw = '請輸入密碼'
        
        #artwork = art(self.handler, 0, 0, self.width, self.height, '../../res/Welcome_birth')
        strip = label(self.handler, self.handler.height / 2, 0, self.width, self.height, title, self.handler.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.White)
        idLabel = label(self.handler, self.handler.height / 2 + 5, 0, len(enterid), 1, enterid) 
        self.idInput = input(self.handler, self.handler.height / 2 + 5, len(enterid), self.width, self.height, 10, True)
        self.idInput.isFocused = True
        pwLabel = label(self.handler, self.handler.height / 2 + 5, 0, len(enterpw), 1, enterpw)
        pwLabel.visible = False
        self.pwInput = input(self.handler, self.handler.height / 2 + 5, len(enterpw), self.width, self.height, 10, True)
        self.pwInput.visible = False
        #self.header = header(self.handler, 0, 0, self.width, self.height, 'haha', 'haha')
        #self.subcomponents.append(artwork)
        self.subcomponents.append(idLabel)
        self.subcomponents.append(self.idInput)
        self.subcomponents.append(pwLabel)
        self.subcomponents.append(self.pwInput)
        self.subcomponents.append(strip)
        
    
    # return 1 if clear screen is needed
    def handleCmds(self, data=''):
        if isKey(data, return_key):
            self.id = self.idInput.buffer
            """
            if self.id == "new":
                    self.handler.push(registration, selfdestruct=True)
                    return
                if self.id == "guest":
                    self.handler.user_lookup(self.id, self.pw) # just to associate guest with IP
                    self.handler.push(welcome, selfdestruct=True)
                    return
                self.handler.buffer.finish_for_input()
                self.changeState(1)
            """
            # check id if len(id) > 0
            # change visibility and then refresh
            self.pw = self.pwInput.buffer
            return 1
        return 0
    
    # the methodology behind this is always static first, always the lowest layer first, think of layers, paint the least
    # dynamic layer first
    def content(self, data=''):
        
        # draw background
        self.drawScrFromFile("../../res/Welcome_login")
    
        #mon = str(localtime().tm_mon)
        #reactor.callLater(1, fn, 0)
   
        self.handler.buffer.put(23, 0, "觀光局邀您分享遊記、相片，福斯汽車、百萬獎勵讓您玩遍台灣!http://ppt.cc/w4vV")
        if self.state == 1:
                self.handler.buffer.put(22, 0, "請輸入密碼： ")
        
        self.handler.buffer.put(21, 0, "請輸入帳號，或以 guest 參觀，或以 new 註冊： ") # offset 45
        
        
        
        if self.state == 0:
            self.handler.buffer.ready_for_input(13, 21, 45)
        elif self.state == 1:
            self.handler.buffer.ready_for_input(20, 22, 13, False)
        
        if self.isKey(data, return_key): # return pressed
            if self.state == 0: # user id
                self.id = self.handler.buffer.input
                if self.id == "new":
                    self.handler.push(registration, selfdestruct=True)
                    return
                if self.id == "guest":
                    self.handler.user_lookup(self.id, self.pw) # just to associate guest with IP
                    self.handler.push(welcome, selfdestruct=True)
                    return
                self.handler.buffer.finish_for_input()
                self.changeState(1)
                
            else: # password
                self.pw = self.handler.buffer.input
                if self.handler.user_lookup(self.id, self.pw) == 0: # 0 success
                    #self.handler.buffer.print_input()
                    self.handler.buffer.finish_for_input()
                    self.handler.push(welcome, selfdestruct=True)
                    return
                else:
                    self.handler.buffer.finish_for_input()
                    self.changeState(0)
                    self.handler.buffer.put(22, 0, "帳號或密碼有錯誤，請重新輸入。")
        elif self.isKey(data, backspace_key): # backspace pressed 
            self.handler.buffer.backspace_input()
        elif self.isKey(data, arrow_up_key):
            pass
        elif self.isKey(data, arrow_down_key):
            pass
        elif self.isKey(data, arrow_right_key):
            self.handler.buffer.move_right_input()
        elif self.isKey(data, arrow_left_key):
            self.handler.buffer.move_left_input()
        else:
            # BIG5
            # ascii
            if data and '\xa1' <= data <= '\xf9' \
            or '\x1f' < data < '\x7f' :
                self.handler.buffer.add_to_input(data)

        self.handler.buffer.hide_cursor() # doesn't work QQ
        self.handler.buffer.print_input()
        
        self.calls = self.calls + 1


class encoding(scrollableScreenlet):
    def __init__(self, handler, line, coln, width, height):
        super(encoding, self).__init__(handler, line, coln, width, height)
        self.focusable = True
        print "encoding init"
        
        self.buffs.append("UTF8")
        self.buffs.append("BIG5")    
        
    def initialize(self):
        self.subcomponents.append(label(self.handler, self.handler.height, 0, self.width, self.height, "如果你可以看到這段句子，請按確認鍵繼續。"))
    
    # return 1 if clear screen is needed
    def handleCmds2(self, data=''):
        if self.cursor == 0:
            self.handler.encoding = 'UTF8'
        elif self.cursor == 1:
            self.handler.encoding = 'BIG5'
        
        if isKey(data, return_key):
            self.handler.stack.pop()
        return 1
        
class resolution(scrollableScreenlet):
    def __init__(self, handler, line, coln, width, height):
        super(resolution, self).__init__(handler, line, coln, width, height)
        self.focusable = True
        print "resolution init"
        
        self.buffs.append("80x24")
        self.buffs.append("160x24")
        self.buffs.append("80x48")    
        
    
    # return 1 if clear screen is needed
    def handleCmds2(self, data=''):
        if isKey(data, return_key):
            return 1
        return 0
    
'''
class welcome(screenlet):
    def initialize(self):
        pass
        # draw background
        #self.drawScrFromFile("../../res/whitemail")
        #self.anyKey(data, menus2)
        
class registration(screenlet):
    def initialize(self, data=''):
        pass
        # draw background
        #self.drawScrFromFile("../../res/register")
        #self.anyKey(data, login)
        
class menus2(scrollableScreenlet):
    def __init__(self, handler):
        super(menus2, self).__init__(handler)
        self.line = 0
        self.coln = 6
        self.width = screen.width 
        self.height = screen.height - self.coln - 1 
        self.align = Align.Center
        
    
    def header(self, data=''):
        if self.state == 0:
            title = "【 主功能表 】"
        site = "批踢踢py實業坊"
        self.handler.buffer.format_put(0, 0, site, screen.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.handler.buffer.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)

    
    def content(self, data=''):
        if self.isKey(data, arrow_left_key):
            self.buff = []
            pass
        elif self.isKey(data, arrow_right_key) or self.isKey(data, return_key):
            self.buff = []
            result = self.offset + self.cursor
            self.handler.push(None, pathappend=str(result))
            """
            if self.cursor == 2:
                self.handler.push(discussionboard2, self.handler.buffer)
            elif self.cursor == 9:
                self.handler.push(quit, self.handler.buffer)
            else:
                self.handler.push(notfinished, self.handler.buffer)
            """
            return
        
        #print globals()
        
        if not self.buff:
            self.buff = self.handler.loadBoardList()
        """
        for i, line in enumerate(open('../../res/topmenu2')):
            self.buff.append(line.strip())
        """


class quit(screenlet):
    def initialize(self, data=''):
        pass
        # draw background
        #self.drawScrFromFile("../../res/goodbye")
        #self.anyKey(data, 'prev')

class notfinished(screenlet):
    def initialize(self, data=''):
        pass
        # draw background
        #self.drawScrFromFile("../../res/notfinished")
        #self.anyKey(data, 'prev')

# discussionboard number 2
class discussionboard2(scrollableScreenlet):
    def __init__(self, handler):
        super(discussionboard2, self).__init__(handler)
        self.line = 0
        self.coln = 5
        self.width = screen.width
        self.height = screen.height - self.coln - 1 
        self.align = Align.Center
        
        
    
    def header(self, data=''):
        if self.state == 0:
            title = "【 功能看板 】"
        site = "批踢踢py實業坊"
        self.handler.buffer.format_put(0, 0, site, screen.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.handler.buffer.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)

        
    def commandinterface(self, data=''):
        #if self.isKey(data, )
        
        msg = "test skjdkf sdlkfjlsdkj  sdfk lkj"
        self.handler.buffer.format_put(screen.height - 1, 0, msg, screen.width)
        
    def content(self, data=''):
        if self.isKey(data, arrow_left_key):
            self.buff = []
            self.handler.pop()    
            return
        elif self.isKey(data, arrow_right_key) or self.isKey(data, return_key):
            self.buff = []
            result = self.offset + self.cursor
            self.handler.push(None, pathappend=str(result))
            return
        
        self.commandinterface(data)
        
        self.buff = self.handler.loadBoardList()
        
        # not used
        for i, line in enumerate(open('../../res/boardlist')):
            self.buff.append(line.strip())
        # end
            
class boardlist(scrollableScreenlet):
    def __init__(self, handler):
        super(boardlist, self).__init__(handler)
        
        self.line = 0
        self.coln = 3
        self.width = screen.width 
        self.height = screen.height - self.coln - 1 
        self.align = Align.Center
        
    def header(self, data=''):
        if self.state == 0:
            title = "【 看板列表 】"
        site = "批踢踢py實業坊"
        self.handler.buffer.format_put(0, 0, site, screen.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.handler.buffer.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
    
    def content(self, data=''):
        self.buff = []
        
        
        

class threadlist(scrollableScreenlet):
    def header(self, data=''):
        if self.state == 0:
            title = "【 看板列表 】"
        site = "批踢踢py實業坊"
        self.handler.buffer.format_put(0, 0, site, screen.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.handler.buffer.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
    
    def content(self, data=''):
        self.coln = 2;
        self.height = screen.height - 3
        
class texteditor(scrollableScreenlet):
    def header(self, data=''):
        if self.state == 0:
            title = "【 看板列表 】"
        site = "批踢踢py實業坊"
        self.handler.buffer.format_put(0, 0, site, screen.width,
                                 True, Colors.Yellow, Colors.Blue, Align.Center)
        self.handler.buffer.format_put(0, 0, title, 20,
                                 True, Colors.White, Colors.Blue)
        
    
    def content(self, data=''):
        self.height = screen.height - 1

class anykey(screenlet):
    def content(self, data, screen):
        self.handler.buffer.format_put(screen.height, 0, "按隨意鍵跳出", screen.width,
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        
        if len(data) > 0:
            if screen == 'prev':
                self.handler.pop()
                return
            else:
                self.handler.push(screen, selfdestruct=True) # don't need to keep this screen
                return
'''

def evalString(string):        
    return globals()[string]        