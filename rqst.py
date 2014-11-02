import socket
import itertools
import re
from struct import *


class Packet:
    def __init__(self, data=None):
        self.ip_header = None
        self.tcp_header = None
        self.ip_address = None
        self.header_size = 0
        self.data_size = 0

        if data is not None:
          self.ip_address = data[1]
          self.ip_header = self.parse_ip_header(data[0])
          self.tcp_header = self.parse_tcp_header(data[0], self.ip_header.length)
          self.header_size = self.ip_header.length + self.tcp_header.length
          self.data_size = len(data[0]) - self.header_size
          self.raw_data = data[0][self.header_size:]
          self.pprint()

    def pprint(self):
      self.ip_header.pprint()
      self.tcp_header.pprint()
           
    def parse_ip_header(self, packet):
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
        version = v_hl >> 4
        ip_header_length = (v_hl >> 4) * 4

        # extract ttl and protocol
        ttl = ip_header_data[5]
        protocol = ip_header_data[6]
        
        # get source and destination address
        src_adr = socket.inet_ntoa(ip_header_data[8])
        dest_adr = socket.inet_ntoa(ip_header_data[9])

        return ip_header(version=version, length=ip_header_length,\
            ttl=ttl, protocol=protocol, src_adr=src_adr, dest_adr=dest_adr)

    def parse_tcp_header(self, packet, offset):
        # Extract TCP Header
        tcp_hdr = packet[offset:offset+ 20]
        tcp_header_data = unpack('!HHLLBBHHH', tcp_hdr)

        # Get various field data
        source_port = tcp_header_data[0]
        dest_port = tcp_header_data[1]
        sequence = tcp_header_data[2]
        ack = tcp_header_data[3]
        doff_reserved = tcp_header_data[4]
        tcp_length = (doff_reserved >> 4) * 4

        return tcp_header(length=tcp_length, src_port=source_port, dest_port=dest_port,\
            ack=ack, seq=sequence)

    
class tcp_header:
  def __init__(self, ack=0, syn=0, fin=0, seqn=0, checksum=0):
    self.srcp = 80
    self.dstp = 80
    self.seqn = seqn
    self.ackn = 0
    self.offset = 5
    self.reserved = 0
    self.urg = 0
    self.ack = ack
    self.psh = 1
    self.rst = 0
    self.syn = syn
    self.fin = fin
    self.window = socket.htons(5840)
    self.checksum = checksum
    self.urgp = 0
    self.payload = ""

  def to_struct(self):
    data_offset = (self.offset << 4) + (0 << 1) + 0
    flags = self.urg + (self.ack << 1) + (self.psh << 2) + (self.rst << 3) + (self.syn << 4) + (self.fin << 5)
    print "FLAGS: %d" % flags
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
    return header


  def pprint(self):
    print "TCP Header"
    print "Source port: %s" % self.srcp
    print "Destination port: %s" % self.dstp
    print "Sequence Number: %s" % self.seqn
    print "Acknowledgemnet Number: %s" % self.ackn
    print "Data Offset: %s" % self.offset
    print "Reserved: %s" % self.reserved
    print "Flags: %d" % (self.fin + (self.syn << 1) + (self.rst << 2) + (self.psh << 3) + (self.ack << 4) + (self.urg << 5))
    print "Window Size: %d" % socket.htons(5840)
    print "Checksum: %d" % self.checksum
    print "Urgent Point: %d" % self.urgp

class ip_header:
  def __init__(self, checksum=0, length=15, src_adr="127.0.0.1", dest_adr="54.213.206.253", reserved=0):
    self.version = 4
    self.ihl = 5
    self.dscp = 0
    self.ecn = 0
    self.total_length = 666
    self.identification = 0
    self.flags = 0
    self.offset = 0
    self.ttl = 0
    self.protocol = socket.IPPROTO_TCP
    self.checksum = checksum
    self.src_adr = socket.inet_aton(src_adr)
    self.dest_adr = socket.inet_aton(dest_adr)

  def to_struct(self):
    header = pack("!BBHHHBBH4s4s",
              (self.version << 4) + self.ihl,
              (self.dscp << 2) + self.ecn,
              self.total_length,
              self.identification,
              (self.flags << 13) + self.offset,
              self.ttl,
              self.protocol,
              self.checksum,
              self.src_adr,
              self.dest_adr)
    return header

  def pprint(self):
    print "IP Header"
    print "Version: %s" % str(self.version)
    print "Length: %d" % self.length
    print "TTL: %d" % self.ttl
    print "Protocol: %s" % str(self.protocol)
    print "Source address: %s" % str(self.src_adr)
    print "Destination address: %s" % str(self.dest_adr)


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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        # get local ip
        self.host = socket.gethostbyname(socket.gethostname())

        self.port = 80
        self.buf = ""
        self.hostname = hostname

    def connect(self):
        try:
            self.sock.connect((self.hostname,self.port))
            print 'connected to ' + self.hostname
        except socket.gaierror as e:
            print("Recieved error when connecting to " + str((self.hostname, self.port)))
            raise e

    def close(self):
        self.sock.shutdown(1)
        self.sock.close()

    def send(self, data):
        self.sock.sendall(data)
        print "Sent,\t", data

    def recv(self):
        # self.buf is a tuple of (packet, ip_address)
        self.buf = self.sock.recvfrom(65565)
        p = Packet(self.buf)
        return self.buf
