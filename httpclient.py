import sys, binascii, socket, re
from optparse import OptionParser
from urlparse import urlparse

from rqst.connection import TCP_Connection
from rqst.tcp import tcp_header
from rqst.ip import ip_header
from tcp_client import TCPClient

def is_ip(arg):
    aa=re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",arg)
    if aa:
        return True
    else:
        return False

def httpget(arg):
  request = {}
  if is_ip(arg):
      print 'rec ip'
      get_request = "GET " + '/' + " HTTP/1.1\r\nHost: " + arg + "\r\n\r\n"
      request['get_request'] = get_request
      request['scheme'] = 'http'
      request['domain'] = arg
      tcpclient = TCPClient(arg, 80, get_request)
  else:
      url = urlparse(arg)
      path = url.path
      filename = path.split('/')[-1]
      print filename
      if url.path == "":
        path = '/'
        filename = 'index.html'
      get_request = "GET " + url.path  + " HTTP/1.0\r\nHost: " + url.netloc + "\r\n\r\n"
      request['get_request'] = get_request
      request['scheme'] = url.scheme
      request['domain'] = url.netloc
      tcpclient = TCPClient(socket.gethostbyname(url.netloc), 80, get_request)

  tcpclient.do_handshake()
  data = tcpclient.get_data()

  f = open(filename, 'w')
  f.write(data.split('\r\n\r\n')[1])
  f.close()

if __name__ == '__main__':
  httpget(sys.argv[1])
