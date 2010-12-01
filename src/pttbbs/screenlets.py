# -*- encoding: UTF-8 -*-

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

yes = 'Y'
no = 'N'

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

class screenlet(object):
    def __init__(self, routine, dimension):
        self.routine = routine
        self.dimension = dimension
        self.controls = []
        self.focusIndex = None

    def handleData(self, data):
        return normal

    def add(self, control):
        self.controls.append(control)

    def focusedControl(self):
        return self.controls[self.focusIndex] if self.focusIndex != None else None

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
            if (force or item.redrawn) and item.visible and item.minACL <= self.routine.acl:
                self.buffer += item.draw()
                item.redrawn = False

        focus = ''
        if self.focusedControl():
            focus = screen.move_cursor(self.focusedControl().focusLine, self.focusedControl().focusColn)
        else:
            focus = screen.move_cursor(self.routine.height+1, self.routine.width+1)
        return self.buffer + focus

class control(object):
    def __init__(self, routine, dimension, **kwargs):
        self.routine = routine
        self.dimension = dimension
        self.focusLine = kwargs['focusLine'] if 'focusLine' in kwargs else self.dimension.line
        self.focusColn = kwargs['focusColn'] if 'focusColn' in kwargs else self.dimension.coln
        self.visible = kwargs['visible'] if 'visible' in kwargs else True
        self.minACL = kwargs['minACL'] if 'minACL' in kwargs else 0
        self.redrawn = False
        self.focused = False
        self.buffer = ""

    def setVisibility(self, flag):
        self.redrawn = True if not flag == self.visible else self.redrawn
        self.visible = flag

    def update(self, data=''):
        pass # set redrawn flag if needed


    def draw(self):
        return self.buffer

class selectionMenu(control):
    def __init__(self, routine, dimension, menu, **kwargs):
        super(selectionMenu, self).__init__(routine, dimension, **kwargs)
        self.menu = menu
        self.change = [1]*len(self.menu)
        self.cursor = 0
        self.offset = 0

    def index(self):
        return self.cursor + self.offset

    def redraw(self):
        self.change = [1]*len(self.menu)

    def update(self, data=''):
        if len(self.menu) == 0: # don't need to update if the list is empty
            return

        print "selectionMenu update"
        ind = self.index()
        self.change[self.index()] = 1
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
                if self.offset + self.dimension.height < len(self.menu)-1:
                    self.offset += 1
                    self.redraw()
            else:
                if self.offset + self.cursor < len(self.menu)-1:
                    self.cursor += 1
            self.redrawn = True

        if self.index() == ind:
            self.change[self.index()] = 0
        else:
            self.change[self.index()] = 1

    def draw(self):
        ind = 0
        self.buffer = ""
        if any(self.change[self.offset:self.offset+self.dimension.height]):
            for i, line in enumerate(self.menu):
                if i >= self.offset and ind < self.dimension.height:
                    #print i, self.offset, ind, self.dimension.height
                    if self.change[i]:
                        if self.cursor == ind:
                            self.buffer = self.buffer + screen.puts(self.dimension.line + ind, self.dimension.coln, line.strip(), self.dimension.width, Align.Left, fg=ForegroundColors.White, bg=BackgroundColors.Yellow)
                        else:
                            self.buffer = self.buffer + screen.puts(self.dimension.line + ind, self.dimension.coln, line.strip(), self.dimension.width, Align.Left)
                        self.change[i] = 0
                    ind = ind + 1

        return self.buffer

class scrollableMenu(control):
    def __init__(self, routine, dimension, menu, **kwargs):
        super(scrollableMenu, self).__init__(routine, dimension, **kwargs)
        self.menu = menu
        self.offset = 0
        self.change = [1]*len(self.menu)

    def index(self):
        return self.offset

    def update(self, data=''):
        if isKey(data, arrow_up_key):
            if self.offset > 0:
                self.offset -= 1
                self.change = self.change[:self.offset] + [1]*self.dimension.height + self.change[self.offset+self.dimension.height+1:]
                self.redrawn = True
        elif isKey(data, arrow_down_key):
            if self.offset + self.dimension.height < len(self.menu)-1:
                self.offset += 1
                self.change = self.change[:self.offset] + [1]*self.dimension.height + self.change[self.offset+self.dimension.height+1:]
                self.redrawn = True

    def draw(self, force=False):
        ind = 0
        for i, line in enumerate(self.menu):
            if i >= self.offset and ind < self.dimension.height:
                if self.change[i]:
                    self.buffer = self.buffer + screen.puts(self.dimension.line + ind, self.dimension.coln, line.strip())
                    self.change[i] = 0
                ind = ind + 1
        return self.buffer

