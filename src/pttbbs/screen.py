# -*- encoding: UTF-8 -*-

## Ptt BBS python rewrite
##
## This is the view of MVC architecture but shouldn't be used directly
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

## Terminal Colors
##     This loops though all the font colors on each background for a linux
##     terminal. Tested on Bash 3.2.25(1). These special escape sequences can
##     be used with any language for a linux terminal. See my bash and perl
##     code for other examples of the same output.
##     "\E[" begins the escape sequence, you can also use "\033" or "\x1B".
##     You can use a semicolon to separated the numbers
##     (eg 1;30;46 = Bold font (making it lighter in color)
##               FG as Black (bolding it makes it a dark gray)
##               BG as Cyan )
##     Note: The foreground and background numbers do not overlap so order
##           does not matter, for formatting reasons I will have it always
##           be Text-format / Foreground / Background.
## 
##     "m" terminates the escape sequence, the text begins immediately after.
##
##     FG hew bit: 0/1 (dark/light)
##
##     Foreground Colors: 3x
##     Background Colors: 4x
##
##     x representing a different color
##         0 = Black   1 = Red
##         2 = Green   3 = Yellow
##         4 = Blue    5 = Magenta
##         6 = Cyan    7 = White
##
##     Black       0;30     Dark Gray     1;30
##     Blue        0;34     Light Blue    1;34
##     Green       0;32     Light Green   1;32
##     Cyan        0;36     Light Cyan    1;36
##     Red         0;31     Light Red     1;31
##     Purple      0;35     Light Purple  1;35
##     Brown       0;33     Yellow        1;33
##     Light Gray  0;37     White         1;37
##
##     ASCII        '\x1f' < x < '\x7f'
##     BIG5         '\xa1' < x < '\xf9'
##     UTF8         '\x4e' < x < '\x9f'


import struct

# For enumeration, using keyword argument (google it!)
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    # meta classes magic!!
    return type('Enum', (), enums)

# color handles
ForegroundColors = enum(Black     =   '0;30', DarkGray    =   '1;30',
                        Blue      =   '0;34', LightBlue   =   '1;34',
                        Green     =   '0;32', LightGreen  =   '1;32',
                        Cyan      =   '0;36', LightCyan   =   '1;36',
                        Red       =   '0;31', LightRed    =   '1;31',
                        Purple    =   '0;35', LightPurple =   '1;35',
                        Brown     =   '0;33', Yellow      =   '1;33',
                        LightGray =   '0;37', White       =   '1;37')
BackgroundColors = enum(Black     =   '0;40', DarkGray    =   '1;40',
                        Blue      =   '0;44', LightBlue   =   '1;44',
                        Green     =   '0;42', LightGreen  =   '1;42',
                        Cyan      =   '0;46', LightCyan   =   '1;46',
                        Red       =   '0;41', LightRed    =   '1;41',
                        Purple    =   '0;45', LightPurple =   '1;45',
                        Brown     =   '0;43', Yellow      =   '1;43',
                        LightGray =   '0;47', White       =   '1;47')

Align = enum(Left='left', Center='center', Right='right')


