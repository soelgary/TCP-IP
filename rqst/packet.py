import socket
import itertools
import re
from struct import *
from rqst.tcp import tcp_header
from rqst.ip import ip_header
from ip import ip_header
from tcp import tcp_header


class Packet:
    """
    the Packet object encapsulates the TCP and IP
    layers by extracting raw data into appropriate header
    objects and providing a clean interface for construction
    of packets
    """
    def __init__(self, data=None,log=False):
      self.ip_header = None
      self.tcp_header = None
      self.ip_address = None
      self.header_size = 0
      self.data_size = 0

      if data is not None:
          self.parse(data)
      if log:
        pass
        #self.pprint()

    def construct(self):
      return self.ip_header.construct() + self.tcp_header.construct()

    def parse(self, data):
      """
      Parses tcp and ip headers from the packet
      allows access through objects fields
      """
      #print unpack("!HHLLBBHHH", data)
      #print "Data:\t", data
      self.ip_address = data[1]
      #print "IP Address: %s" % self.ip_address
      ip_hdr = ip_header().parse(data[0])
      self.ip_header = ip_hdr
      #ip_hdr.pprint()
      tcp_hdr = tcp_header().parse(data[0], self.ip_header.total_length)
      #tcp_hdr.pprint()
      self.tcp_header = tcp_hdr

      #self.header_size = self.ip_header.length + self.tcp_header.length
      #self.data_size = len(data[0]) - self.header_size
      #self.raw_data = data[0][self.header_size:]

      #return self

    def pprint(self):
      self.ip_header.pprint()
      self.tcp_header.pprint()