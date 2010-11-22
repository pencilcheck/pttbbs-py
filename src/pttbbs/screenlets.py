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
import itertools
import codecs
import gevent

import screen
from screen import ForegroundColors, BackgroundColors
from screen import Align

from utility import Dimension
from string import lowercase

return_key = ['\r', '\r\x00']
backspace_key = ['\x7f']
arrow_up_key = ['\x1bOA', '\x1b[A']
arrow_down_key = ['\x1bOB', '\x1b[B']
arrow_right_key = ['\x1bOC', '\x1b[C']
arrow_left_key = ['\x1bOD', '\x1b[D']
tab_key = ['\t']
shift_key = '' # it doesn't send

clr_scr = 1
normal = 0

def isKey(input, key):
    for k in key:
        if k == input:
            return True
    return False

def isSingleByte(data):
    if '\x1f' < data < '\x7f':
        return True
    else:
        return False

def isDoubleByte(data):
    if '\x4e\x00' < data < '\x9f\xff' or '\x81\x40' < data < '\xfe\xff' or '\xa1\x40' < data < '\xf9\xff':
        return True
    else:
        return False

class Node:
    def __init__(self, component, parents=[], next=None):
        self.parents = parents # a list of parents and the last one is the control
        self.component = component
        self.next = next

class Nodes:
    def __init__(self):
        self.focusChain = []
        self.focusNode = None

    def add(self, component, parents=[]):

        if isinstance(component, control):
            if len(self.focusChain) > 0:
                node = Node(component, parents, self.focusChain[0])
                self.focusChain[-1].next = node
                self.focusChain.append(node)
            else:
                node = Node(component, parents)
                node.next = node
                self.focusChain.append(node)
        else:
            parents.append(component)
            for comp in component.subcomponents.chain():
                self.add(comp.component, parents)


    def chain(self):
        return self.focusChain

    def setFocusNode(self, component):
        if isinstance(component, screenlet):
            return
        for node in self.focusChain:
            if node.component == component:
                self.focusNode = node


    def getFocusNode(self):
        if not self.focusNode:
            self.focusNode = self.focusChain[0]
        return self.focusNode

    def passFocus(self):
        self.focusNode = self.focusNode.next

    def draw(self, force):
        self.buffer = ""
        for node in self.chain():
            if isinstance(node.component, control):
                if node.component.redrawn:
                    if not node.component.visible:
                        print "erasing", node.component
                        self.buffer += screen.fillBlank(node.component.dimension)
                        node.component.redrawn = False

        for node in self.chain():
            if force:
                if node.component.visible or isinstance(node.component, screenlet):
                    print "force drawing", node.component
                    self.buffer += node.component.draw(True)
                    continue
            else:
                if node.component.visible and node.component.redrawn \
                        or node == self.getFocusNode():
                    print "drawing focus or visible redrawn or screenlet", node.component
                    self.buffer += node.component.draw(force)
            node.component.redrawn = False
        return self.buffer

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
class screenlet(object):
    def __init__(self, handler, dimension):
        self.handler = handler
        self.dimension = dimension
        self.buffer = "" # if this is the terminal it should have the logic for it, else should be the aggregate of all components'
        self.subcomponents = Nodes()

    def handleData(self, data):
        return normal

    def add(self, stuff):
        self.subcomponents.add(stuff)

    def setFocus(self, component):
        self.subcomponents.setFocusNode(component)
        self.handler.focusLine = self.subcomponents.focusNode.component.focusLine
        self.handler.focusColn = self.subcomponents.focusNode.component.focusColn

    def redrawn(self): # this will turn all redrawn flags of subcomponents to true
        for node in self.subcomponents.chain():
            if isinstance(node.component, control):
                node.component.requestRedrawn()
            else:
                node.component.redrawn()

    def passFocus(self):
        self.subcomponents.passFocus()
        self.handler.focusLine = self.subcomponents.focusNode.component.focusLine
        self.handler.focusColn = self.subcomponents.focusNode.component.focusColn

    def update(self, data=''):
        ret = 0
        for node in self.subcomponents.chain():
            if isinstance(node.component, screenlet):
                ret |= node.component.update(data) # clr scr?
            elif node == self.subcomponents.getFocusNode():
                node.component.update(data) # chance to set the redrawn flag
                self.handler.focusLine = node.component.focusLine
                self.handler.focusColn = node.component.focusColn
            else:
                node.component.update() # set redrawn flag

        ret |= self.handleData(data)
        return ret


    def draw(self, force=False): # force will redrawn all components
        return self.subcomponents.draw(force)

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# keywords: focusLine, focusColn, visible
class control(object):
    def __init__(self, handler, dimension, **kwargs):
        self.handler = handler
        self.dimension = dimension
        self.buffer = ""
        self.redrawn = True # for first time
        if 'visible' in kwargs:
            self.visible = kwargs['visible']
        else:
            self.visible = True
        if 'focusLine' in kwargs:
            self.focusLine = kwargs['focusLine']
        else:
            self.focusLine = self.dimension.line
        if 'focusColn' in kwargs:
            self.focusColn = kwargs['focusColn']
        else:
            self.focusColn = self.dimension.coln

    def setVisibility(self, value):
        self.redrawn = True
        self.visible = value
        print self, "called visibility set", self.visible, self.redrawn

    # all control should implement this for behavior when redrawning
    def requestRedrawn(self):
        pass

    def update(self, data=''):
        pass # set redrawn flag if needed


    def draw(self, force=False):
        return self.buffer

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# keywords: focusLine, focusColn, visible
# *align - Alignment
# *l - content
class selectionMenu(control):
    def __init__(self, handler, dimension, align, l, **kwargs):
        super(selectionMenu, self).__init__(handler, dimension, **kwargs)
        self.align = align
        self.list = l
        self.change = [1]*len(self.list)
        self.cursor = 0
        self.offset = 0
        self.handler.resetFocus()

    def getIndex(self):
        return self.cursor + self.offset

    def requestRedrawn(self):
        for i in xrange(len(self.change)):
            self.change[i] = 1

    def update(self, data=''):
        print "selectionMenu update"
        ind = self.getIndex()
        self.change[self.getIndex()] = 1
        # self.cursor can only go from 0 to self.height
        if isKey(data, arrow_up_key):
            if self.cursor == 0:
                if self.offset > 0:
                    self.offset -= 1
            else:
                self.cursor -= 1
        elif isKey(data, arrow_down_key):
            if self.cursor == self.dimension.height-1:
                if self.offset + self.dimension.height < len(self.list)-1:
                    self.offset += 1
            else:
                if self.offset + self.cursor < len(self.list)-1:
                    self.cursor += 1

        if self.getIndex() == ind:
            self.change[self.getIndex()] = 0
        else:
            self.change[self.getIndex()] = 1

    def draw(self, force=False):
        print "selectionMenu draw"
        ind = 0
        self.buffer = ""
        if any(self.change[self.offset:self.offset+self.dimension.height]):
            for i, line in enumerate(self.list):
                if i >= self.offset and ind < self.dimension.height:
                    #print i, self.offset, ind, self.dimension.height
                    if self.change[i]:
                        if self.cursor == ind:
                            self.buffer = self.buffer + screen.format_puts(self.dimension.line + ind, self.dimension.coln, line.strip(), self.dimension.width, self.align, fg=ForegroundColors.White, bg=BackgroundColors.Yellow)
                        else:
                            self.buffer = self.buffer + screen.format_puts(self.dimension.line + ind, self.dimension.coln, line.strip(), self.dimension.width, self.align)
                        self.change[i] = 0
                    ind = ind + 1

        return self.buffer

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# *l - content
# keywords: visible
class scrollableControl(control):
    def __init__(self, handler, dimension, l, **kwargs):
        super(scrollableControl, self).__init__(handler, dimension, **kwargs)
        self.list = l
        self.offset = 0
        self.change = [1]*len(self.list)

    def getIndex(self):
        return self.offset

    #TODO: need to minimize refreshing buffer, now need to test
    def update(self, data=''):
        # self.cursor can only go from 0 to self.height
        if isKey(data, arrow_up_key):
            if self.offset > 0:
                self.offset -= 1
                self.change = self.change[:self.offset] + [1]*self.dimension.height + self.change[self.offset+self.dimension.height+1:]
        elif isKey(data, arrow_down_key):
            if self.offset + self.dimension.height < len(self.list)-1:
                self.offset += 1
                self.change = self.change[:self.offset] + [1]*self.dimension.height + self.change[self.offset+self.dimension.height+1:]

    def draw(self, force=False):
        ind = 0
        for i, line in enumerate(self.list):
            if i >= self.offset and ind < self.dimension.height:
                if self.change[i]:
                    self.buffer = self.buffer + screen.puts(self.dimension.line + ind, self.dimension.coln, line.strip())
                    self.change[i] = 0
                ind = ind + 1
        return self.buffer

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# keywords: focusLine, focusColn, visible
# *path - the path of the file
class art(control):
    def __init__(self, handler, dimension, path, **kwargs):
        super(art, self).__init__(handler, dimension, **kwargs)
        self.buffer = screen.move_cursor(self.line, self.coln)
        self.file = path

        for i, line in enumerate(open(self.file)):
            if i < self.dimension.height:
                self.buffer = self.buffer + line[:self.dimension.width] + screen.move_cursor_down(1) + screen.move_cursor_left(self.dimension.width)

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# *msg, length, align
# keywords: focusLine, focusColn, fg, bg, visible
class label(control):
    def __init__(self, handler, dimension, *args, **kwargs):
        super(label, self).__init__(handler, dimension, **kwargs)
        self.data = args[0]

        if len(args) == 1:
                self.buffer = screen.puts(self.dimension.line, self.dimension.coln, self.data, **kwargs)

        if len(args) == 3:
                self.buffer = screen.format_puts(self.dimension.line, self.dimension.coln, args[0], args[1], args[2], **kwargs)


# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# *length, concealed
# keywords: focusLine, focusColn, visible
class input(control):
    def __init__(self, handler, dimension, *args, **kwargs):
        super(input, self).__init__(handler, dimension, **kwargs)
        self.length = args[0]
        self.concealed = False if len(args) < 2 else args[1]
        self.insert = 0
        self.data = ""

    def moveRight(self, n):
        if self.insert < min(self.length - n, len(self.data)):
            self.insert = self.insert + n
        
    def moveLeft(self, n):
        if self.insert >= n:
            self.insert = self.insert - n
                
    def backSpace(self):
        if self.insert > 0:
                # check for double byte character
                self.data = self.data[:self.insert-1] + self.data[self.insert:]
                self.moveLeft(1)
        if self.insert == 0 and len(self.data) == 0:
            self.data = screen.commands['BEL']

    def addInput(self, data):
        if len(self.data) < self.length-1: # minus 1 for the cursor
            self.data = self.data[:self.insert] + data + self.data[self.insert:]

            # watch out for double byte
            self.moveRight(len(data))

    def update(self, data=''):
        if len(self.data) > 0 and self.data[-1] == screen.commands['BEL']:
            print repr(self.data), repr(screen.commands['BEL'])
            self.data = self.data[:-1]
        if isKey(data, backspace_key): # backspace pressed
            self.redrawn = True
            self.backSpace()
        elif isKey(data, arrow_right_key):
            self.redrawn = True
            self.moveRight(1)
        elif isKey(data, arrow_left_key):
            self.redrawn = True
            self.moveLeft(1)
        elif len(data) > 0:
            if isDoubleByte(data) or isSingleByte(data):
                self.redrawn = True
                self.addInput(data)

        if not self.concealed:
            self.focusColn = self.dimension.coln + self.insert


    def draw(self, force=False):

        if self.concealed:
            self.buffer = screen.format_puts(self.dimension.line, self.dimension.coln, self.data, self.length, Align.Left, fg=ForegroundColors.Black, bg=BackgroundColors.Black, concealed=self.concealed)
        else:
            self.buffer = screen.format_puts(self.dimension.line, self.dimension.coln, self.data, self.length, Align.Left, fg=ForegroundColors.Black, bg=BackgroundColors.White, concealed=self.concealed)
        return self.buffer

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# *location - the location of the screen
# *title - the middle text on the header
class header(screenlet):
    def __init__(self, handler, dimension, location, title):
        if dimension == None:
            super(header, self).__init__(handler, Dimension(0, 0, handler.width, 1))
        else:
            super(header, self).__init__(handler, dimension)

        self.location = location
        self.title = title
        
        # just for testing
        #self.location = u"【 主功能表 】"
        #self.title = u"批踢踢py實業坊"
        # end
        
        #self.subcomponents.append(label(self.handler, 0, 0, self.title, self.handler.width, Align.Center, fg=ForegroundColors.Black, bg=BackgroundColors.White))
        self.subcomponents.add(label(self.handler, self.dimension, self.title, self.dimension.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.LightBlue))
        self.subcomponents.add(label(self.handler, self.dimension, self.location, fg=ForegroundColors.Yellow, bg=BackgroundColors.LightBlue))

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# anykey - if this will be anykey footer
class footer(screenlet):
    def __init__(self, handler, dimension, anykey=False):
        if dimension == None:
            super(footer, self).__init__(handler, Dimension(handler.height, 0, handler.width, 1))
        else:
            super(footer, self).__init__(handler, dimension)

        if anykey:
            self.label = label(self.handler, self.dimension, u"按隨意鍵跳出", self.dimension.width, Align.Center, fg=ForegroundColors.Cyan, bg=BackgroundColors.Blue)
            self.subcomponents.add(self.label)
        else:
            self.title = ''
            self.time = ''
            self.number = ''
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


