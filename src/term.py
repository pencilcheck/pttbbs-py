# -*- encoding: UTF8 -*-

## Ptt BBS python rewrite
##
## This is the model of MVC architecture but shouldn't be used directly
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
Colors = enum('Black', 'Red', 'Green', 'Yellow', 'Blue', 'Magenta', 'Cyan', 'White')
Align = enum(Left='left', Center='center', Right='right')




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




clr = "\033[2J" # clear the screen
eratocol = "\033[K" # erase to the end of line
color_reset = '\x1b[0m' # reset color
blink = '\x1b[5m'; # blink
hide = '\033[?25l' # hide cursor
show = '\033[?25h' # show curdasfd

fg = '3'
bg = '4'

delim = ';'

prefix = '\x1b['
end = 'm'

# easier if this is a singleton
class Term:
    
    def __init__(self, pro, w=80, h=22):
        self.temp = []
        
        self.width = w
        self.height = h
        
        self.protocol = pro
        
        self.echo = True
        
        self.cursor_line = 0
        self.cursor_coln = 0
        
        self.ready = False

    def setLineMode(self, enable):
        self.protocol.setLineMode(enable)
    
    def put_on_cursor(self, msg):
        self.protocol.transport.write(msg)
        self.cursor_coln = self.cursor_coln + len(msg)
    
    def put(self, row, coln, msg):
        self.move_cursor(row, coln)
        self.protocol.transport.write(msg)
        self.cursor_coln = self.cursor_coln + len(msg)
    
    def format_put_on_cursor(self, msg, maxLen, light, fg, bg, align=Align.Left):
        self.put_on_cursor(self.format(light, fg, bg, msg, maxLen, align))
        
    def format_put(self, row, coln, msg, maxLen, light, fg, bg, align=Align.Left):
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
                    print 'bs_inut', repr(self.input[-1])
                    if self.input[-1] >= '\xa1' and self.input[-1] <= '\xf9': # BIG5
                        self.input = self.input[:self.insert-1] + self.input[self.insert:]
                        self.move_left_input(1)
                """
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
                """
                
    
    def finish_for_input(self):
        self.ready = False
    
    def hide_cursor(self):
        self.put_on_cursor(hide)
    
    def show_cursor(self):
        self.put_on_cursor(show)
    
    def move_cursor(self, row, coln):
        self.cursor_line = row
        self.cursor_coln = coln
        self.protocol.transport.write('\033[' + str(row) + ';' + str(coln) + 'H')
    
    def move_cursor_up(self, N):
        self.cursor_line = self.cursor_line - N
        self.protocol.transport.write('\033[' + str(N) + 'A')
    
    def move_cursor_down(self, N):
        self.cursor_line = self.cursor_line + N
        self.protocol.transport.write('\033[' + str(N) + 'B')
    
    def move_cursor_right(self, N):
        self.cursor_coln = self.cursor_coln + N
        self.protocol.transport.write('\033[' + str(N) + 'C')
    
    def move_cursor_left(self, N):
        self.cursor_coln = self.cursor_coln - N
        self.protocol.transport.write('\033[' + str(N) + 'D')
    
    def clr_scr(self):
        self.protocol.transport.write(clr)
    
    def escape_sequence(self, light, fg_color, bg_color):
        return prefix + delim.join([str(int(light)), fg + str(fg_color), bg + str(bg_color)]) + end
    
    def adjust(self, align, msg, maxLen):
        if maxLen < len(msg):
            return msg
        
        #remains = self.width - self.cursor_coln
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