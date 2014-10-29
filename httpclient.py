from optparse import OptionParser
import sys
from urlparse import urlparse
from tcpclient import TCPClient

def httpget(arg):
  url = urlparse(arg)
  get_request = "GET " + url.path + " HTTP/1.1\r\nHost: " + url.netloc + "\r\n\r\n"
  request = {}
  request['get_request'] = get_request
  request['scheme'] = url.scheme
  request['domain'] = url.netloc
  tcpClient = TCPClient()
  response = tcpClient.send(request)
  print response

  

if __name__ == '__main__':
  httpget(sys.argv[1])