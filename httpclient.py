from optparse import OptionParser
import sys
from urlparse import urlparse
from rqst import tcp_header, ip_header
import pprint
import binascii
from rqst import Connection

def httpget(arg):
  url = urlparse(arg)
  get_request = "GET " + url.path + " HTTP/1.1\r\nHost: " + url.netloc + "\r\n\r\n"
  request = {}
  request['get_request'] = get_request
  request['scheme'] = url.scheme
  request['domain'] = url.netloc
  tcpheader = tcp_header(length=0, src_port=80, dest_port=80, ack=0, seq=0, doff_reserved=5, flags=0, window_size=1, checksum=0, urg_pointer=0)
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(tcpheader.to_struct())

  ipheader = ip_header()
  pp.pprint(ipheader.to_struct())

  data = ipheader.to_struct() + tcpheader.to_struct() + get_request
  print "Start"
  print data
  print "End"

  connection = Connection()
  connection.new_connection("gsoeller.com")
  connection.connect()
  connection.send(data)
  

if __name__ == '__main__':
  httpget(sys.argv[1])