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

# For enumeration, using keyword argument (google it!)
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    # meta classes magic!!
    return type('Enum', (), enums)

# color handles
Colors = enum('Black', 'Red', 'Green', 'Yellow', 'Blue', 'Magenta', 'Cyan', 'White')
Align = enum(Left='left', Center='center', Right='right')

clr = "\033[2J"
eratocol = "\033[K"
color_reset = '\x1b[0m'
blink = '\x1b[5m';

fg = '3'
bg = '4'

delim = ';'

prefix = '\x1b['
end = 'm'

class Term:
    def __call__(self):
        return self
    
    def __init__(self, pro, w=80, h=22):
        self.width = w
        self.height = h
        
        self.cursor_line = 0
        self.cursor_coln = 0
        
        self.protocol = pro

    def setLineMode(self, enable):
        self.protocol.setLineMode(enable)
    
    def put(self, row, coln, msg):
        self.protocol.transport.write(self.move_cursor(row, coln))
        self.protocol.transport.write(msg)
        
    def format_put(self, row, coln, msg, light, fg, bg, align=Align.Left):
        self.protocol.transport.write(self.move_cursor(row, coln))
        self.protocol.transport.write(self.format(light, fg, bg, msg, align))

    def move_cursor(self, row, coln):
        self.cursor_line = row
        self.cursor_coln = coln
        return '\033[' + str(row) + ';' + str(coln) + 'H'
    
    def move_cursor_up(self, N):
        self.cursor_line = self.cursor_line - N
        return '\033[' + str(N) + 'A'
    
    def move_cursor_down(self, N):
        self.cursor_line = self.cursor_line + N
        return '\033[' + str(N) + 'B'
    
    def move_cursor_right(self, N):
        self.cursor_coln = self.cursor_coln + N
        return '\033[' + str(N) + 'C'
    
    def move_cursor_left(self, N):
        self.cursor_coln = self.cursor_coln - N
        return '\033[' + str(N) + 'D'
    
    def clr_scr(self):
        self.protocol.transport.write(clr)
    
    def escape_sequence(self, light, fg_color, bg_color):
        return prefix + delim.join([str(int(light)), fg + str(fg_color), bg + str(bg_color)]) + end
    
    def adjust(self, align, msg):
        if msg == '':
            return ''
        
        remains = self.width - self.cursor_coln
        
        ret = ' '*(self.cursor_coln)
        if len(msg) > remains:
            segs = [msg[i:i+min(remains, len(msg)-i)] for i in xrange(0, len(msg), remains)]
            if len(msg) % remains == 0:
                ret = '\n'.join(segs)
                msg = ''
            else:
                msg = segs[-1]
                ret = '\n'.join(segs[:-1]) 
    
        if align == Align.Left:
            ret = ret + ''
        elif align == Align.Center:
            ret = ret + ' '*(remains / 2 - len(msg) / 2)
        elif align == Align.Right:
            ret = ret + ' '*(remains - len(msg))
            
        for i in xrange(self.width - len(ret)):
            if i < len(msg):
                ret = ret + msg[i]
            else:
                ret = ret + ' '
        return ret
    
    def format(self, light, fg_color, bg_color, msg, alignment=Align.Left):
        rows = msg.split('\n')
        print repr(rows)
        msg = '\n'.join([self.adjust(alignment, line) for line in rows])
        print msg
        return self.escape_sequence(light, fg_color, bg_color) + msg + color_reset
    
    def adjust_form(self, light, fg_color, bg_color, align, input, msg):
        ret = ' '*self.cursor_coln
        
        remains = self.width - self.cursor_coln
        
        if len(msg) + len(input) > remains:
            return 'Form too long'
    
        if align == Align.Left:
            ret = ''
        elif align == Align.Center:
            ret = ' '*(remains / 2 - len(msg) / 2 - len(input) / 2)
        elif align == Align.Right:
            ret = ' '*(remains - len(msg) - len(input))
        
            
        ret = self.escape_sequence(light, fg_color, bg_color) + ret + msg + \
                self.escape_sequence(False, Colors.White, Colors.White) + input + \
                self.escape_sequence(light, fg_color, bg_color) + ' '*(remains - len(ret) - len(msg)) + color_reset
        
        
        
        return ret
    
    
    def form(self, light, fg_color, bg_color, msg, maxLen, alignment=Align.Left):
        rows = msg.split('\n')
        input = ' '*maxLen
        rows_after = [self.adjust_form(light, fg_color, bg_color, alignment, input, line) for line in rows]
        msg = '\n'.join(rows_after) + '\n'
         
        return msg, rows_after