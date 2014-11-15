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
    def __init__(self, data=None):
      self.ip_header = None
      self.tcp_header = None
      self.ip_address = None
      self.header_size = 0

      if data is not None:
          self.parse(data)

    def construct(self):
      tcph = self.tcp_header.construct()
      iph = self.ip_header.construct(self.tcp_header.length)
      self.header_size = self.ip_header.total_length + self.tcp_header.length
      return iph + tcph

    def parse(self, data):
      """
        Parses tcp and ip headers from the packet
        allows access through objects fields
      """
      self.ip_address = data[1]

      self.ip_header = ip_header().parse(data[0])
      self.tcp_header = tcp_header().parse(data[0], self.ip_header.total_length)
      self.header_size = self.ip_header.total_length + self.tcp_header.length

    def __str__(self):
      out = ""
      out += "Header Size: %d\n" % self.header_size
      out += str(self.ip_header)
      out += str(self.tcp_header)
      return out
