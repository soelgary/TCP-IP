import socket
import itertools
import re
from struct import *

class tcp_header:
  """
    Provides an interface to construct and parse TCP headers
  """
  def __init__(self, length=None, src_port=None, dest_port=None,\
  src_addr=None, dest_addr=None,\
  ack=0, seq=None, syn=0, fin=0, seqn=0, checksum=0):

    self.length = length
    self.src_port = src_port
    self.dest_port = dest_port
    self.ack = ack
    self.seq = seq
    self.psh = 0
    self.rst = 0
    self.syn = syn
    self.fin = fin
    self.window = socket.htons(5840)
    self.checksum = checksum
    self.urgp = 0
    self.payload = ""

    self.src_addr = src_addr
    self.dest_addr = dest_addr

    self.srcp = 1234
    self.dstp = 80
    self.seqn = seqn
    self.ackn = 0
    self.offset = 5
    self.reserved = 0
    self.urg = 0


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

  def to_struct(self):
    """
     converts internal data into binary stuct for transmission
    """

    data_offset = (self.offset << 4) + 0
    print (self.ack, self.fin, self.syn, self.rst, self.psh, self.urg)

    flags = self.fin + \
            (self.syn << 1) + \
            (self.rst << 2) + \
            (self.psh << 3) + \
            (self.ack << 4) + \
            (self.urg << 5)

    header = pack('!HHLLBBHHH',
                  self.srcp,
                  self.dstp,
                  self.seqn,
                  self.ackn,
                  data_offset,
                  flags,
                  self.window,
                  self.checksum,
                  self.urgp)

    pseudo_header = pack('!4s4sBBH',\
            socket.inet_aton(self.src_addr),\
            socket.inet_aton(self.dest_addr),\
            0,\
            socket.IPPROTO_TCP,\
            len(header))

    check = self.gen_checksum((pseudo_header + header))

    header = pack('!HHLLBBHHH',
                  self.srcp,
                  self.dstp,
                  self.seqn,
                  self.ackn,
                  data_offset,
                  flags,
                  self.window,
                  check,
                  self.urgp)
    return header

  def parse2(self, packet, offset):
    """
      Parse tcp header out of raw packet data
      offset is the size of the ip header
    """

    tcp_header_data = unpack('!HHLLBBHHH', packet[offset:offset+20])
    # Get various field data
    self.srcp = tcp_header_data[0]
    self.dstp = tcp_header_data[1]
    self.seqn = tcp_header_data[2]
    self.ackn = tcp_header_data[3]
    self.doff_reserved = tcp_header_data[4]
    self.length = (self.doff_reserved >> 4) * 4
    flags = tcp_header_data[5]
    self.fin = (flags & 1)
    self.syn = (flags & 2) >> 1
    self.rst = (flags & 4) >> 2
    self.psh = (flags & 8) >> 3
    self.ack = (flags & 16) >> 4
    self.urg = (flags & 32) >> 5
    self.ece = (flags & 64) >> 6
    self.cwr = (flags & 128) >> 7
    self.window = tcp_header_data[6]
    self.checksum = tcp_header_data[7]
    self.urgp = tcp_header_data[8]
    return self


  def construct(self):
    """
      Non tested
    """
    tcp_header_data = []
    tcp_header_data[0] = self.src
    tcp_header_data[1] = self.dest_port 
    tcp_header_data[2] = self.seq
    tcp_header_data[3] = self.ack
    # does this work?
    doff_reserved = (self.length / 4) << 4
    tcp_header_data[4] = doff_reserved
    data = pack('!HHLLBBHHH',tcp_header_data)
    return data

  def parse(self, packet, offset):
    """
      Not sure why there are two of these
    """
    tcp_header_data = unpack('!HHLLBBHHH', packet[offset:offset+20])

    # Get various field data
    self.src = tcp_header_data[0]
    self.dest_port = tcp_header_data[1]
    self.seq = tcp_header_data[2]
    self.ack = tcp_header_data[3]
    doff_reserved = tcp_header_data[4]
    self.length = (doff_reserved >> 4) * 4

    return self

  def __str__(self):
    out = ""
    out += "TCP Header\n"
    out += "Source port: %s\n" % self.src_port
    out += "Destination port: %s\n" % self.dest_port
    out += "Acknowledgemnet: %s\n" % self.ack
    out += "Sequence: %s\n" % self.seq
    out += "TCP Length: %d\n" % self.length
    return out