# arguments:
# *handler - the routine class
# *dimension - a Dimension object
class login(screenlet):
    def __init__(self, handler, dimension):
        super(login, self).__init__(handler, dimension)
        self.id = ''
        self.pw = ''
        
        title = u'=Welcome to BBS='
        warning = u'帳號或密碼有錯誤，請重新輸入。'
        lenwarning = len(warning.encode('big5'))
        enterid = u'請輸入帳號，或以 guest 參觀，或以 new 註冊： '
        lenenterid = len(enterid.encode('big5'))
        enterpw = u'請輸入密碼：'
        lenenterpw = len(enterpw.encode('big5'))
        
        #artwork = art(self.handler, 0, 0, self.width, self.height, '../../res/Welcome_birth')

        self.artwork = label(self.handler, Dimension(self.dimension.height / 2, 0, self.dimension.width, self.dimension.height), title, self.dimension.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.White)
        self.idLabel = label(self.handler, Dimension(self.dimension.height / 2 + 5, 0, lenenterid, 1), enterid)
        self.idInput = input(self.handler, Dimension(self.dimension.height / 2 + 5, lenenterid+1, 20, 1), 20, False)

        self.pwLabel = label(self.handler, Dimension(self.dimension.height / 2 + 5, 0, lenenterpw, 1), enterpw, visible=False)
        self.pwInput = input(self.handler, Dimension(self.dimension.height / 2 + 5, lenenterpw+1, 20, 1), 20, True, visible=False)
        self.warningLabel = label(self.handler, Dimension(self.dimension.height / 2 + 6, 0, lenwarning, 1), warning, visible=False)

        self.subcomponents.add(self.idLabel)
        self.subcomponents.add(self.idInput)
        self.subcomponents.add(self.pwLabel)
        self.subcomponents.add(self.pwInput)
        self.subcomponents.add(self.artwork)
        self.subcomponents.add(self.warningLabel)

        self.setFocus(self.idInput)

    def registrationProcedures(self):
        self.handler.stack.pop()
        self.handler.stack.push(registration(self.handler, self.dimension))
        self.handler.resetFocus()

    def loginProcedures(self):
        self.handler.id = self.id
        self.handler.createSession()
        self.handler.stack.pop()
        self.handler.stack.push(welcome(self.handler, self.dimension))
        self.handler.resetFocus()

    def handleData(self, data=''):
        if isKey(data, return_key):
            self.id = self.idInput.data
            self.pw = self.pwInput.data
            if len(self.id) > 0 and self.idInput.visible:
                if self.id == "new":
                    self.registrationProcedures()
                    return clr_scr

                elif self.id == "guest":
                    self.loginProcedures()
                    return clr_scr

                self.idLabel.setVisibility(False)
                self.idInput.setVisibility(False)
                self.pwLabel.setVisibility(True)
                self.pwInput.setVisibility(True)
                self.setFocus(self.pwInput)
                self.warningLabel.setVisibility(False)

            elif self.pwInput.visible:
                # validate id and pw
                if self.handler.userLookup(self.id, self.pw):
                    self.loginProcedures()
                    return clr_scr
                else:
                    self.pwInput.data = ""
                    self.idLabel.setVisibility(True)
                    self.idInput.setVisibility(True)
                    self.pwLabel.setVisibility(False)
                    self.pwInput.setVisibility(False)
                    self.setFocus(self.idInput)
                    self.warningLabel.setVisibility(True)
        return normal

    # the methodology behind this is always static first, always the lowest layer first, think of layers, paint the least
    # dynamic layer first
    def content(self, data=''):
        
        # draw background
        self.drawScrFromFile("../../res/Welcome_login")
    
        #mon = str(localtime().tm_mon)
   
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
                    self.handler.resetFocus()
                    return
                if self.id == "guest":
                    self.handler.user_lookup(self.id, self.pw) # just to associate guest with IP
                    self.handler.push(welcome, selfdestruct=True)
                    self.handler.resetFocus()
                    return
                self.handler.buffer.finish_for_input()
                self.changeState(1)

            else: # password
                self.pw = self.handler.buffer.input
                if self.handler.user_lookup(self.id, self.pw) == 0: # 0 success
                    #self.handler.buffer.print_input()
                    self.handler.buffer.finish_for_input()
                    self.handler.push(welcome, selfdestruct=True)
                    self.handler.resetFocus()
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


