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
from copy import copy
from copy import deepcopy

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
ctrl_x = ['\x18']
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

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
class screenlet(object):
    def __init__(self, handler, dimension):
        self.handler = handler
        self.dimension = dimension
        self.controls = []
        self.focusIndex = None

    def handleData(self, data):
        return normal

    def add(self, control):
        self.controls.append(control)

    def focusedControl(self):
        return self.controls[self.focusIndex] if self.focusIndex != None else None

    def nextFocusedControl(self):
        if self.focusIndex == len(self.controls)-1:
            self.controls[self.focusIndex].focused = False
            self.focusIndex == 0
            self.controls[self.focusIndex].focused = True
        else:
            self.controls[self.focusIndex].focused = False
            self.focusIndex += 1
            self.controls[self.focusIndex].focused = True

    def setFocusedControl(self, control):
        for i, item in enumerate(self.controls):
            item.focused = False
            if item == control:
                self.focusIndex = i
                item.focused = True
                return

    def update(self, data=''):
        for i, item in enumerate(self.controls):
            item.update(data if i == self.focusIndex else '')

        if not self.focusIndex:
            for item in self.controls:
                item.update(data)

        return self.handleData(data)

    def draw(self, force=False):
        self.buffer = ""
        for item in self.controls:
            if item.redrawn and not item.visible:
                self.buffer += screen.fillBlank(item.dimension)
                item.redrawn = False

        for item in self.controls:
            if (force or item.redrawn) and item.visible:
                self.buffer += item.draw()
                item.redrawn = False

        focus = ''
        if self.focusedControl():
            focus = screen.move_cursor(self.focusedControl().focusLine, self.focusedControl().focusColn)
        else:
            focus = screen.move_cursor(self.handler.height+1, self.handler.width+1)
        return self.buffer + focus

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# keywords: focusLine, focusColn, visible, minACL
class control(object):
    def __init__(self, handler, dimension, **kwargs):
        self.handler = handler
        self.dimension = dimension
        self.buffer = ""
        self.visible = kwargs['visible'] if 'visible' in kwargs else True
        self.minACL = kwargs['minACL'] if 'minACL' in kwargs else 0
        self.focused = False
        self.focusLine = kwargs['focusLine'] if 'focusLine' in kwargs else self.dimension.line
        self.focusColn = kwargs['focusColn'] if 'focusColn' in kwargs else self.dimension.coln
        self.redrawn = False

    def setVisibility(self, flag):
        if not flag == self.visible:
            self.redrawn = True
        self.visible = flag

    def update(self, data=''):
        pass # set redrawn flag if needed


    def draw(self):
        return self.buffer

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# *l - menu list
# keywords: focusLine, focusColn, visible, minACL
class selectionMenu(control):
    def __init__(self, handler, dimension, l, **kwargs):
        super(selectionMenu, self).__init__(handler, dimension, **kwargs)
        self.menulist = l
        self.cursor = 0
        self.offset = 0
        self.change = [1]*len(self.menulist)

    def getIndex(self):
        return self.cursor + self.offset

    def redraw(self):
        for i in xrange(len(self.change)):
            self.change[i] = 1

    def update(self, data=''):
        if len(self.menulist) == 0: # don't need to update if the list is empty
            return
        print "selectionMenu update"
        ind = self.getIndex()
        self.change[self.getIndex()] = 1
        # self.cursor can only go from 0 to self.height
        if isKey(data, arrow_up_key):
            if self.cursor == 0:
                if self.offset > 0:
                    self.offset -= 1
                    self.redraw()
            else:
                self.cursor -= 1
            self.redrawn = True
        elif isKey(data, arrow_down_key):
            if self.cursor == self.dimension.height-1:
                if self.offset + self.dimension.height < len(self.menulist)-1:
                    self.offset += 1
                    self.redraw()
            else:
                if self.offset + self.cursor < len(self.menulist)-1:
                    self.cursor += 1
            self.redrawn = True

        if self.getIndex() == ind:
            self.change[self.getIndex()] = 0
        else:
            self.change[self.getIndex()] = 1

    def draw(self):
        ind = 0
        self.buffer = ""
        if any(self.change[self.offset:self.offset+self.dimension.height]):
            print "selectionMenu draw"
            for i, line in enumerate(self.menulist):
                if i >= self.offset and ind < self.dimension.height:
                    #print i, self.offset, ind, self.dimension.height
                    if self.change[i]:
                        if self.cursor == ind:
                            self.buffer = self.buffer + screen.format_puts(self.dimension.line + ind, self.dimension.coln, line.strip(), self.dimension.width, Align.Left, fg=ForegroundColors.White, bg=BackgroundColors.Yellow)
                        else:
                            self.buffer = self.buffer + screen.format_puts(self.dimension.line + ind, self.dimension.coln, line.strip(), self.dimension.width, Align.Left)
                        self.change[i] = 0
                    ind = ind + 1

        return self.buffer

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# *l - list content
# keywords: focusLine, focusColn, visible, minACL
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
            self.redrawn = True
        elif isKey(data, arrow_down_key):
            if self.offset + self.dimension.height < len(self.list)-1:
                self.offset += 1
                self.change = self.change[:self.offset] + [1]*self.dimension.height + self.change[self.offset+self.dimension.height+1:]
            self.redrawn = True

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
# *path - the path of the file
# keywords: focusLine, focusColn, visible, minACL
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
# keywords: focusLine, focusColn, fg, bg, visible, minACL
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
# keywords: focusLine, focusColn, visible, minACL
class input(control):
    def __init__(self, handler, dimension, *args, **kwargs):
        super(input, self).__init__(handler, dimension, **kwargs)
        self.length = args[0]
        self.concealed = False if len(args) < 2 else args[1]
        self.internalCursor = 0
        self.data = ""

    def insert(self):
        return len(self.data[:self.internalCursor].encode('big5'))

    def moveRight(self, n):
        if self.internalCursor < min(self.length - n, len(self.data)):
            self.internalCursor += n

    def moveLeft(self, n):
        if self.internalCursor >= n:
            self.internalCursor = self.internalCursor - n

    def backSpace(self):
        if self.internalCursor == 0:
            self.data = screen.commands['BEL']

        elif self.internalCursor > 0:
            self.data = self.data[:self.internalCursor-1] + self.data[self.internalCursor:]
            self.moveLeft(1)

    def addInput(self, data):
        if len(self.data) < self.length-1: # minus 1 for the cursor
            self.data = self.data[:self.internalCursor] + data + self.data[self.internalCursor:]

            # watch out for double byte
            self.moveRight(len(data))

    def update(self, data=''):
        print "input update"
        if screen.commands['BEL'] in self.data:
            self.data = self.data.replace(screen.commands['BEL'], '')

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
            #if isDoubleByte(data) or isSingleByte(data):
            if data > '\x20':
                self.redrawn = True
                self.addInput(data)
                print "adding input data", repr(data)

        if not self.concealed:
            self.focusColn = self.dimension.coln + self.insert()


    def draw(self):
        self.buffer = ''
        if self.concealed:
            self.buffer = screen.format_puts(self.dimension.line, self.dimension.coln, self.data, self.length, Align.Left, fg=ForegroundColors.Black, bg=BackgroundColors.Black, concealed=self.concealed)
        else:
            self.buffer = screen.format_puts(self.dimension.line, self.dimension.coln, self.data, self.length, Align.Left, fg=ForegroundColors.Black, bg=BackgroundColors.White, concealed=self.concealed)
        print "input draw", repr(self.buffer)
        return self.buffer

# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# keywords: focusLine, focusColn, visible, minACL
class multilineinput(control):
    def __init__(self, handler, dimension, **kwargs):
        super(multilineinput, self).__init__(handler, dimension, **kwargs)
        self.cursor = [0,0] # line, coln
        self.inputs = []
        for i in xrange(self.dimension.height):
            self.inputs.append(input(self.handler, Dimension(self.dimension.line + i, self.dimension.coln, self.dimension.width, 1), self.dimension.width))

    def data(self):
        return '\n'.join([d.data for d in self.inputs])

    def update(self, data=''):
        print "multi-line input update"
        self.redrawn = True
        self.inputs[self.cursor[0]].update(data)
        self.cursor[1] = self.inputs[self.cursor[0]].focusColn

        if isKey(data, return_key):
            self.cursor[0] += 1 # more work to do actually, need to move all data one input below
            self.cursor[1] = self.inputs[self.cursor[0]].focusColn
        elif isKey(data, arrow_up_key):
            if self.cursor[0] > 0:
                self.cursor[0] -= 1
                self.cursor[1] = self.inputs[self.cursor[0]].focusColn
        elif isKey(data, arrow_down_key):
            if self.cursor[0] < self.dimension.height:
                self.cursor[0] += 1
                self.cursor[1] = self.inputs[self.cursor[0]].focusColn

        self.focusLine = self.dimension.line + self.cursor[0]
        self.focusColn = self.cursor[1] + 1


    def draw(self):
        self.buffer = ''
        for i, text in enumerate(self.inputs):
            self.buffer += text.draw()
        return self.buffer


