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

import sqlite3


class BBS:
    
    def __init__(self):
        
        self.DB_BBS_PATH = 'bbs.db'   
        self.bbs_conn = sqlite3.connect(self.DB_BBS_PATH)
    
    def commit(self):
        self.bbs_conn.commit()
        
    def close(self):
        self.bbs_conn.close()
    
    def getCursor(self):
        return self.bbs_conn.cursor()
    

class User:
    
    def __init__(self):
        self.DB_USERS_PATH = 'users.db'
        self.user_conn = sqlite3.connect(self.DB_USERS_PATH)
    
    def commit(self):
        self.user_conn.commit()
    
    def close(self):
        self.user_conn.close()
    
    def getCursor(self):
        return self.user_conn.cursor()    