class encoding(screenlet):
    def __init__(self, handler, dimension):
        super(encoding, self).__init__(handler, dimension)
        self.confirm = label(self.handler, Dimension(self.dimension.height, 0, self.dimension.width, self.dimension.height), u'如果你可以看到這段句子，請按確認鍵繼續。')

        self.options = [u"utf8", u"big5"]
        self.list = selectionMenu(self.handler, Dimension(self.dimension.height / 2, 0, self.dimension.width, self.dimension.height), Align.Center, self.options)
        self.list.focus = True
        self.list.focusLine = -1
        self.list.focusColn = -1

        self.subcomponents.append(self.confirm)
        self.subcomponents.append(self.list)

    # return 1 if clear screen is needed
    def handleData(self, data=''):
        if isKey(data, return_key):
            self.handler.stack.pop()
            self.handler.stack.push(login(self.handler, Dimension(0, 0, self.handler.width, self.handler.height)))
            self.handler.resetFocus()
            return 1

        self.handler.encoding = self.options[self.list.offset + self.list.cursor]
        #print "encoding is", self.handler.encoding, "and", self.subcomponents[1].offset + self.subcomponents[1].cursor
        return 0

class resolution(screenlet):
    def __init__(self, handler, line, coln, width, height):
        super(resolution, self).__init__(handler, line, coln, width, height)
        self.focusable = True
        print "resolution init"

        self.buffs.append("80x24")
        self.buffs.append("160x24")
        self.buffs.append("80x48")

