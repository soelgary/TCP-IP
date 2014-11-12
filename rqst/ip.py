import socket
import itertools
import re
from struct import *

class ip_header:
  """
    Provides a interface for constructing and parsing ip headers
  """
  def __init__(self, version=None, length=None, ttl=None, \
          protocol=None, src_adr=None, dest_adr=None):

    self.version = version
    self.length = length
    self.ttl = ttl
    self.protocol = protocol
    self.src_adr = src_adr
    self.dest_adr = dest_adr

  def parse(self, packet):
    """
      Parses and returns an ip_header object
      from the packets data
    """
    # header length is 20 
    ip_hdr = packet[0:20]

    # unpack ip_head see:
    #   https://docs.python.org/2/library/struct.html#format-characters
    ip_header_data = unpack('!BBHHHBBH4s4s', ip_hdr)

    # extract version and header length
    v_hl = ip_header_data[0]
    self.version = v_hl >> 4
    self.length = (v_hl >> 4) * 4

    # extract ttl and protocol
    self.ttl = ip_header_data[5]
    self.protocol = ip_header_data[6]

    # get source and destination address
    self.src_adr = socket.inet_ntoa(ip_header_data[8])
    self.dest_adr = socket.inet_ntoa(ip_header_data[9])

    return self

  def construct(self):
    ip_hdr_data = []
    vhl = self.version << 4 + (self.length / 4) << 4
    ip_hdr_data[0] = vhl
    ip_hdr_data[5] = self.ttl
    ip_hdr_data[6] = self.protocol
    ip_hdr_data[8] = self.src_adr
    ip_hdr_data[9] = self.dest_adr
    data = pack('!BBHHHBBH4s4s', ip_hdr_data)
    return data

  def __str__(self):
    out = ""
    out += "IP Header\n"
    out += "Version: %s\n" % str(self.version)
    out += "Length: %d\n" % self.length
    out += "TTL: %d\n" % self.ttl
    out += "Protocol: %s\n" % str(self.protocol)
    out += "Source address: %s\n" % str(self.src_adr)
    out += "Destination address: %s\n" % str(self.dest_adr)
    return out
