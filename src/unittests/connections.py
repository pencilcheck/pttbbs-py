import unittest

import gevent
from gevent import socket

class TestConnections(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConnections(self):
        for i in xrange(1000):        
            sock = socket.socket()
            sock.connect(('127.0.0.1', 9090))
            print sock.recv(4096)
            sock.send(str(i))
            #sock.close()
            
            
if __name__ == '__main__':
    unittest.main()