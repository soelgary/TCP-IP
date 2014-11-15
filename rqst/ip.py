import socket
import itertools
import re
from struct import *

class ip_header:
  def __init__(self, checksum=0, length=15, src_adr="127.0.0.1", dest_adr="54.213.206.253", reserved=0):
    self.version = 4
    self.ihl = 5
    self.tos = 0
    self.total_length = 40
    self.identification = 54321
    self.offset = 0
    self.ttl = 255
    self.protocol = socket.IPPROTO_TCP
    self.checksum = 0
    self.src_adr = src_adr
    self.dest_adr = dest_adr

  def construct(self, offset):
    print offset / 4
    print 'Offset: XXXXXXXXXxx %d' % offset
    #offset = (offset / 4) - 5

    header = pack("!BBHHHBBH4s4s",
              (self.version << 4) + self.ihl,
              self.tos,
              self.total_length,
              self.identification,
              self.offset,
              self.ttl,
              self.protocol,
              self.checksum,
              socket.inet_aton(self.src_adr),
              socket.inet_aton(self.dest_adr))
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
    self.ihl = v_hl & 0xF
    self.total_length = self.ihl * 4

    # extract ttl and protocol
    self.ttl = ip_header_data[5]
    self.protocol = ip_header_data[6]

    # get source and destination address
    self.src_adr = socket.inet_ntoa(ip_header_data[8])
    self.dest_adr = socket.inet_ntoa(ip_header_data[9])

    return self

  def __str__(self):
    out = ""
    out+= "IP Header"
    out+= "Version:\t%d\n" % self.version
    out+= "Length:\t%d\n" % self.total_length
    out+= "TTL:\t%d\n" % self.ttl
    out+= "Protocol:\t%d\n" % self.protocol
    out+= "Source address:\t%s\n" % self.src_adr
    out+= "Destination address:\t%s\n" % self.dest_adr
    return out
