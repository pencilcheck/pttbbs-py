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

import os
import sqlite3

DB_PATH = 'users.db'

# make singleton
class DB:
   
    # tables: users, posts     
    # fields for users: IP, login time, login duration, ACL, scr, mood, idle, sex, friends, banlist, birthday date, contact info (like phone number, address)    
    # fields for posts: post time, author, board, title, type, history, attach (給推用的)
        
    def __init__(self):
        self.exist = os.path.exists(DB_PATH)
        
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        if not self.exist:
            self.create()
            self.commit()
    
    def create(self):
    
        users =      """CREATE TABLE Users
                        (
                         UId TEXT UNIQUE NOT NULL,
                         PW TEXT,
                         IPs TEXT,
                         ACL INTEGER NOT NULL,
                         Location TEXT,
                         Avatar TEXT,
                         Mood TEXT,
                         IdleTime TEXT,    
                         LoginTime TEXT,
                         LoginDuration TEXT,
                         Sex TEXT,
                         Birthday TEXT,
                         LastName TEXT,
                         FirstName TEXT,
                         HomePhone TEXT,
                         WorkPhone TEXT,
                         Address TEXT,
                         City TEXT
                        )"""
        relations =  """CREATE TABLE Relations
                        (
                         UId TEXT NOT NULL,
                         FId TEXT,
                         Status TEXT NOT NULL
                        )"""
        
        guest =      """INSERT INTO
                        users(
                                UId,
                                ACL
                        ) 
                        VALUES (
                                \"guest\",
                                0                         
                        )"""
        
        self.cursor.execute(users)
        self.cursor.execute(relations)
        self.cursor.execute(guest)
    
    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.cursor.close()    
    
instance = DB()