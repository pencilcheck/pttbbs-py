# -*- encoding: UTF-8 -*-

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
    if row == coln == -1:
        return hide
    return '\033[' + str(row) + ';' + str(coln) + 'H'

def move_cursor_up(N):
    return '\033[' + str(N) + 'A'

def move_cursor_down(N):
    return '\033[' + str(N) + 'B'

def move_cursor_right(N):
    return '\033[' + str(N) + 'C'

def move_cursor_left(N):
    return '\033[' + str(N) + 'D'

def puts(row, coln, msg, length=None, align=Align.Left, **kwargs):
    ifg = kwargs['fg'] if 'fg' in kwargs else ForegroundColors.White
    ibg = kwargs['bg'] if 'bg' in kwargs else BackgroundColors.Black

    return move_cursor(row, coln) + format(msg, length, align, fg=ifg, bg=ibg)


def fillBlank(dimension):
    instructions = move_cursor(dimension.line, dimension.coln)
    for i in xrange(dimension.height):
        instructions += " "*dimension.width + move_cursor_down(1) + move_cursor_left(dimension.width)
    return instructions

def attributes(args):
    return ''.join(['\033[' + x + 'm' for x in args])

def padding(msg, length, align):
    if not length:
        return msg

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

def format(msg, length=None, align=Align.Left, **kwargs):
    args = [values for values in kwargs.values()]
    print "format args:", args

    return attributes(args) + padding(msg, length, align) + (reset if len(args) > 0 else '')
