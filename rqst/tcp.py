import socket
import itertools
import re
from struct import *

class tcp_header:
  """
    Provides an interface to construct and parse TCP headers
  """
  def __init__(self, length=None, src_port=1234, dest_port=80,\
        src_addr=None, dest_addr=None,\
        ack_seq=0, seq=0, syn=0, fin=0, checksum=0):

    # (doff >> 4) * 4
    self.length = length
    # again a field used in input
    self.payload = ""
    # not sure about these two
    self.src_addr = src_addr
    self.dest_addr = dest_addr

    # header fields
    self.src_port = src_port
    self.dest_port = dest_port
    self.seq = seq
    self.ack_seq = ack_seq
    self.doff = 5 # 4 bit field, tcp header size, 5 * 4 = 20

    # flags
    self.fin = fin
    self.syn = syn
    self.rst = 0
    self.psh = 0
    self.ack = 0
    self.urg = 0
    self.window = socket.htons(5840) # max window size
    self.checksum = checksum
    self.urgp = 0

    self.offset = (self.doff << 4) + 0 # tcp offset res

  def construct(self):
    self.flags = self.fin + (self.syn << 1) + \
        (self.rst << 2) + (self.psh << 3) + (self.ack << 4) + (self.urg << 5)

    print (self.src_port, self.dest_port, self.seq, self.ack_seq, self.offset, self.flags, self.window, self.checksum, self.urgp)

    # the ! in the pack format string means network order
    header = pack('!HHLLBBHHH',\
        self.src_port, self.dest_port,\
        self.seq, self.ack_seq,\
        self.offset, self.flags,\
        self.window, self.checksum, self.urgp)

    return header


  def gen_checksum(self, header):
    """
      checksum functions needed for calculation checksum
    """
    checksum = 0
    for index in range(0, len(header), 2):
        complement = (ord(header[index]) << 8) + (ord(header[index+1]) )
        checksum = checksum + complement
    checksum = (checksum >> 16) + (checksum & 0xffff);
    checksum = ~checksum & 0xffff
    return checksum

  def gchecksum(self, msg):
    s = 0
    for i in range(0, len(msg),2):
      w = ord(msg[i]) + (ord(msg[i+1]) << 8)
      s = s + w
    s = (s >> 16) + (s & 0xffff)
    s = s + (s >> 16)
    return s

  def parse(self, packet, offset):
    """
      Parse tcp header out of raw packet data
      offset is the size of the ip header
    """
    tcp_header_data = unpack('!HHLLBBHHH', packet[offset:offset+20])

    # Get header data
    self.src_port = tcp_header_data[0]
    self.dest_port = tcp_header_data[1]
    self.seq = tcp_header_data[2]
    self.ack_seq = tcp_header_data[3]
    doff_reserved = tcp_header_data[4]
    self.length = (doff_reserved >> 4) * 4

    # Get flags
    flags = tcp_header_data[5]
    self.fin = (flags & 1)
    self.syn = (flags & 2) >> 1
    self.rst = (flags & 4) >> 2
    self.psh = (flags & 8) >> 3
    self.ack = (flags & 16) >> 4
    self.urg = (flags & 32) >> 5

    #self.ece = (flags & 64) >> 6
    #self.cwr = (flags & 128) >> 7

    self.window = tcp_header_data[6]
    self.checksum = tcp_header_data[7]
    self.urgp = tcp_header_data[8]

    return self

  def __str__(self):
    out = ""
    out += "TCP Header\n"
    out += "Source port: %s\n" % self.src_port
    out += "Destination port: %s\n" % self.dest_port
    out += "Acknowledgemnet: %s\n" % self.ack_seq
    out += "Sequence: %s\n" % self.seq
    out += "TCP Length: %d\n" % self.length
    return out