class art(control):
    def __init__(self, routine, dimension, file, **kwargs):
        super(art, self).__init__(routine, dimension, **kwargs)
        self.buffer = screen.move_cursor(self.line, self.coln)
        self.file = file

        for i, line in enumerate(open(self.file)):
            if i < self.dimension.height:
                self.buffer = self.buffer + line[:self.dimension.width] + screen.move_cursor_down(1) + screen.move_cursor_left(self.dimension.width)

class label(control):
    def __init__(self, routine, dimension, msg, length=None, align=Align.Left, **kwargs):
        super(label, self).__init__(routine, dimension, **kwargs)
        "display a label"

        self.data = msg
        self.buffer = screen.puts(self.dimension.line, self.dimension.coln, self.data, length, align, **kwargs)

class input(control):
    def __init__(self, routine, dimension, **kwargs):
        super(input, self).__init__(routine, dimension, **kwargs)
        "display an input box"

        self.cursor = 0
        self.length = self.dimension.width
        self.concealed = kwargs['concealed'] if 'concealed' in kwargs else False
        self.fg = ForegroundColors.DarkGray if 'fg' not in kwargs else kwargs['fg']
        if 'bg' not in kwargs:
            if self.concealed:
                self.bg = BackgroundColors.Black
            else:
                self.bg = BackgroundColors.White
        else:
            self.bg = kwargs['bg']
        self.data = kwargs['default'] if 'default' in kwargs else ''

    def insert(self):
        return len(self.data[:self.cursor].encode('big5'))

    def moveRight(self, n):
        if self.cursor < min(self.length - n, len(self.data)):
            self.cursor += n

    def moveLeft(self, n):
        if self.cursor >= n:
            self.cursor -= n

    def backSpace(self):
        if self.cursor == 0:
            self.data = screen.commands['BEL']

        elif self.cursor > 0:
            self.data = self.data[:self.cursor-1] + self.data[self.cursor:]
            self.moveLeft(1)
            self.redrawn = True

    def addInput(self, data):
        if len(self.data) < self.length-1: # minus 1 for the cursor
            self.data = self.data[:self.cursor] + data + self.data[self.cursor:]
            self.moveRight(len(data))
            self.redrawn = True

    def update(self, data=''):
        if screen.commands['BEL'] in self.data:
            self.data = self.data.replace(screen.commands['BEL'], '')

        if isKey(data, backspace_key):
            self.backSpace()
        elif isKey(data, arrow_right_key):
            self.moveRight(1)
        elif isKey(data, arrow_left_key):
            self.moveLeft(1)
        elif data > '\x20':
            "can't be control bytes"

            self.addInput(data)

        if not self.concealed:
            self.focusColn = self.dimension.coln + self.insert()


    def draw(self):
        if not self.concealed:
            return screen.puts(self.dimension.line, self.dimension.coln, self.data, self.length, Align.Left, fg=self.fg, bg=self.bg)
        else:
            return ''

