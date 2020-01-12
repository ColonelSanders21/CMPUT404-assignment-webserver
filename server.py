#  coding: utf-8 
import socketserver
import os
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

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        request_str = self.data.decode('utf-8')
        print(request_str, '\n')
        # We parse this string to determine which response we need to send. 

        # We start by checking whether it's a GET request (or if we need to return a 405)
        if(request_str.split(' ')[0] == "GET"):
            # It's a GET request, so we must respond appropriately.
            # First, a quick check to see whether we should return a 404.
            path = 'www' + request_str.split()[1]
            if os.path.exists(path) and 'www' in os.path.abspath(path):
                # The path is valid. We continue on.

                # We want to redirect via 301 when the path to the resource is not an actual file.
                # ie. /deep --> /deep/
                if '.' not in path:
                    if path[-1] != '/':
                        # We need to redirect via 301.
                        response = 'HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:8080' + path[3:] + '/\r\n'
                    else:
                        # Since the request path ends in /, we send the index.html of that directory.
                        index_file = open((path + 'index.html'), 'r')
                        index_text = index_file.read()
                        index_file.close()
                        response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\n' + index_text
                        
                else:
                    # A file was requested specifically, so we should just return that file. We know it exists from earlier tests.
                    # But we have to consider the mime type.
                    filetype = path.split('.')[-1]
                    if filetype == 'html':
                        mimetype = 'text/html'
                    else:
                        mimetype = 'text/css'
                    page_file = open(path, 'r')
                    page_text = page_file.read()
                    page_file.close()
                    response = 'HTTP/1.1 200 OK\r\nContent-Type: ' + mimetype + '\r\n\n' + page_text
            else:
                # The path is not valid, so we should return a 404.
                response = 'HTTP/1.1 404 Not Found\r\nConnection: close\r\n'
        else:
            # We should refuse connection with a 405, and return that only GET is supported on this server.
            response = 'HTTP/1.1 405 Method Not Allowed\r\nAllow: GET\r\nConnection: close\r\n'
            
        self.request.sendall(bytearray(response, 'utf-8'))
    
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