commands = {
'NULL':chr(0),      # No operation.
'BEL':chr(7),       # Produces an audible or visible signal (which does NOT move the print head).
'BS':chr(8),        # Moves the print head one character position towards the left margin.
'HT':chr(9),        # Moves the printer to the next horizontal tab stop.
                    # It remains unspecified how either party determines or
                    # establishes where such tab stops are located.
'LF':chr(10),       # Moves the printer to the next print line,
                    # keeping the same horizontal position.
'VT':chr(11),       # Moves the printer to the next vertical tab stop.
                    # It remains unspecified how either party determines or
                    # establishes where such tab stops are located.
'FF':chr(12),       # Moves the printer to the top of the next page,
                    # keeping the same horizontal position.
'CR':chr(13),       # Moves the printer to the left margin of the current line.
'ECHO':chr(1),      # User-to-Server:  Asks the server to send Echos of the transmitted data.
'SGA':chr(3),       # Suppress Go Ahead.
                    # Go Ahead is silly and most modern servers should suppress it.
'NAWS':chr(31),     # Negotiate About Window Size.
                    # Indicate that information about the size of the terminal can be communicated.
'LINEMODE':chr(34), # Allow line buffering to be negotiated about.
'SE':chr(240),      # End of subnegotiation parameters.
'NOP':chr(241),     # No operation.
'DM':chr(242),      # "Data Mark": The data stream portion of a Synch.
                    # This should always be accompanied by a TCP Urgent notification.
'BRK':chr(243),     # NVT character Break.
'IP':chr(244),      # The function Interrupt Process.
'AO':chr(245),      # The function Abort Output
'AYT':chr(246),     # The function Are You There.
'EC':chr(247),      # The function Erase Character.
'EL':chr(248),      # The function Erase Line
'GA':chr(249),      # The Go Ahead signal.
'SB':chr(250),      # Indicates that what follows is subnegotiation of the indicated option.
'WILL':chr(251),    # Indicates the desire to begin performing,
                    # or confirmation that you are now performing, the indicated option.
'WONT':chr(252),    # Indicates the refusal to perform, or continue performing,
                    # the indicated option.
'DO':chr(253),      # Indicates the request that the other party perform,
                    # or confirmation that you are expecting the other party to perform,
                    # the indicated option.
'DONT':chr(254),    # Indicates the demand that the other party stop performing,
                    # or confirmation that you are no longer expecting the other party to perform,
                    # the indicated option.
'IAC':chr(255)      # Data Byte 255.  Introduces a telnet command.
}

'''
commands = {
    chr(0):'NULL',      # No operation.
    chr(7):'BEL',       # Produces an audible or visible signal (which does NOT move the print head).
    chr(8):'BS',        # Moves the print head one character position towards the left margin.
    chr(9):'HT',        # Moves the printer to the next horizontal tab stop. It remains unspecified how either party determines or
                        # establishes where such tab stops are located.
    chr(10):'LF',       # Moves the printer to the next print line, keeping the same horizontal position.
    chr(11):'VT',       # Moves the printer to the next vertical tab stop.  It remains unspecified how either party determines or
                        # establishes where such tab stops are located.
    chr(12):'FF',       # Moves the printer to the top of the next page, keeping the same horizontal position.
    chr(13):'CR',       # Moves the printer to the left margin of the current line.
    chr(1):'ECHO',      # User-to-Server:  Asks the server to send Echos of the transmitted data.
    chr(3):'SGA',       # Suppress Go Ahead.  Go Ahead is silly and most modern servers should suppress it.
    chr(31):'NAWS',     # Negotiate About Window Size.  Indicate that information about the size of the terminal can be communicated.
    chr(34):'LINEMODE', # Allow line buffering to be negotiated about.
    chr(240):'SE',      # End of subnegotiation parameters.
    chr(241):'NOP',     # No operation.
    chr(242):'DM',      # "Data Mark": The data stream portion of a Synch.  This should always be accompanied by a TCP Urgent notification.
    chr(243):'BRK',     # NVT character Break.
    chr(244):'IP',      # The function Interrupt Process.
    chr(245):'AO',      # The function Abort Output
    chr(246):'AYT',     # The function Are You There.
    chr(247):'EC',      # The function Erase Character.
    chr(248):'EL',      # The function Erase Line
    chr(249):'GA',      # The Go Ahead signal.
    chr(250):'SB',      # Indicates that what follows is subnegotiation of the indicated option.
    chr(251):'WILL',    # Indicates the desire to begin performing, or confirmation that you are now performing, the indicated option.
    chr(252):'WONT',    # Indicates the refusal to perform, or continue performing, the indicated option.
    chr(253):'DO',      # Indicates the request that the other party perform, or confirmation that you are expecting the other party to perform, the indicated option.
    chr(254):'DONT',    # Indicates the demand that the other party stop performing, or confirmation that you are no longer expecting the other party to perform, the indicated option.
    chr(255):'IAC'      # Data Byte 255.  Introduces a telnet command.
}
'''