class welcome(screenlet):
    def __init__(self, handler, dimension):
        super(welcome, self).__init__(handler, dimension)

        self.footer = footer(self.handler, None, True)

        self.subcomponents.add(self.footer)


    def handleData(self, data=''):
        if len(data) > 0:
            self.handler.stack.pop()
            self.handler.stack.push(topMenu(self.handler, self.dimension))
            self.handler.resetFocus()
            return clr_scr

        return normal

class topMenu(screenlet):
    def __init__(self, handler, dimension):
        super(topMenu, self).__init__(handler, dimension)

        self.items = [u"(A)nnouncement",
                      u"(B)oards",
                      u"(C)hatroom",
                      u"(G)ames",
                      u"(S)ettings",
                      u"(Q)uit"]
        self.selectionMenu = selectionMenu(self.handler, Dimension(4, 20, 45, self.dimension.height - 2), Align.Left, self.items)
        self.subcomponents.add(self.selectionMenu)

    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            self.handler.stack.pop()
            self.handler.resetFocus()
            return clr_scr
        elif isKey(data, arrow_right_key) or isKey(data, return_key):
            self.selectionMenu.requestRedrawn()
            if self.selectionMenu.getIndex() == 0: # Announcement
                self.handler.stack.push(announce(self.handler, self.dimension))
            elif self.selectionMenu.getIndex() == 1: # Boards
                self.handler.stack.push(boardlist(self.handler, self.dimension, "/"))
            elif self.selectionMenu.getIndex() == 2: # Chatroom
                self.handler.stack.push(notfinished(self.handler, self.dimension))
            elif self.selectionMenu.getIndex() == 3: # Games
                self.handler.stack.push(notfinished(self.handler, self.dimension))
            elif self.selectionMenu.getIndex() == 4: # Settings
                self.handler.stack.push(notfinished(self.handler, self.dimension))
            else: # Quit
                # double check with input textbox

                # confirm
                self.handler.stack.push(quit(self.handler, self.dimension))
            self.handler.resetFocus()
            return clr_scr

        return normal