class multilineinput(control):
    def __init__(self, routine, dimension, **kwargs):
        super(multilineinput, self).__init__(routine, dimension, **kwargs)
        self.cursor = 0
        self.inputs = [input(self.routine, Dimension(self.dimension.line + i, self.dimension.coln, self.dimension.width, 1)) for i in xrange(self.dimension.height)]
        self.display = [self.cursor, self.dimension.height] # start index, length

    def data(self):
        return '\n'.join([d.data for d in self.inputs])

    def update(self, data=''):
        self.inputs[self.cursor].update(data)
        self.redrawn = self.inputs[self.cursor].redrawn

        if isKey(data, return_key):
            # more work to do actually, need to move all data one input below
            if self.cursor == self.display[1]-1:
                self.display = [x+1 for x in self.display]
                if self.display[1] > len(self.inputs):
                    self.inputs.append(input(self.routine, Dimension(self.dimension.line + i, self.dimension.coln, self.dimension.width, 1)))
            self.cursor += 1 if self.cursor < len(self.inputs)-1 else 0

        elif isKey(data, arrow_up_key):
            self.cursor -= 1 if self.cursor > 0 else 0

        elif isKey(data, arrow_down_key):
            self.cursor += 1 if self.cursor < len(self.inputs)-1 else 0

        "adjust display"
        if self.cursor < self.display[0]:
            self.display[0] = self.cursor
        elif self.cursor > self.display[0] + self.display[1]-1:
            self.display[0] = self.cursor - self.display[1]

        if self.display[0] + self.display[1] > len(self.inputs):
            "append new inputboxes"
            self.inputs.append(input(self.routine, Dimension(self.dimension.line, self.dimension.coln, self.dimension.width, 1)))

        "reset inputs"

        self.focusLine = self.inputs[self.cursor].focusLine
        self.focusColn = self.inputs[self.cursor].focusColn + 1


    def draw(self):
        self.buffer = ''
        for text in self.inputs:
            self.buffer += text.draw()
        return self.buffer

class optioninput(control):
    def __init__(self, routine, dimension, header, textandoptions=None, **kwargs):
        super(optioninput, self).__init__(routine, dimension, **kwargs)
        "in default display a option(s) inputbox"
        self.text = header
        tmp = []
        for text, flag in textandoptions.items():
            if text != 'default':
                tmp.append(text + " (" + flag + ")")
        self.text = ", ".join(tmp)

        self.text += " [" + textandoptions['default'] + "] "

        self.label = label(self.routine, Dimension(self.dimension.line, self.dimension.coln, len(self.text.encode('big5')), 1), self.text)
        self.input = input(self.routine, Dimension(self.dimension.line, self.dimension.coln + len(self.text.encode('big5')) + 1, 2, 1), fg=ForegroundColors.White, bg=BackgroundColors.Black)

    def update(self, data=''):
        self.input.update(data)
        self.redrawn = self.input.redrawn
        self.focusLine = self.input.focusLine
        self.focusColn = self.input.focusColn

    def draw(self):
        return self.label.draw() + self.input.draw()

# arguments:
# *routine - the routine class
# *location - the location of the screen
# *title - the middle text on the header
# keywords: focusLine, focusColn, visible, minACL
class header(control):
    def __init__(self, routine, location, title, **kwargs):
        super(header, self).__init__(routine, Dimension(0, 0, routine.width, 1), **kwargs)

        # just for testing
        #self.location = u"【 主功能表 】"
        #self.title = u"批踢踢py實業坊"

        self.buffer = label(self.routine, self.dimension, title, self.dimension.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.LightBlue).buffer + label(self.routine, self.dimension, location, fg=ForegroundColors.Yellow, bg=BackgroundColors.LightBlue).buffer

# arguments:
# *routine - the routine class
# keywords: focusLine, focusColn, visible, minACL
class anykey(control):
    def __init__(self, routine, **kwargs):
        super(anykey, self).__init__(routine, Dimension(routine.height, 0, routine.width, 1), **kwargs)

        self.buffer = label(self.routine, self.dimension, u"按隨意鍵跳出", self.dimension.width, Align.Center, fg=ForegroundColors.Yellow, bg=BackgroundColors.LightBlue).buffer
        print repr(self.buffer)

# arguments:
# *routine - the routine class
# keywords: focusLine, focusColn, visible, minACL
class footer(control):
    def __init__(self, routine, **kwargs):
        super(footer, self).__init__(routine, Dimension(routine.height, 0, routine.width, 1), **kwargs)

        self.buffer = label(self.routine, self.dimension, u"批踢踢py實業坊", self.dimension.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.LightBlue).buffer + label(self.routine, self.dimension, u"【 主功能表 】", fg=ForegroundColors.Yellow, bg=BackgroundColors.LightBlue).buffer

        '''
        self.title = ''
        self.time = ''
        self.number = ''
        time = self.routine.getTime()
        constellation = "星座"
        online = "線上" + str(self.routine.getOnlineCount()) + "人"
        id = "我是" + self.routine.id
        self.routine.buffer.format_put(screen.height, 0, time, len(time),
                                 True, Colors.Cyan, Colors.Blue, Align.Center)
        self.routine.buffer.format_put_on_cursor(constellation, len(constellation),
                                 True, Colors.White, Colors.Magenta, Align.Center)
        self.routine.buffer.format_put_on_cursor(online, len(online) + 10,
                                 True, Colors.Cyan, Colors.Blue)
        self.routine.buffer.format_put_on_cursor(id, len(id) + 20,
                                 True, Colors.Cyan, Colors.Blue)
        '''


