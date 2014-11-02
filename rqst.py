import socket
import itertools
import re
from struct import *
import sys

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
        self.pprint()

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
      tcp_hdr.pprint()
      #self.tcp_header = tcp_hdr

      #self.header_size = self.ip_header.length + self.tcp_header.length
      #self.data_size = len(data[0]) - self.header_size
      #self.raw_data = data[0][self.header_size:]

      #return self

    def pprint(self):
      print self.ip_header
      print self.tcp_header
    
class tcp_header:
  def __init__(self, src_addr=None, dest_addr=None, ack=0, syn=0, fin=0, seqn=0, checksum=0):
    self.src_addr = src_addr
    self.dest_addr = dest_addr
    self.srcp = 1234
    self.dstp = 80
    self.seqn = seqn
    self.ackn = 0
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
    self.payload = ""

  # checksum functions needed for calculation checksum
  def gen_checksum(self, header):
    checksum = 0
    for index in range(0, len(header), 2):
        complement = (ord(header[index]) << 8) + (ord(header[index+1]) )
        checksum = checksum + complement
    checksum = (checksum >> 16) + (checksum & 0xffff);
    checksum = ~checksum & 0xffff
    return checksum

  def to_struct(self):
    data_offset = (self.offset << 4) + 0
    flags = self.fin + (self.syn << 1) + (self.rst << 2) + (self.psh << 3) + (self.ack << 4) + (self.urg << 5) 
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
    pseudo_header = pack('!4s4sBBH' , socket.inet_aton(self.src_addr) , socket.inet_aton(self.dest_addr) , 0 , socket.IPPROTO_TCP , len(header))
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

  def parse(self, packet, offset):
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


  def pprint(self):
    print "TCP Header"
    print "Source port: %s" % self.srcp
    print "Destination port: %s" % self.dstp
    print "Sequence Number: %s" % self.seqn
    print "Acknowledgemnet Number: %s" % self.ackn
    print "Data Offset: %s" % self.offset
    print "Reserved: %s" % self.reserved
    print "Fin: %d" % self.fin
    print "Syn: %d" % self.syn
    print "Rst: %d" % self.rst
    print "Psh: %d" % self.psh
    print "Ack: %d" % self.ack
    print "Urg: %d" % self.urg
    print "Ece: %d" % self.ece
    print "Cwr: %d" % self.cwr
    print "Window Size: %d" % socket.htons(5840)
    print "Checksum: %d" % self.checksum
    print "Urgent Point: %d" % self.urgp

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
    self.src_adr = socket.inet_aton(src_adr)
    self.dest_adr = socket.inet_aton(dest_adr)

  def to_struct(self):
    header = pack("!BBHHHBBH4s4s",
              (self.version << 4) + self.ihl,
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
    self.ihl = v_hl & 0xF
    self.total_length = self.ihl * 4

    # extract ttl and protocol
    self.ttl = ip_header_data[5]
    self.protocol = ip_header_data[6]
    
    # get source and destination address
    self.src_adr = socket.inet_ntoa(ip_header_data[8])
    self.dest_adr = socket.inet_ntoa(ip_header_data[9])

    self.pprint()
    return self

  def pprint(self):
    print "IP Header"
    print "Version:\t", self.version
    print "Length:\t", self.total_length
    print "TTL:\t", self.ttl
    print "Protocol:\t", self.protocol
    print "Source address:\t", self.src_adr
    print "Destination address:\t", self.dest_adr


class Connection:
    def __init__(self):
        self.BUFFER_SIZE = (2**16)

    def new_basic_connection(self, hostname):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostbyname(socket.gethostname())
        self.hostname = socket.gethostbyname(hostname)
        self.port = 80
        self.buf = ""
        print self.hostname

    def new_connection(self, hostname):
        
        # set up raw socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        # get local ip
        self.host = socket.gethostbyname(socket.gethostname())

        self.port = 80
        self.buf = ""
        self.hostname = hostname

    def connect(self):
        try:
            self.sock.connect((self.hostname, self.port))
            #self.sock_in.connect((self.hostname, self.port))
            print 'connected to ' + self.hostname
        except socket.gaierror as e:
            print("Recieved error when connecting to " + str((self.hostname, self.port)))
            raise e

    def close(self):
        self.sock.shutdown(1)
        self.sock.close()

    def send(self, data):
        self.sock.sendall(data)
        print sys.getsizeof(self.buf)

    def recv(self):
        # self.buf is a tuple of (packet, ip_address)
        self.buf = self.sock_in.recvfrom(65565)
        print sys.getsizeof(self.buf)
        p = Packet(data=self.buf,log=True)