clr = '\033[2J' # clear the screen
eratocol = '\033[K' # erase to the end of line
underscore = '\033[4m'
inverse = '\033[7m'
concealed = '\033[8m' # for password, will not echo
blink = '\033[5m'; # blink
hide = '\033[?25l' # hide cursor
show = '\033[?25h' # show cursor
reset = '\x1b[0m' # reset color

#'\[\033[44m\]\[\033[1;31m\]'

def move_cursor(row, coln):
    return '\033[' + str(row) + ';' + str(coln) + 'H'

def move_cursor_up(N):
    return '\033[' + str(N) + 'A'

def move_cursor_down(N):
    return '\033[' + str(N) + 'B'

def move_cursor_right(N):
    return '\033[' + str(N) + 'C'

def move_cursor_left(N):
    return '\033[' + str(N) + 'D'

# arguments for puts:
# msg
# row, coln, msg
# or above two with keyword arguments: fg, bg, concealed
def puts(*args, **kwargs):
    print "puts", args, kwargs
    instructions = ""
    if len(args) == 1:
        if 'fg' in kwargs and 'bg' in kwargs:
            if 'concealed' in kwargs:
                instructions = format(args[0], fg=kwargs['fg'], bg=kwargs['bg'], concealed=kwargs['concealed'])
            else:
                instructions = format(args[0], fg=kwargs['fg'], bg=kwargs['bg'])
        else:
            if 'concealed' in kwargs:
                instructions = format(args[0], concealed=kwargs['concealed'])
            else:
                instructions = args[0]

    if len(args) == 3:
        if 'fg' in kwargs and 'bg' in kwargs:
            if 'concealed' in kwargs:
                instructions = move_cursor(args[0], args[1]) + format(args[2], fg=kwargs['fg'], bg=kwargs['bg'], concealed=kwargs['concealed'])
            else:
                instructions = move_cursor(args[0], args[1]) + format(args[2], fg=kwargs['fg'], bg=kwargs['bg'])
        else:
            if 'concealed' in kwargs:
                instructions = move_cursor(args[0], args[1]) + format(args[2], concealed=kwargs['concealed'])
            else:
                instructions = move_cursor(args[0], args[1]) + args[2]
    return instructions

# arguments for format_puts:
# msg, length, align
# row, coln, msg, length, align
# or above two with keyword arguments: fg, bg, concealed
def format_puts(*args, **kwargs):
    instructions = ""
    if len(args) == 3:
        if 'fg' in kwargs and 'bg' in kwargs:
            if 'concealed' in kwargs and kwargs['concealed']:
                instructions = format(args[0], args[1], args[2], fg=kwargs['fg'], bg=kwargs['bg'], concealed=kwargs['concealed'])
            else:
                instructions = format(args[0], args[1], args[2], fg=kwargs['fg'], bg=kwargs['bg'])
        
        if len(kwargs) == 0:
            instructions = format(args[0], args[1], args[2])
    
    if len(args) == 5:
        if 'fg' in kwargs and 'bg' in kwargs:
            if 'concealed' in kwargs and kwargs['concealed']:
                instructions = move_cursor(args[0], args[1]) + format(args[2], args[3], args[4], fg=kwargs['fg'], bg=kwargs['bg'], concealed=kwargs['concealed'])
            else:
                instructions = move_cursor(args[0], args[1]) + format(args[2], args[3], args[4], fg=kwargs['fg'], bg=kwargs['bg'])
        
        if len(kwargs) == 0:
            instructions = move_cursor(args[0], args[1]) + format(args[2], args[3], args[4])
    
    return instructions

