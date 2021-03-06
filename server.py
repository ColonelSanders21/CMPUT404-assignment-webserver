#  coding: utf-8 
import socketserver
import os
import time
# Copyright 2020 Abram Hindle, Eddie Antonio Santos, Anders Johnson
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

    def get_date(self):
        # Returns string with the current date, for use with HTTP headers.
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

    def get_page(self, message):
        # Using a simple HTML template, returns a small webpage containing the message provided.
        page = '''
        <html>
            <head>
                <title>%s</title>
            </head>
            <body>
                <center>
                    <h1>%s</h1>
                </center>
            </body>
        </html>
        ''' % (message, message)
        return page

    def get_content_length(self, page):
        # Given a string, returns the length of what the string will be encoded so we can share the content length.
        return len(page.encode('utf-8'))

    def handle_405(self, request_str):
        # Test to determine whether or not we need to return a 405. 
        # If we should, it returns the appropriate response message.
        # Else, it returns False.

        # We just check to see if it's a GET request.
        if(request_str.split(' ')[0] == "GET"):
            return False
        # Else, we respond with a simple HTML page saying that the method is not allowed.
        message = "405 Method Not Allowed"
        page = self.get_page(message)
        content_length = self.get_content_length(page)
        response = 'HTTP/1.1 %s\r\nDate: %s\r\nServer: CMPUT404a1\r\nAllow: GET\r\nContent-Type: text/html\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s' % (message, self.get_date(), content_length, page)
        return response

    def handle_404(self,request_str):
        # Test to determine whether to send a 404.
        # If we should, it returns the appropriate response message.
        # Else, it returns False.

        # In a nutshell: check to see if the requested path is:
        # A) to a file or folder that actually exists
        # B) to a file or folder contained within www
        # If one or both of these are not the case then we should send a 404.

        allowed = os.path.abspath('www') # This is the path to our www folder
        path = 'www' + request_str.split()[1] # This gives a path to resource the HTTP request is requesting
        if os.path.exists(path) and (os.path.abspath(path)[:len(allowed)] == allowed):
            # If the path points to a valid resource, and the absolute path leads to something in the appropriate www folder
            if os.path.isfile(path):
                # If the path requests a specific file and the filetype is not html or css, we should also return a 404. https://tools.ietf.org/html/rfc7231#section-6.5.4
                filetype = path.split('.')[-1]
                if filetype == 'html' or filetype == 'htm' or filetype == 'css':
                    return False
            elif path[-1] =='/':
                # If the path ends in a /, it requests index.html by default. If this file doesn't exist we should be returning a 404.
                if os.path.exists(path+'index.html'):
                    return False
            else:
                # We leave this path to be corrected by 301. If the new location path does not include index.html then a 404 will be served from the above tests.
                return False
        message = "404 Not Found"
        page = self.get_page(message)
        content_length = self.get_content_length(page)
        response = 'HTTP/1.1 %s\r\nDate: %s\r\nServer: CMPUT404a1\r\nContent-Type: text/html\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s' % (message, self.get_date(), content_length, page)
        return response

    def handle_301(self, request_str):
        # Test to determine whether to send a 301.
        # If we should, it returns a 301 reponse.
        # Else, returns False.
        path = 'www' + request_str.split()[1]
        if os.path.isfile(path):
            return False # They're requesting a file that is where they say it is. So we should just be sending a 200 OK.
        if path[-1] == '/':
            return False # We just need to return the index.html from this folder. We will do this in handle_200
        message = "301 Moved Permanently"
        page = self.get_page(message)
        content_length = self.get_content_length(page)
        response = ('HTTP/1.1 %s\r\nDate: %s\r\nServer: CMPUT404a1\r\nLocation: ' % (message, self.get_date())) + path[4:] + ('/\r\nContent-Type: text/html\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s' % (content_length, page))
        return response

    def handle_200(self, request_str):
        # We have passed all the other tests, so we send a 200 OK.
        # Returns our response.
        path = 'www' + request_str.split()[1]
        if path[-1] == '/':
            # We return index.html from that folder.
            index_file = open((path + 'index.html'), 'r')
            index_text = index_file.read()
            index_file.close()
            content_length = self.get_content_length(index_text)
            response = 'HTTP/1.1 200 OK\r\nDate: %s\r\nServer: CMPUT404a1\r\nContent-Type: text/html\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s' % (self.get_date(), content_length, index_text)
            return response
        filetype = path.split('.')[-1]
        if filetype == 'html' or filetype == 'htm':
            mimetype = 'text/html'
        elif filetype == 'css':
            mimetype = 'text/css'
        page_file = open(path, 'r')
        page_text = page_file.read()
        page_file.close()
        content_length = self.get_content_length(page_text)
        response = 'HTTP/1.1 200 OK\r\nDate: %s\r\nServer: CMPUT404a1\r\nContent-Type: %s\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s' % (self.get_date(),mimetype, content_length, page_text)
        return response

    def handle(self):
        self.data = self.request.recv(1024).strip()
        request_str = self.data.decode('utf-8')
        # We parse this string to determine which response we need to send. 

        # We run a few methods to determine if a certain reponse is necessary. If it is, we return the response they return.
        # Else, we continue testing to see if other responses are necessary.
        # Some of these run tests that others assume have passed.
        response = self.handle_405(request_str)
        if not response:
            response = self.handle_404(request_str)
            if not response:
                response = self.handle_301(request_str)
                if not response:
                    response = self.handle_200(request_str)
        self.request.sendall(bytearray(response, 'utf-8'))
    
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