# arguments:
# *routine - the routine class
# *dimension - a Dimension object
class login(screenlet):
    def __init__(self, routine, dimension):
        super(login, self).__init__(routine, dimension)
        self.id = ''
        self.pw = ''

        title = u'=Welcome to BBS='
        warning = u'帳號或密碼有錯誤，請重新輸入。'
        lenwarning = len(warning.encode('big5'))
        enterid = u'請輸入帳號，或以 guest 參觀，或以 new 註冊： '
        lenenterid = len(enterid.encode('big5'))
        enterpw = u'請輸入密碼：'
        lenenterpw = len(enterpw.encode('big5'))

        #artwork = art(self.routine, 0, 0, self.width, self.height, '../../res/Welcome_birth')

        self.artwork = label(self.routine, Dimension(self.dimension.height / 2, 0, self.dimension.width, self.dimension.height), title, self.dimension.width, Align.Center, fg=ForegroundColors.White, bg=BackgroundColors.White)
        self.idLabel = label(self.routine, Dimension(self.dimension.height / 2 + 5, 0, lenenterid, 1), enterid)
        self.idInput = input(self.routine, Dimension(self.dimension.height / 2 + 5, lenenterid+1, 20, 1))

        self.pwLabel = label(self.routine, Dimension(self.dimension.height / 2 + 5, 0, lenenterpw, 1), enterpw, visible=False)
        self.pwInput = input(self.routine, Dimension(self.dimension.height / 2 + 5, lenenterpw+1, 20, 1), concealed=True, visible=False)
        self.warningLabel = label(self.routine, Dimension(self.dimension.height / 2 + 6, 0, lenwarning, 1), warning, visible=False)

        self.add(self.idLabel)
        self.add(self.idInput)
        self.add(self.pwLabel)
        self.add(self.pwInput)
        self.add(self.artwork)
        self.add(self.warningLabel)

        self.setFocusedControl(self.idInput)

    def registrationProcedures(self):
        self.routine.stack.pop()
        self.routine.stack.push(registration(self.routine, self.dimension))

    def loginProcedures(self):
        self.routine.id = self.id
        self.routine.createSession()
        self.routine.stack.pop()
        self.routine.stack.push(welcome(self.routine, self.dimension))

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
                if self.routine.userLookup(self.id, self.pw):
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
    def __init__(self, routine, dimension):
        super(welcome, self).__init__(routine, dimension)

        self.anykey = anykey(self.routine)

        self.add(self.anykey)


    def handleData(self, data=''):
        if len(data) > 0:
            self.routine.stack.pop()
            self.routine.stack.push(topMenu(self.routine, self.dimension))
            return clr_scr

        return normal

class topMenu(screenlet):
    def __init__(self, routine, dimension):
        super(topMenu, self).__init__(routine, dimension)

        self.items = [u"(A)nnouncement",
                      u"(B)oards",
                      u"(C)hatroom",
                      u"(G)ames",
                      u"(S)ettings",
                      u"(Q)uit"]
        self.selectionMenu = selectionMenu(self.routine, Dimension(4, 20, 45, self.dimension.height - 2), self.items)
        self.header = header(self.routine, u"【主功能表】", u"批踢踢py實業坊")
        self.footer = footer(self.routine)

        self.add(self.header)
        self.add(self.footer)
        self.add(self.selectionMenu)

    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            pass
        elif isKey(data, arrow_right_key) or isKey(data, return_key):
            self.selectionMenu.redraw()
            if self.selectionMenu.index() == 0: # Announcement
                self.routine.stack.push(announce(self.routine, self.dimension))
            elif self.selectionMenu.index() == 1: # Boards
                self.routine.stack.push(boardlist(self.routine, self.dimension, "/boards"))
            elif self.selectionMenu.index() == 2: # Chatroom
                self.routine.stack.push(notfinished(self.routine, self.dimension))
            elif self.selectionMenu.index() == 3: # Games
                self.routine.stack.push(notfinished(self.routine, self.dimension))
            elif self.selectionMenu.index() == 4: # Settings
                self.routine.stack.push(notfinished(self.routine, self.dimension))
            else: # Quit
                # double check with input textbox

                # confirm
                self.routine.stack.push(quit(self.routine, self.dimension))
            return clr_scr

        return normal


