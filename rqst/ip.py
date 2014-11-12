import socket
import itertools
import re
from struct import *

class ip_header:
  """
    Provides a interface for constructing and parsing ip headers
  """
  def __init__(self, version=4, length=5, ttl=255, \
          protocol=socket.IPPROTO_TCP,\
          src_adr="192.168.1.211", dest_adr="192.168.1.1"):

    self.length = length
    self.version = version
    self.tos = 0
    self.total_length = 0 # kernel should handle
    self.identification = 54321
    self.offset = 0 # frag_off
    self.ttl = ttl
    self.protocol = protocol
    self.checksum = 0 # kernel should handle
    self.src_adr = socket.inet_aton(src_adr)
    self.dest_adr = socket.inet_aton(dest_adr)

  def construct(self):
    header = pack("!BBHHHBBH4s4s",
              (self.version << 4) + self.length,
              self.tos,
              self.total_length,
              self.identification,
              self.offset,
              self.ttl,
              self.protocol,
              self.checksum,
              self.src_adr,
              self.dest_adr)
    return header

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