# arguments:
# *handler - the routine class
# *dimension - a Dimension object
# *labelText - the label text
# keywords: focusLine, focusColn, visible, minACL, allowedOps
class optionInput(control):
    def __init__(self, handler, dimension, labelText, **kwargs):
        super(optionInput, self).__init__(handler, dimension, **kwargs)

        self.allowedOps = kwargs['allowedOps'] if 'allowedOps' in kwargs else ['Y', 'N']
        self.labelText = labelText + '[' + '/'.join(self.allowedOps) + ']'
        self.label = label(self.handler, Dimension(self.dimension.line, self.dimension.coln, len(self.labelText.encode('big5')), 1), self.labelText)
        self.input = input(self.handler, Dimension(self.dimension.line, self.dimension.coln + len(self.labelText.encode('big5')) + 1, self.dimension.width, 1), max([len(a) for a in self.allowedOps]) + 1)

    def update(self, data=''):
        self.redrawn = True
        self.input.update(data)
        self.focusLine = self.input.focusLine
        self.focusColn = self.input.focusColn

    def draw(self):
        self.buffer = self.label.draw() + self.input.draw()
        return self.buffer

# arguments:
# *handler - the routine class
# *location - the location of the screen
# *title - the middle text on the header
# keywords: focusLine, focusColn, visible, minACL
class header(control):
    def __init__(self, handler, location, title, **kwargs):
        super(header, self).__init__(handler, Dimension(0, 0, handler.width, 1), **kwargs)

        # just for testing
        #self.location = u"【 主功能表 】"
        #self.title = u"批踢踢py實業坊"

        self.buffer = label(self.handler, self.dimension, title, self.dimension.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.LightBlue).buffer + label(self.handler, self.dimension, location, fg=ForegroundColors.Yellow, bg=BackgroundColors.LightBlue).buffer

# arguments:
# *handler - the routine class
# keywords: focusLine, focusColn, visible, minACL
class anykey(control):
    def __init__(self, handler, **kwargs):
        super(anykey, self).__init__(handler, Dimension(handler.height, 0, handler.width, 1), **kwargs)

        self.buffer = label(self.handler, self.dimension, u"按隨意鍵跳出", self.dimension.width, Align.Center, fg=ForegroundColors.Cyan, bg=BackgroundColors.Blue).buffer

