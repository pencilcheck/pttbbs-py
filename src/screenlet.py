# -*- encoding: UTF8 -*-

## Ptt BBS python rewrite
##
## This is the view of MVC architecture extended from term
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

from term import Term
from term import Colors
from term import Align

class screenlet:
    def __init__(self, t):
        self.billboard = []
        self.header = []
        self.content = []
        self.footer = []
        self.term = t

    def update(self):
        # turn off line buffer mode
        self.term.setLineMode(False)


class login(screenlet):
    def update(self):
        inputLen = 10
    
        print inputLen
        
        #Form
        id     =        "User ID:\n"
        passwd =        "Password:\n"
                
        # format takes argument: light, foreground, background, msg, alignment
        self.term.clr_scr()
        self.term.put(20, 10, id)
        self.term.format_put(0, 0, passwd, True, Colors.White, Colors.Cyan, Align.Center)
        
        #self.term.form(False, Colors.White, Colors.Cyan, form, inputLen, Align.Center)
        #self.term.move_cursor_up(len(rows))
        #self.term.move_cursor_right(rows[0].find(':') + 1 - len(term.escape_sequence(False, Colors.White, Colors.Cyan)))