def fillBlank(dimension):
    instructions = move_cursor(dimension.line, dimension.coln)
    for i in xrange(dimension.height):
        instructions += " "*dimension.width + move_cursor_down(1) + move_cursor_left(dimension.width)
    return instructions

# arguments for attributes:
# any array of colors
def attributes(*args):
    return ''.join(['\033[' + x + 'm' for x in args])

def adjust(msg, length, align):
    realen = len(msg.encode('big5'))
    if length < realen:
        return msg[:length]
    
    remains = length - realen

    if align == Align.Left or align == None:
        left = ''
        right = ' '*remains
    if align == Align.Center:
        left = ' '*(remains / 2)
        right = left
    elif align == Align.Right:
        left = ' '*remains
        right = ''

    return left + msg + right

# arguments for format:
# msg
# msg, length, align
# or above with keyword arguments: fg, bg, concealed
def format(*args, **kwargs):
    if len(args) == 1:
        if 'fg' in kwargs and 'bg' in kwargs:
            if 'concealed' in kwargs and kwargs['concealed']:
                return attributes(kwargs['fg'], kwargs['bg'], concealed) + reset
            else:
                return attributes(kwargs['fg'], kwargs['bg']) + args[0] + reset

        if len(kwargs) == 0:
            return args[0]

    if len(args) == 3:
        if 'fg' in kwargs and 'bg' in kwargs:
            if 'concealed' in kwargs and kwargs['concealed']:
                return attributes(kwargs['fg'], kwargs['bg']) + adjust('', args[1], args[2]) + reset
            else:
                return attributes(kwargs['fg'], kwargs['bg']) + adjust(args[0], args[1], args[2]) + reset

        if len(kwargs) == 0:
            return adjust(args[0], args[1], args[2])




