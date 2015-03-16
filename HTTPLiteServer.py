import socket
import os
import sys
from datetime import datetime
from config import PORT, ROOT, LOGFILE
from status import PROTOCOL, OK_STATUS_CODE, NOT_FOUND_CODE
import mimetypes
from urllib import unquote

HOST = ''
class HTTPLiteServer (object):

    def __init__(self):
         print 'Server Started: '

    def get_default_headers(self):
        reply = 'Server: httplite\n'
        time =  datetime.utcnow().strftime("%a, %d0 %b %Y %X") + " GMT\n"
        reply = reply + 'Date: ' + time
        reply = reply + 'Connection: close\n'
        return reply

    def extractpath(self, path):
        print "path is " + path
        filename = ''
        path = unquote(path)
        print "path is " +  path
        if(path == '/'):
            filename =  '/index.html'
        elif(path.endswith('/')):
            filename = path + 'index.html'
        else:
            filename = path

        somepath =  os.path.abspath(ROOT)
        #used for windows needs to be changed when transfered to linux
        filename = somepath + filename
        print filename
        return filename

    #Function for handling connections. this will be used to create threads
    def client_thread(self, conn):
        data = conn.recv(1024)
        print "recived data"
        http_request = data.split('\n')
        print "split 1"
        commands = http_request[0].split(' ')
        print "split 2"
        reply = ""
        command = commands[0]
        if(command != "GET"):
            reply = self.not_found();
        else:
            path = commands[1]
            path = unquote(path)
            filename = self.extractpath(path)
            if(self.file_exists(filename)):
                header = PROTOCOL + ' ' + OK_STATUS_CODE + '\n'
                contentType = mimetypes.guess_type(filename)
                data = self.read_file(filename)
                data = data.decode('utf-8')
                header = header + self.get_default_headers()
                header = header + self.get_entity_headers(data, contentType[0] )
                reply = header + '\n' + data
            else:
                reply = self.not_found()

            conn.sendall(reply)
            #came out of loop
            conn.close()


    def file_exists(self, filename):
        if (os.path.exists(filename) and (os.path.isfile(filename))):
            return True
        else:
            return False

    def not_found(self):
        data = self.read_file("template/notfound.html")
        header = PROTOCOL + ' ' + NOT_FOUND_CODE + '\n'
        data = data.decode('utf-8')
        header = header +  self.get_default_headers()
        header = header + self.get_entity_headers( data, "text/html")
        reply = header +'\n'+ data
        return reply

    def get_entity_headers(self,reply, contentType):
        length = len(reply)
        header = 'Content-Length: ' + str(length) + '\n'
        header = header + 'Content-Type: ' + contentType + '\n'
        header = header + 'Connection: close\n' #leave this here for now
        return header

    def read_file(self, filename):
        with open (filename, "r") as myfile:
            data=myfile.read().replace('\n', '')
        return data


    def run (self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((HOST, PORT))
        except socket.error, msg:
            print 'Bind failed. Error Code :' +  str(msg[0])
            sys.exit()

        print 'Socket bind complete'

        sock.listen(10)
        while 1:
            #wait to accept a connection - blocking call
            conn, addr = sock.accept()
            #display client information
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
            self.client_thread(conn)
