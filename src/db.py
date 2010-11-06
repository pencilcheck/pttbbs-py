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
        if not self.exist:
            self.create()
    
    def create(self):
        c = self.conn.cursor()
        
        users =      """CREATE TABLE Users
                        (
                         UId char(255) NOT NULL PRIMARY KEY IDENTITY,
                         IPs char(15) NOT NULL,
                         ACL int NOT NULL,
                         Location varchar(255) NOT NULL,
                         Mood varchar(255),
                         IdleTime datetime2,    
                         LoginTime date NOT NULL,
                         LoginDuration datetime2,
                         Sex char(1),
                         Birthday,
                         LastName varchar(255) NOT NULL,
                         FirstName varchar(255),
                         HomePhone varchar(255),
                         WorkPhone varchar(255),
                         Address varchar(255),
                         City varchar(255)
                        )"""
        relations =  """CREATE TABLE Relations
                        (
                         Id char(255) NOT NULL PRIMARY KEY IDENTITY,
                         UId char(255) NOT NULL,
                         FId char(255),
                         Status NOT NULL
                        )"""
    
    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.conn.close()
    
    def getCursor(self):
        return self.conn.cursor()    
    
instance = DB()