# Copyright (c) 2008 AG Projects
# Author: Denis Bilenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Test than modules in gevent.green package are indeed green.
To do that spawn a green server and then access it using a green socket.
If either operation blocked the whole script would block and timeout.
"""
from gevent import monkey
monkey.patch_all()

import greentest
import test_support
import urllib2
import BaseHTTPServer
from gevent import spawn


def start_http_server():
    server_address = ('', 0)
    BaseHTTPServer.BaseHTTPRequestHandler.protocol_version = "HTTP/1.0"
    httpd = BaseHTTPServer.HTTPServer(server_address, BaseHTTPServer.BaseHTTPRequestHandler)
    #sa = httpd.socket.getsockname()[1]
    #print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.request_count = 0

    def serve():
        httpd.handle_request()
        httpd.request_count += 1

    return spawn(serve), httpd


class TestGreenness(greentest.TestCase):

    def setUp(self):
        self.gthread, self.httpd = start_http_server()

    def tearDown(self):
        self.httpd.server_close()
        self.gthread.kill(block=True)

    def test_urllib2(self):
        self.assertEqual(self.httpd.request_count, 0)
        port = self.httpd.socket.getsockname()[1]
        try:
            urllib2.urlopen('http://127.0.0.1:%s' % port)
            assert False, 'should not get there'
        except urllib2.HTTPError, ex:
            assert ex.code == 501, repr(ex)
        self.assertEqual(self.httpd.request_count, 1)

if __name__ == '__main__':
    test_support.run_unittest(TestGreenness)
