from HTTPLiteServer import HTTPLiteServer
import sys

try:
    server = HTTPLiteServer()
    server.run()
except:
    print "Unexpected error:", sys.exc_info()
