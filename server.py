#  coding: utf-8 
import socketserver
import os

# Copyright 2020 Andrew Smith
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

RESPONSE_404_HEADERS = """HTTP/1.1 404 Not Found
Content-Type: text/html; charset=UTF-8
Content-Length: {}

"""
RESPONSE_404_BODY="""<html> 
  <head> 
    <title>404 Not Found</title> 
  </head> 
  <body> 
    <h1>404 Not Found</h1>
   </body> 
</html>
"""
RESPONSE_404=RESPONSE_404_HEADERS.format(len(RESPONSE_404_BODY.encode('utf-8')))+RESPONSE_404_BODY

RESPONSE_405_HEADERS = """HTTP/1.1 405 Method Not Allowed
Content-Type: text/html; charset=UTF-8
Content-Length: {}

"""
RESPONSE_405_BODY = """<html> 
  <head> 
    <title>Method Not Allowed</title> 
  </head> 
  <body> 
    <h1>405 Method Not Allowed</h1>
   </body> 
</html>
"""
RESPONSE_405 = RESPONSE_405_HEADERS.format(len(RESPONSE_405_BODY.encode('utf-8')))+RESPONSE_405_BODY

RESPONSE_301 = """HTTP/1.1 301 Moved Permanently
Location: {}\r\n
"""

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.parseRequest()

    def servePage(self,path):
        try:
            name, ext = os.path.splitext(path)
            f = open('www'+path, 'r')
            header = "HTTP/1.1 200 OK\r\n"
            header += "Content-Type: text/"+ext[1:]+"; charset=UTF-8\r\n"
            header += "Content-Length: {}\r\n\r\n"
            data = ""
            for line in f:
                data = data + line
            msg = header.format(len(data.encode('utf-8'))) + data
            self.request.sendall(bytearray(msg,'utf-8'))
        except IOError:
            if os.path.isdir('www'+path):
                data = RESPONSE_301.format("http://127.0.0.1:8080"+path+"/")
                self.request.sendall(bytearray(data,'utf-8'))
            else:
                self.request.sendall(bytearray(RESPONSE_404,'utf-8'))

    def parseRequest(self):
        lines = self.data.split(b'\r\n')
        for line in lines:
            data = line.split(b' ')
            if b'GET' in data[0]:
                dir = data[1].decode('utf-8').replace('..','')
                if dir[-1:] == '/':
                    self.servePage(dir+'index.html')
                else:
                    self.servePage(dir)
            elif b'POST' in data[0] or b'PUT' in data[0] or b'DELETE' in data[0]:
                self.request.sendall(bytearray(RESPONSE_405,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
