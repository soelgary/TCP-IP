import socket
import itertools
import re
from struct import *

class tcp_header:
  def __init__(self, src_addr=None, dest_addr=None,
          ack=0, syn=0, fin=0, seqn=0, checksum=0, ackn=0, payload=""):

    self.src_addr = src_addr
    self.dest_addr = dest_addr
    self.srcp = 1234
    self.dstp = 80
    self.seqn = seqn
    self.ackn = ackn
    self.offset = 5
    self.reserved = 0
    self.urg = 0
    self.ack = ack
    self.psh = 0
    self.rst = 0
    self.syn = syn
    self.fin = fin
    self.window = socket.htons(5840)
    self.checksum = 0
    self.urgp = 0
    self.payload = payload
    self.length = 0

  def gen_checksum(self, header):
    """
      checksum functions needed for calculation checksum
    """
    # if header is odd add padding
    if len(header) % 2 != 0:
        header = header + '0'
    checksum = 0
    for index in range(0, len(header), 2):
        complement = (ord(header[index]) << 8) + (ord(header[index+1]) )
        checksum = checksum + complement
    checksum = (checksum >> 16) + (checksum & 0xffff);
    checksum = ~checksum & 0xffff
    return checksum

  def construct(self):
    data_offset = (self.offset << 4) + 0

    flags = self.fin +\
            (self.syn << 1) +\
            (self.rst << 2) +\
            (self.psh << 3) +\
            (self.ack << 4) +\
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

    pseudo_header = pack('!4s4sBBH',
            socket.inet_aton(self.src_addr),
            socket.inet_aton(self.dest_addr),
            0,
            socket.IPPROTO_TCP,
            len(header))

    check = self.gen_checksum((pseudo_header + header + self.payload))

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

    return header + self.payload

  def parse(self, packet, offset):
    tcp_header_data = unpack('!HHLLBBHHH', packet[offset:offset+20])
    # Get various field data
    self.srcp = tcp_header_data[0]
    self.dstp = tcp_header_data[1]
    self.seqn = tcp_header_data[2]
    self.ackn = tcp_header_data[3]
    self.doff_reserved = tcp_header_data[4]
    self.length = (self.doff_reserved >> 4) * 4
    # parse header data
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

  def __str__(self):
    """
      Overrides string method to allow string casting
      to return this

      print packet instead of packet.pprint()
    """
    out = ""
    out+= "TCP Header"
    out+= "Source port: %s\n" % self.srcp
    out+= "Destination port: %s\n" % self.dstp
    out+= "Sequence Number: %s\n" % self.seqn
    out+= "Acknowledgemnet Number: %s\n" % self.ackn
    out+= "Data Offset: %s\n" % self.offset
    out+= "Reserved: %s\n" % self.reserved
    out+= "Fin: %d\n" % self.fin
    out+= "Syn: %d\n" % self.syn
    out+= "Rst: %d\n" % self.rst
    out+= "Psh: %d\n" % self.psh
    out+= "Ack: %d\n" % self.ack
    out+= "Urg: %d\n" % self.urg
    out+= "Window Size: %d\n" % socket.htons(5840)
    out+= "Checksum: %d\n" % self.checksum
    out+= "Urgent Point: %d" % self.urgp
    return out

