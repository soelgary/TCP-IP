import socket
import itertools
import re
from struct import *

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
        self.ip_address = data[1]
        ip_hdr = ip_header().parse(data[0])
        self.ip_header = ip_hdr
        tcp_hdr = tcp_header().parse(data[0], self.ip_header.length)
        self.tcp_header = tcp_hdr

        self.header_size = self.ip_header.length + self.tcp_header.length
        self.data_size = len(data[0]) - self.header_size
        self.raw_data = data[0][self.header_size:]

        return self

    def pprint(self):
      print self.ip_header
      print self.tcp_header

class tcp_header:
  """
    Provides an interface to construct and parse TCP headers
  """
  def __init__(self, length=None, src_port=None, dest_port=None, ack=None, seq=None):
    self.length = length
    self.src_port = src_port
    self.dest_port = dest_port
    self.ack = ack
    self.psh = 0
    self.rst = 0
    self.syn = syn
    self.fin = fin
    self.window = socket.htons(5840)
    self.checksum = 0
    self.urgp = 0
    self.payload = ""

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

    data_offset = (self.offset << 4) + 0

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


  def construct(self):
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

class ip_header:
  """
    Provides a interface for constructing and parsing ip headers
  """
  def __init__(self,version=None,length=None,ttl=None,protocol=None,src_adr=None,dest_adr=None):
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


class TCP_Connection:
    """
      Constructs a new TCP connection
    """
    def __init__(self):
      self.BUFFER_SIZE = (2**16)

    def new_connection(self,hostname):
      # set up raw socket
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
      self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
      # get local ip
      self.host = socket.gethostbyname(socket.gethostname())
      # just support HTTP for now
      self.port = 80
      self.buf = ""
      self.hostname = hostname

    def connect(self):
        """
          Attempts to open a connection to given hostname port
        """
        try:
            self.sock.connect((self.hostname, self.port))
            #self.sock_in.connect((self.hostname, self.port))
            print 'connected to ' + self.hostname
        except socket.gaierror as e:
            print("Recieved error when connecting to " + str((self.hostname, self.port)))
            raise e

    def close(self):
        """
          Closes the socket
        """
        self.sock.shutdown(1)
        self.sock.close()

    def send(self, data):
        """
          sends data over the TCP connection
          data will need to have valid HTTP headers
        """
        print self.host
        self.sock.sendall(data)
        print sys.getsizeof(self.buf)

    def recv(self):
        """
          Parses IP and TCP headers in Packet
          currently logs all packets to stdout
        """
        # self.buf is a tuple of (packet, ip_address)
        self.buf = self.sock.recvfrom(65565)
        p = Packet(data=self.buf,log=True)
        return self.buf

