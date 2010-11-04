# -*- encoding: BIG5 -*-

## Ptt BBS python rewrite
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




import terminfo

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

def move_cursor(row, coln):
    return '\033[' + str(row) + str(coln) + 'H'

def move_cursor_up(N):
    return '\033[' + str(N) + 'A'

def move_cursor_down(N):
    return '\033[' + str(N) + 'B'

def move_cursor_right(N):
    return '\033[' + str(N) + 'C'

def move_cursor_left(N):
    return '\033[' + str(N) + 'D'

def adjust(align, msg):
    ret = ''
    if len(msg) > terminfo.width:
        segs = [msg[i:i+min(terminfo.width, len(msg)-i)] for i in xrange(0, len(msg), terminfo.width)]
        if len(msg) % terminfo.width == 0:
            ret = '\n'.join(segs)
            msg = ''
        else:
            msg = segs[-1]
            ret = '\n'.join(segs[:-1]) 

    if align == Align.Left:
        ret = ret + ''
    elif align == Align.Center:
        ret = ret + ' '*(terminfo.width / 2 - len(msg) / 2)
    elif align == Align.Right:
        ret = ret + ' '*(terminfo.width - len(msg))
        
    for i in xrange(terminfo.width - len(ret)):
        if i < len(msg):
            ret = ret + msg[i]
        else:
            ret = ret + ' '
    return ret

def print_to_term(protocol, msg):
    protocol.transport.write(msg + '\n')
    """
    i = 0
    while i < len(msg):
        protocol.transport.write(msg[i:i+min(len(msg)-i, terminfo.width)])
        i = i + terminfo.width
    """

def clr_and_print_to_term(protocol, msg):
    protocol.transport.write(clr)
    print_to_term(protocol, msg)

def escape_sequence(light, fg_color, bg_color):
    return prefix + delim.join([str(int(light)), fg + str(fg_color), bg + str(bg_color)]) + end

def format(light, fg_color, bg_color, msg, alignment=Align.Left):
    rows = msg.split('\n')
    msg = '\n'.join([adjust(alignment, line) for line in rows])
     
    return escape_sequence(light, fg_color, bg_color) + msg + color_reset

def adjust_form(align, input, msg):
    msg = msg + input
    ret = ''
    if len(msg) > terminfo.width:
        segs = [msg[i:i+min(terminfo.width, len(msg)-i)] for i in xrange(0, len(msg), terminfo.width)]
        if len(msg) % terminfo.width == 0:
            ret = '\n'.join(segs)
            msg = ''
        else:
            msg = segs[-1]
            ret = '\n'.join(segs[:-1]) 

    if align == Align.Left:
        ret = ret + ''
    elif align == Align.Center:
        ret = ret + ' '*((terminfo.width - len(msg)) / 2)
    elif align == Align.Right:
        ret = ret + ' '*(terminfo.width - len(msg))
        
    ret = ret + msg
    ret = ret + ' '*(terminfo.width - len(ret))
    
    return ret


def form(light, fg_color, bg_color, msg, maxLen, alignment=Align.Left):
    rows = msg.split('\n')
    lines = len(rows)
    input = color_reset + escape_sequence(light, Colors.White, Colors.Black) + ' '*maxLen + color_reset + escape_sequence(light, fg_color, bg_color)
    msg = '\n'.join([adjust_form(alignment, input, line) for line in rows])
     
    return escape_sequence(light, fg_color, bg_color) + msg + color_reset