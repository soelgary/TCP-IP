from optparse import OptionParser
from urlparse import urlparse
import sys, binascii

from rqst.connection import TCP_Connection
from rqst.tcp import tcp_header
from rqst.ip import ip_header
from tcp_client import TCPClient

def httpget(arg):
  url = urlparse(arg)
  get_request = "GET " + url.path + " HTTP/1.1\r\nHost: " + url.netloc + "\r\n\r\n"
  request = {}
  request['get_request'] = get_request
  request['scheme'] = url.scheme
  request['domain'] = url.netloc

  tcpclient = TCPClient('192.168.1.1', get_request)
  tcpclient.do_handshake()

  #tcpheader = tcp_header(length=0, src_port=80, dest_port=80,\
  #       ack=0, seq=0, doff_reserved=5, flags=0, window_size=1, checksum=0, urg_pointer=0)

  #ipheader = ip_header()
  #data = ipheader.to_struct() + tcpheader.to_struct() + get_request


if __name__ == '__main__':
  httpget(sys.argv[1])
