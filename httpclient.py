from optparse import OptionParser
from urlparse import urlparse
import sys, binascii

from rqst.connection import TCP_Connection
from rqst.tcp import tcp_header
from rqst.ip import ip_header
from tcp_client import TCPClient
import socket

def httpget(arg):
  url = urlparse(arg)
  get_request = "GET " + url.path + " HTTP/1.1\r\nHost: " + url.netloc + "\r\n\r\n"
  request = {}
  request['get_request'] = get_request
  request['scheme'] = url.scheme
  request['domain'] = url.netloc

  tcpclient = TCPClient(socket.gethostbyname(url.netloc),80, get_request)
  tcpclient.do_handshake()

if __name__ == '__main__':
  httpget(sys.argv[1])