# arguments:
# *handler - the routine class
# keywords: focusLine, focusColn, visible, minACL
class footer(control):
    def __init__(self, handler, **kwargs):
        super(footer, self).__init__(handler, Dimension(handler.height, 0, handler.width, 1), **kwargs)

        self.buffer = label(self.handler, self.dimension, u"批踢踢py實業坊", self.dimension.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.LightBlue).buffer + label(self.handler, self.dimension, u"【 主功能表 】", fg=ForegroundColors.Yellow, bg=BackgroundColors.LightBlue).buffer

        '''
        self.title = ''
        self.time = ''
        self.number = ''
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

        self.add(self.idLabel)
        self.add(self.idInput)
        self.add(self.pwLabel)
        self.add(self.pwInput)
        self.add(self.artwork)
        self.add(self.warningLabel)

        self.setFocusedControl(self.idInput)

    def registrationProcedures(self):
        self.handler.stack.pop()
        self.handler.stack.push(registration(self.handler, self.dimension))

    def loginProcedures(self):
        self.handler.id = self.id
        self.handler.createSession()
        self.handler.stack.pop()
        self.handler.stack.push(welcome(self.handler, self.dimension))

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
                self.warningLabel.setVisibility(False)
                self.setFocusedControl(self.pwInput)

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
                    self.setFocusedControl(self.idInput)
                    self.warningLabel.setVisibility(True)
        return normal

class welcome(screenlet):
    def __init__(self, handler, dimension):
        super(welcome, self).__init__(handler, dimension)

        self.anykey = anykey(self.handler)

        self.add(self.anykey)


    def handleData(self, data=''):
        if len(data) > 0:
            self.handler.stack.pop()
            self.handler.stack.push(topMenu(self.handler, self.dimension))
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
        self.selectionMenu = selectionMenu(self.handler, Dimension(4, 20, 45, self.dimension.height - 2), self.items)
        self.header = header(self.handler, u"【主功能表】", u"批踢踢py實業坊")
        self.footer = footer(self.handler)

        self.add(self.header)
        self.add(self.footer)
        self.add(self.selectionMenu)

    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            pass
        elif isKey(data, arrow_right_key) or isKey(data, return_key):
            self.selectionMenu.redraw()
            if self.selectionMenu.getIndex() == 0: # Announcement
                self.handler.stack.push(announce(self.handler, self.dimension))
            elif self.selectionMenu.getIndex() == 1: # Boards
                self.handler.stack.push(boardlist(self.handler, self.dimension, "/boards"))
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

        self.add(footer(self.handler))
        self.add(label(self.handler, Dimension(self.dimension.height / 2, 0, len(self.msg.encode('big5')), 1), self.msg))


    def handleData(self, data=''):
        if len(data) > 0:
            self.handler.stack.pop()
            return clr_scr

        return normal

class createBoard(screenlet):
    def __init__(self, handler, dimension, path):
        super(createBoard, self).__init__(handler, dimension)
        self.path = path
        self.title = ''

        warning = u'標題格式有錯誤，請重新輸入。'
        enterid = u'請輸入看板標題： '

        self.titlelabel = label(self.handler, Dimension(self.dimension.height / 2 + 5, 0, len(enterid.encode('big5')), 1), enterid)
        self.titleinput = input(self.handler, Dimension(self.dimension.height / 2 + 5, len(enterid.encode('big5'))+1, 20, 1), 20, False)

        self.warninglabel = label(self.handler, Dimension(self.dimension.height / 2 + 6, 0, len(warning.encode('big5')), 1), warning, visible=False)

        self.add(self.titlelabel)
        self.add(self.titleinput)
        self.add(self.warninglabel)

        self.setFocusedControl(self.titleinput)

    def handleData(self, data=''):
        self.title = self.titleinput.data
        if isKey(data, tab_key):
            self.nextFocusedControl()
        if isKey(data, return_key):
            if self.handler.addBoard(self.path, self.title):
                print "added board successfully"
                self.handler.stack.pop() #destroy it
                self.handler.stack.push(boardlist(self.handler, self.dimension, self.path))
                return clr_scr
            else:
                self.warninglabel.setVisibility(True)
        return normal

class createThread(screenlet):
    def __init__(self, handler, dimension, path):
        super(createThread, self).__init__(handler, dimension)
        self.path = path
        self.title = ''
        self.content = ''

        warning = u'標題格式有錯誤，請重新輸入。'
        enterid = u'請輸入看板標題： '

        self.titlelabel = label(self.handler, Dimension(3, 0, len(enterid.encode('big5')), 1), enterid)
        self.titleinput = input(self.handler, Dimension(3, len(enterid.encode('big5'))+1, 20, 1), 20, False)

        self.warninglabel = label(self.handler, Dimension(4, 0, len(warning.encode('big5')), 1), warning, visible=False)

        # need a control for multi-line input
        self.contentinput = multilineinput(self.handler, Dimension(6, 0, self.dimension.width, 5))

        # need a control for confirmation
        self.confirmationinput = optionInput(self.handler, Dimension(self.dimension.height - 3, 0, self.dimension.width, 1), u'請確認：')

        self.add(self.titlelabel)
        self.add(self.titleinput)
        self.add(self.warninglabel)
        self.add(self.contentinput)
        self.add(self.confirmationinput)

        self.setFocusedControl(self.titleinput)

    def handleData(self, data=''):
        self.title = self.titleinput.data
        self.content = self.contentinput.data()
        if isKey(data, tab_key):
            if self.titleinput.focused:
                self.setFocusedControl(self.contentinput)

            elif self.contentinput.focused:
                self.setFocusedControl(self.confirmationinput)

            elif self.confirmationinput.focused:
                self.setFocusedControl(self.titleinput)

        if isKey(data, return_key):
            if self.confirmationinput.focused and self.confirmationinput.input.data == u'Y':
                if self.handler.addThread(self.path + '/' + self.title, self.title, self.content):
                    print "added thread successfully"
                    self.handler.stack.pop() #destroy it
                    self.handler.stack.push(threadlist(self.handler, self.dimension, self.path))
                    return clr_scr
            else:
                self.setFocusedControl(self.contentinput)

        return normal


class announce(screenlet):
    def __init__(self, handler, dimension):
        super(announce, self).__init__(handler, dimension)

        self.announcements = scrollableControl(self.handler, Dimension(4, 0, self.dimension.width, self.dimension.height-2), self.handler.loadAnnouncement())
        self.header = header(self.handler, u"【公佈欄】", u"批踢踢py實業坊")
        self.footer = footer(self.handler)

        self.add(self.announcements)
        self.add(self.header)
        self.add(self.footer)

    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            self.handler.stack.pop()
            return clr_scr
        return normal

class boardlist(screenlet):
    def __init__(self, handler, dimension, cwd):
        super(boardlist, self).__init__(handler, dimension)

        self.cwd = cwd
        self.boards = selectionMenu(self.handler, Dimension(3, 0, self.dimension.width, self.dimension.height), self.handler.loadBoards(self.cwd))


        self.administration = label(self.handler, Dimension(2, 0, self.dimension.width, 1),
                "Key C-x creates a board here", self.dimension.width, Align.Left)
        self.header = header(self.handler, u"【看板列表】", u"批踢踢py實業坊")
        self.footer = footer(self.handler)

        self.add(self.administration)
        self.add(self.boards)

        self.add(self.header)
        self.add(self.footer)

    def handleData(self, data=''):
        if isKey(data, ctrl_x):
            self.handler.stack.pop() # destroy it first
            self.handler.stack.push(createBoard(self.handler, self.dimension, self.cwd))
            return clr_scr
        elif isKey(data, arrow_left_key):
            self.handler.stack.pop()
            return clr_scr
        elif isKey(data, arrow_right_key):
            self.boards.redraw()
            self.handler.stack.push(threadlist(self.handler, self.dimension, self.cwd + '/' + self.boards.menulist[self.boards.getIndex()]))
            return clr_scr
        return normal

class threadlist(screenlet):
    def __init__(self, handler, dimension, cwd):
        super(threadlist, self).__init__(handler, dimension)

        self.cwd = cwd
        self.threads = selectionMenu(self.handler, Dimension(3, 0, self.dimension.width, self.dimension.height), self.handler.loadThreads(self.cwd))

        self.administration = label(self.handler, Dimension(2, 0, self.dimension.width, 1), "Key C-x creates a thread", self.dimension.width, Align.Left)

        self.header = header(self.handler, u"【版主：】", u"批踢踢py實業坊")
        self.footer = footer(self.handler)

        self.add(self.administration)
        self.add(self.threads)

        self.add(self.header)
        self.add(self.footer)

    def handleData(self, data=''):
        if isKey(data, ctrl_x):
            self.handler.stack.pop() #destroy it first
            self.handler.stack.push(createThread(self.handler, self.dimension, self.cwd))
            return clr_scr
        elif isKey(data, arrow_left_key):
            self.handler.stack.pop()
            return clr_scr
        elif isKey(data, arrow_right_key):
            self.threads.redraw()
            self.handler.stack.push(threadViewer(self.handler, self.dimension, self.cwd + '/' + self.threads.menulist[self.threads.getIndex()]))
            return clr_scr
        return normal

class threadViewer(screenlet):
    def __init__(self, handler, dimension, cwd):
        super(threadViewer, self).__init__(handler, dimension)
    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            self.handler.stack.pop()
            return clr_scr
        return normal

class editor(screenlet):
    def __init__(self, handler, dimension, content):
        super(editor, self).__init__(handler, dimension)

        self.content = content

        self.footer = footer()
    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            self.handler.stack.pop()
            return clr_scr
        return normal

class registration(screenlet):
    def __init__(self, handler, dimension):
        super(registration, self).__init__(handler, dimension)
    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            self.handler.stack.pop()
            return clr_scr
        return normal


def evalString(string):
    return globals()[string]