class quit(screenlet):
    def __init__(self, routine, dimension):
        super(quit, self).__init__(routine, dimension)
        self.msg = u'Bye bye'

        self.add(footer(self.routine))
        self.add(label(self.routine, Dimension(self.dimension.height / 2, 0, len(self.msg.encode('big5')), 1), self.msg))

    def handleData(self, data=''):
        if len(data) > 0:
            self.routine.disconnect()
            return clr_scr

        return normal

class notfinished(screenlet):
    def __init__(self, routine, dimension):
        super(notfinished, self).__init__(routine, dimension)

        self.msg = u'對不起，請稍後再試！'

        self.add(footer(self.routine))
        self.add(label(self.routine, Dimension(self.dimension.height / 2, 0, len(self.msg.encode('big5')), 1), self.msg))


    def handleData(self, data=''):
        if len(data) > 0:
            self.routine.stack.pop()
            return clr_scr

        return normal

class createBoard(screenlet):
    def __init__(self, routine, dimension, path):
        super(createBoard, self).__init__(routine, dimension)
        self.path = path
        self.title = ''

        warning = u'標題格式有錯誤，請重新輸入。'
        enterid = u'請輸入看板標題： '

        self.titlelabel = label(self.routine, Dimension(self.dimension.height / 2 + 5, 0, len(enterid.encode('big5')), 1), enterid)
        self.titleinput = input(self.routine, Dimension(self.dimension.height / 2 + 5, len(enterid.encode('big5'))+1, 20, 1))

        self.warninglabel = label(self.routine, Dimension(self.dimension.height / 2 + 6, 0, len(warning.encode('big5')), 1), warning, visible=False)

        self.add(self.titlelabel)
        self.add(self.titleinput)
        self.add(self.warninglabel)

        self.setFocusedControl(self.titleinput)

    def handleData(self, data=''):
        self.title = self.titleinput.data
        if isKey(data, tab_key):
            pass # implement custom cycle
        if isKey(data, return_key):
            if self.routine.addBoard(self.path, self.title):
                print "added board successfully"
                self.routine.stack.pop() #destroy it
                self.routine.stack.push(boardlist(self.routine, self.dimension, self.path))
                return clr_scr
            else:
                self.warninglabel.setVisibility(True)
        return normal

class createThread(screenlet):
    def __init__(self, routine, dimension, path):
        super(createThread, self).__init__(routine, dimension)
        self.path = path
        self.title = ''
        self.content = ''

        warning = u'標題格式有錯誤，請重新輸入。'
        enterid = u'請輸入文章標題： '

        self.titlelabel = label(self.routine, Dimension(3, 0, len(enterid.encode('big5')), 1), enterid)
        self.titleinput = input(self.routine, Dimension(3, len(enterid.encode('big5'))+1, 20, 1))

        self.warninglabel = label(self.routine, Dimension(4, 0, len(warning.encode('big5')), 1), warning, visible=False)

        # need a control for multi-line input
        self.contentinput = multilineinput(self.routine, Dimension(6, 0, self.dimension.width, 5))

        # need a control for confirmation
        self.confirmationinput = optioninput(self.routine, Dimension(self.dimension.height - 3, 0, self.dimension.width, 1), u'請確認', {u'發送' : 'Y', u'繼續編輯' : 'N', 'default' : 'N'})

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
            if self.confirmationinput.focused and self.confirmationinput.input.data == 'Y':
                if self.routine.addThread(self.path + '/' + self.title, self.title, self.content):
                    print "added thread successfully"
                    self.routine.stack.pop() #destroy it
                    self.routine.stack.push(threadlist(self.routine, self.dimension, self.path))
                    return clr_scr
            else:
                self.setFocusedControl(self.contentinput)

        return normal


