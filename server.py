#  coding: utf-8 
# License 2023 Kyle Bricker

import os
import socketserver

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
        print ("Got a request of: %s\n" % self.data)

        # Reference taken from
        # Author: Emalsha - https://emalsha.wordpress.com/
        # https://emalsha.wordpress.com/2016/11/24/how-create-http-server-using-python-socket-part-ii/

        # parse the arguments
        args = self.data.decode('utf-8').split(' ') # split the recieved data
        method = args[0] # this must be GET or returns 405
        requested = args[1] # get the requested file/folder

        # Check the desired method is GET
        if method != 'GET':
            header = 'HTTP/1.1 405 Method Not Allowed\r\n'
            final_response = header.encode('utf-8')
            self.request.sendall(final_response)
            return

        filepath = requested.lstrip('/')
        filepath = 'www/' + filepath
        if os.path.isdir(filepath):
            if not filepath.endswith('/'): # 301
                header = 'HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:8080/' + filepath.lstrip('www/') + '/\r\n'
                final_response = header.encode('utf-8')
                self.request.sendall(final_response)
                return
            filepath += 'index.html'

        # This will try to find, read and send the desired file back to the connected client. If no such file is found then we return 404 Not Found
        try:
            if filepath.endswith('.html'):
                mimetype = 'text/html'
            elif filepath.endswith('.css'):
                mimetype = 'text/css'
            else: # html not specified in file path but could still be desired
                mimetype = 'text/html'
                filepath += 'index.html'
            
            # will return an error if file does not exist -> will direct user to 404 Not Found
            file = open(filepath, 'rb')
            response = file.read()
            file.close()

            header = 'HTTP/1.1 200 OK\nContent-Type: ' + mimetype + '\n\n'

        except Exception as e:
            header = 'HTTP/1.1 404 Not Found\r\n\n'
            response = '<html><body><h3>Error 404: File not found</h3></body></html>\n'.encode('utf-8')

        # Package up our final response to send to the client
        final_response = header.encode('utf-8')
        final_response += response
        self.request.sendall(final_response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
