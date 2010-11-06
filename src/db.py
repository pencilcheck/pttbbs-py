# -*- encoding: UTF8 -*-

## Ptt BBS python rewrite
##
## This is the model of MVC architecture
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

import sqlite3

# make singleton
class DB:
   
    # tables: users, posts     
    # fields for users: IP, login time, login duration, ACL, scr, mood, idle, sex, friends, banlist, birthday date, contact info (like phone number, address)    
    # fields for posts: post time, author, board, title, type, history, attach (給推用的)
        
    def __init__(self, path):
        # create db if not exist already
        
        self.DB_USERS_PATH = path
        self.conn = sqlite3.connect(self.DB_USERS_PATH)
    
    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.conn.close()
    
    def getCursor(self):
        return self.conn.cursor()    