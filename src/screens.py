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

import colors
from colors import Colors
from colors import Align

def loginScr(protocol):
    inputLen = 5
    
    #Form
    form =  "User ID:\n" + \
            "Password:"
    # format takes argument: light, foreground, background, msg, alignment
    colors.clr_and_print_to_term(protocol, colors.format(True, Colors.White, Colors.Cyan, 
                                      "Welcome to ptt BBS python server!\n" +
                                      "目前有" + str(protocol.factory.connections) + "位在線上.\n" +
                                      "test" * 100,
                                      Align.Center))
    colors.print_to_term(protocol, "您的IP: " + protocol.transport.getHost().host)
    colors.print_to_term(protocol, colors.form(True, Colors.White, Colors.Cyan, 
                                      form,
                                      inputLen,
                                      Align.Center))
    protocol.transport.write(colors.move_cursor_up(form.count(':')))
    protocol.transport.write(colors.move_cursor_right(form.find(':')))
    protocol.setLineMode(False)
    
    
def header(protocol):
    # header of the screen
    return

def footer(protocol):
    # footer of the screen
    return