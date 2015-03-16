import socket
import os
import sys
from datetime import datetime
from config import PORT, ROOT, LOGFILE
from status import PROTOCOL, OK_STATUS_CODE, NOT_FOUND_CODE
import mimetypes
from urllib import unquote

HOST = ''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

try:
    s.bind((HOST, PORT))
except socket.error, msg:
    print 'Bind failed. Error Code :' +  str(msg[0])
    sys.exit()

print 'Socket bind complete'

s.listen(10)
print 'Socket now listening'
def read_file(filename):
    with open (filename, "r") as myfile:
        data=myfile.read().replace('\n', '')
    return data

def extractpath(path):
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
    return filename
                

def get_command(request):
    strings = request.split()
    return strings

def process_request(request):
    filename = ''
    status_code = ''
    reply = ''
    data = ''
    http_request = request.split('\n')
    commands = get_command(http_request[0])
    print commands
    command = commands[0]
    filename = commands[1]
    filename = extractpath(filename)
    contentType = mimetypes.guess_type(filename)
    print filename
    if(file_exists(filename)):
        status_code = get_status_code(filename)
        data = read_file(filename)
    else:
        status_code = get_status_code(filename)
        data = read_file("template/notfound.html")
    reply = reply + status_code
    reply = reply + 'Server: httplite\n'
    time =  datetime.utcnow().strftime("%a, %d0 %b %Y %X") + " GMT\n"
    reply = reply + 'Date: ' + time
    unicodeReturn = data.decode('utf-8')
    length = len(unicodeReturn)
    reply = reply + 'Content-Length: ' + str(length) + '\n'
    reply = reply + 'Content-Type: ' + contentType[0] + '\n'
    reply = reply + 'Connection: close\n'
    reply = reply + '\n'
    reply = reply + unicodeReturn
    return reply


def file_exists(filename):
    if (os.path.exists(filename) and (os.path.isfile(filename))):
        return True
    else:
        return False

def get_status_code(filename):
    status_code = PROTOCOL + ' ';
    if(file_exists(filename)):
        return status_code + OK_STATUS_CODE + '\n'
    else:
        return status_code + NOT_FOUND_CODE + '\n'


#Function for handling connections. this will be used to create threads
def client_thread(conn):
    #sending message to client:
    #infinite loop so that function do not terminate and the thread does not end.
    #reciveing from client
    data = conn.recv(1024)
    reply = process_request(data)
    conn.sendall(reply)
    #came out of loop
    conn.close()


while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    #display client information
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    client_thread(conn)