"""
class Tools:
    
    def __init__(self, sock):
        self.temp = []
        
        self.echo = True
        
        self.cursor_line = 0
        self.cursor_coln = 0
        
        self.ready = False    
        
        self.protocol = sock
    
    def put_on_cursor(self, msg):
        self.protocol.send(str(msg))
        self.cursor_coln = self.cursor_coln + len(msg)
    
    def put(self, row, coln, msg):
        self.move_cursor(row, coln)
        self.put_on_cursor(msg)
    
    def format_put_on_cursor(self, msg, maxLen, light=None, fg=None, bg=None, align=Align.Left, highlight=False):
        if highlight:
            light = True
            fg = Colors.Black
            bg = Colors.Yellow
            # maybe add an arrow on the right pointing to the right
        self.put_on_cursor(self.format(light, fg, bg, msg, maxLen, align))
        
    def format_put(self, row, coln, msg, maxLen, light=None, fg=None, bg=None, align=Align.Left, highlight=False):
        if highlight:
            light = True
            fg = Colors.Black
            bg = Colors.Yellow
            # maybe add an arrow on the right pointing to the right
        self.put(row, coln, self.format(light, fg, bg, msg, maxLen, align))

    def ready_for_input(self, maxLen, line=None, coln=None, ech=True):
        if not self.ready:
            self.input = ''
            self.limit = maxLen
            self.ready = True
            self.insert = 0
            self.input_line = line if line != None else self.input_line
            self.input_coln = coln if coln != None else self.input_coln
            self.echo = ech
    
    
    # print input will erase line from the position of the input box to the end of line first then print input
    def print_input(self, input_light=False, input_fg=Colors.Black, input_bg=Colors.White):
        if self.ready:
            self.put(self.input_line, self.input_coln, eratocol)
            if self.echo:
                self.format_put(self.input_line, self.input_coln, self.input, self.limit, input_light, input_fg, input_bg)
                self.move_cursor(self.input_line, self.input_coln + self.insert)
            else:
                self.format_put(self.input_line, self.input_coln, '*'*len(self.input), self.limit, False, Colors.Black, Colors.Black)
                self.move_cursor(self.input_line, self.input_coln)
    
    def add_to_input(self, data):
        if self.ready:
            if len(self.input) < self.limit-1: # minus 1 for the cursor
                self.input = self.input[:self.insert] + data + self.input[self.insert:]
                
                # watch out for double byte
                self.insert = self.insert + len(data)
    
    def move_left_input(self, n=1):
        if self.ready:
            if self.insert - n >= 0:
                self.insert = self.insert - n
    
    def move_right_input(self, n=1):
        if self.ready:
            if self.insert + n < self.limit and self.insert < len(self.input):
                self.insert = self.insert + n
    
    def backspace_input(self):
        if self.ready:
            if self.insert > 0:
                # check for double byte character
                self.input = self.input[:self.insert-1] + self.input[self.insert:]
                self.move_left_input(1)
                if len(self.input) > 0:
                    if self.input[-1] >= '\xa1' and self.input[-1] <= '\xf9': # BIG5
                        self.input = self.input[:self.insert-1] + self.input[self.insert:]
                        self.move_left_input(1)
                
                # not used
                if len(self.id) == 1:
                    if self.id[-1] > '\x1f' and self.id[-1] < '\x7f':
                        self.id = self.id[:-1]
                
                if len(self.id) >= 2: # check for double byte character
                    if self.id[-2] > '\xa1' and self.id[-2] < '\xf9': # BIG5
                        print '1'
                        self.id = self.id[:-2]
                    elif self.id[-2] > '\x4e' and self.id[-2] < '\x9f': # Utf-8
                        print '2', repr(self.id[-2])
                        self.id = self.id[:-2]
                    elif self.id[-1] > '\x1f' and self.id[-1] < '\x7f':
                        self.id = self.id[:-1]
                # end
                
    
    def finish_for_input(self):
        self.ready = False
    
    def hide_cursor(self):
        self.put_on_cursor(hide)
    
    def show_cursor(self):
        self.put_on_cursor(show)
    
    def move_cursor(self, row, coln):
        self.cursor_line = row
        self.cursor_coln = coln
        self.protocol.send('\033[' + str(row) + ';' + str(coln) + 'H')
    
    def move_cursor_up(self, N):
        self.cursor_line = self.cursor_line - N
        self.protocol.send('\033[' + str(N) + 'A')
    
    def move_cursor_down(self, N):
        self.cursor_line = self.cursor_line + N
        self.protocol.send('\033[' + str(N) + 'B')
    
    def move_cursor_right(self, N):
        self.cursor_coln = self.cursor_coln + N
        self.protocol.send('\033[' + str(N) + 'C')
    
    def move_cursor_left(self, N):
        self.cursor_coln = self.cursor_coln - N
        self.protocol.send('\033[' + str(N) + 'D')
    
    def clr_scr(self):
        self.protocol.send(clr)
    
    def escape_sequence(self, light, fg_color, bg_color):
        arr = []
        if light != None:
            arr.append(str(int(light)))
        if fg_color != None:
            arr.append(fg + str(fg_color))
        if bg_color != None:
            arr.append(bg + str(bg_color))
        return prefix + delim.join(arr) + end
    
    def adjust(self, align, msg, maxLen):
        if maxLen < len(msg):
            return msg
        
        #remains = width - self.cursor_coln
        remains = maxLen
        
        ret = ''
    
        if align == Align.Center:
            ret = ret + ' '*(remains / 2 - len(msg) / 2)
        elif align == Align.Right:
            ret = ret + ' '*(remains - len(msg))
            
        ret = ret + msg + ' '*(remains - len(msg) - len(ret))
        return ret
    
    # assuming len(msg) and maxLen are both < width 
    def format(self, light, fg_color, bg_color, msg, maxLen, alignment=Align.Left):
        return self.escape_sequence(light, fg_color, bg_color) + self.adjust(alignment, msg, maxLen) + color_reset
"""