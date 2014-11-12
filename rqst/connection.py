import socket, itertools, re, sys, os
from struct import *
from rqst.ip import ip_header
from rqst.tcp import tcp_header
from rqst.packet import Packet

class TCP_Connection:
    """
      Constructs a new TCP connection
    """
    def __init__(self):
      self.BUFFER_SIZE = (2**16)

    def new_connection(self, hostname, port):
      # set up raw socket
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
      # only works with ipproto tcp ....
      self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
      # get local ip
      self.host = socket.gethostbyname(socket.gethostname())

      self.port = port
      self.buf = ""
      self.hostname = hostname
      self.connect()

    def connect(self):
        """
          Attempts to open a connection to given hostname port
        """
        try:
            #self.sock.connect((self.hostname, self.port))
            print 'connected to ' + self.hostname
        except socket.gaierror as e:
            print("Recieved error when connecting to " + str((self.hostname, self.port)))
            raise e

    def close(self):
        """
          Closes the socket
        """
        self.sock.shutdown(1)
        self.sock.close()

    def send(self, data):
        """
          sends data over the TCP connection
          data will need to have valid HTTP headers
        """
        print "Attempting to send packet of size %d to %s" % (len(data), self.hostname)
        self.sock.sendto(data,(self.hostname,0))

    def recv(self):
        """
          Parses IP and TCP headers in Packet
          currently logs all packets to stdout
        """
        self.buf = self.sock_in.recvfrom(65565)
        p = Packet(data=self.buf)
        return p

