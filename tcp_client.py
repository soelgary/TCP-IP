import socket
from rqst import Connection, tcp_header, ip_header
import pprint
from struct import *
import binascii

class TCPClient():
  def __init__(self, destination, data):
    self.dest_addr = socket.gethostbyname(destination)
    self.src_addr = socket.gethostbyname(socket.gethostname())
    self.data = data
    self.connection = Connection()

  def do_handshake(self):
    self.connection.new_connection(self.dest_addr)
    self.connection.connect()
    tcp_header(syn=1).pprint()

    tcpheader = tcp_header(syn=1).to_struct()
    ipheader = ip_header(src_adr=self.src_addr, dest_adr=self.dest_addr).to_struct()
    packet = ipheader + tcpheader


    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(ipheader)
    pp.pprint(tcpheader)
    print calcsize('!BBHHHBBH4s4s')
    print calcsize('!HHLLBBHHH')

    print unpack('!BBHHHBBH4s4s', ipheader)
    print unpack('!HHLLBBHHH', tcpheader)
    
    #print binascii.hexlify(tcpheader)

    ipchecksum = self.checksum(ipheader + tcpheader)
    tcpchecksum = self.checksum(tcpheader)

    ipheader = ip_header(checksum=ipchecksum, src_adr=self.src_addr, dest_adr=self.dest_addr).to_struct()
    tcpheader = tcp_header(checksum=tcpchecksum, syn=1).to_struct()
    print ipchecksum
    print tcpchecksum
    print unpack('!BBHHHBBH4s4s', ipheader)
    print unpack('!HHLLBBHHH', tcpheader)
    self.connection.send(ipheader + tcpheader)

  # checksum functions needed for calculation checksum
  def checksum(self, msg):
    s = 0
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
      w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
      s = s + w
    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);
    #complement and mask to 4 byte short
    s = ~s & 0xffff
    return s