class quit(screenlet):
    def __init__(self, handler, dimension):
        super(quit, self).__init__(handler, dimension)

        self.subcomponents.add(art(self.handler, self.dimension, ))

    def handleData(self, data=''):
        if len(data) > 0:
            self.handler.disconnect()
            return clr_scr

        return normal

class notfinished(screenlet):
    def __init__(self, handler, dimension):
        super(notfinished, self).__init__(handler, dimension)

        self.msg = u'對不起，請稍後再試！'

        self.subcomponents.add(footer(self.handler, self.dimension, True))
        self.subcomponents.add(label(self.handler, Dimension(self.dimension.height / 2, 0, len(self.msg.encode('big5')), 1), self.msg))


    def handleData(self, data=''):
        if len(data) > 0:
            self.handler.stack.pop()
            return clr_scr

        return normal

# deprecated
class discussionboards(screenlet):
    def __init__(self, handler, dimension):
        super(discussionboards, self).__init__(handler, dimension)

    def handleData(self, data=''):
        #if self.isKey(data, )

        msg = "test skjdkf sdlkfjlsdkj  sdfk lkj"
        self.handler.buffer.format_put(screen.height - 1, 0, msg, screen.width)

        if self.isKey(data, arrow_left_key):
            self.buff = []
            self.handler.pop()    
            return
        elif self.isKey(data, arrow_right_key) or self.isKey(data, return_key):
            self.buff = []
            result = self.offset + self.cursor
            self.handler.push(None, pathappend=str(result))
            self.handler.resetFocus()
            return

        self.commandinterface(data)

        self.buff = self.handler.loadBoardList()

        # not used
        for i, line in enumerate(open('../../res/boardlist')):
            self.buff.append(line.strip())
        # end

class announce(screenlet):
    def __init__(self, handler, dimension):
        super(announce, self).__init__(handler, dimension)

        self.announcements = scrollableControl(self.handler, Dimension(4, 0, self.dimension.width, self.dimension.height-2), self.handler.loadAnnouncement())
        self.header = header(self.handler, None, u"【 主功能表 】", u"批踢踢py實業坊")
        self.footer = footer(self.handler, None)

        self.add(self.announcements)
        self.add(self.header)
        self.add(self.footer)

class boardlist(screenlet):
    def __init__(self, handler, dimension, cwd):
        super(boardlist, self).__init__(handler, dimension)

        self.cwd = cwd
        self.boards = scrollableControl(self.handler, self.dimension, self.handler.loadBoards(self.cwd))

        self.header = header(self.handler, Dimension())
        self.footer = footer()


class threadlist(screenlet):
    def __init__(self, handler, dimension, cwd):
        super(threadlist, self).__init__(handler, dimension)

        self.cwd = cwd
        self.threads = scrollableControl(self.handler, self.dimension, self.handler.loadThreads(self.cwd))

        self.header = header()
        self.footer = footer()

class threadViewer(screenlet):
    def __init__(self, handler, dimension, cwd):
        super(threadViewer, self).__init__(handler, dimension)

class editor(screenlet):
    def __init__(self, handler, dimension, content):
        super(editor, self).__init__(handler, dimension)

        self.content = content

        self.footer = footer()

class registration(screenlet):
    def __init__(self, handler, dimension):
        super(registration, self).__init__(handler, dimension)


def evalString(string):
    return globals()[string]