class announce(screenlet):
    def __init__(self, routine, dimension):
        super(announce, self).__init__(routine, dimension)

        self.announcements = scrollableMenu(self.routine, Dimension(4, 0, self.dimension.width, self.dimension.height-2), self.routine.loadAnnouncement())
        self.header = header(self.routine, u"【公佈欄】", u"批踢踢py實業坊")
        self.footer = footer(self.routine)

        self.add(self.announcements)
        self.add(self.header)
        self.add(self.footer)

    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            self.routine.stack.pop()
            return clr_scr
        return normal

class boardlist(screenlet):
    def __init__(self, routine, dimension, cwd):
        super(boardlist, self).__init__(routine, dimension)

        self.cwd = cwd
        self.boards = selectionMenu(self.routine, Dimension(3, 0, self.dimension.width, self.dimension.height), self.routine.loadBoards(self.cwd))


        self.administration = label(self.routine, Dimension(2, 0, self.dimension.width, 1),
                "Key C-x creates a board here", self.dimension.width, Align.Left)
        self.header = header(self.routine, u"【看板列表】", u"批踢踢py實業坊")
        self.footer = footer(self.routine)

        self.add(self.administration)
        self.add(self.boards)

        self.add(self.header)
        self.add(self.footer)

    def handleData(self, data=''):
        if isKey(data, ctrl_x):
            self.routine.stack.pop() # destroy it first
            self.routine.stack.push(createBoard(self.routine, self.dimension, self.cwd))
            return clr_scr
        elif isKey(data, arrow_left_key):
            self.routine.stack.pop()
            return clr_scr
        elif isKey(data, arrow_right_key):
            self.boards.redraw()
            self.routine.stack.push(threadlist(self.routine, self.dimension, self.cwd + '/' + self.boards.menu[self.boards.index()]))
            return clr_scr
        return normal

class threadlist(screenlet):
    def __init__(self, routine, dimension, cwd):
        super(threadlist, self).__init__(routine, dimension)

        self.cwd = cwd
        self.threads = selectionMenu(self.routine, Dimension(3, 0, self.dimension.width, self.dimension.height), self.routine.loadThreads(self.cwd))

        self.administration = label(self.routine, Dimension(2, 0, self.dimension.width, 1), "Key C-x creates a thread", self.dimension.width, Align.Left)

        self.header = header(self.routine, u"【版主：】", u"批踢踢py實業坊")
        self.footer = footer(self.routine)

        self.add(self.administration)
        self.add(self.threads)

        self.add(self.header)
        self.add(self.footer)

    def handleData(self, data=''):
        if isKey(data, ctrl_x):
            self.routine.stack.pop() #destroy it first
            self.routine.stack.push(createThread(self.routine, self.dimension, self.cwd))
            return clr_scr
        elif isKey(data, arrow_left_key):
            self.routine.stack.pop()
            return clr_scr
        elif isKey(data, arrow_right_key):
            if len(self.threads.menu) > 0:
                self.threads.redraw()
                self.routine.stack.push(threadViewer(self.routine, self.dimension, self.cwd + '/' + self.threads.menu[self.threads.index()]))
                return clr_scr
        return normal

class threadViewer(screenlet):
    def __init__(self, routine, dimension, cwd):
        super(threadViewer, self).__init__(routine, dimension)

        self.cwd = cwd
        self.content = scrollableMenu(self.routine, Dimension(2, 0, self.dimension.width, self.dimension.height - 3), self.routine.loadThread(self.cwd).split("\n"))

        self.add(self.content)

    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            self.routine.stack.pop()
            return clr_scr
        return normal

class editor(screenlet):
    def __init__(self, routine, dimension, content):
        super(editor, self).__init__(routine, dimension)

        self.content = content

        self.footer = footer()
    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            self.routine.stack.pop()
            return clr_scr
        return normal

class registration(screenlet):
    def __init__(self, routine, dimension):
        super(registration, self).__init__(routine, dimension)
    def handleData(self, data=''):
        if isKey(data, arrow_left_key):
            self.routine.stack.pop()
            return clr_scr
        return normal


def evalString(string):
    return globals()[string]
