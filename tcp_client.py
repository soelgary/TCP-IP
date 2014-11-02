import socket
from rqst import Connection, tcp_header, ip_header
import pprint
from struct import *
import binascii

class TCPClient():
  def __init__(self, destination, data):
    self.dest_addr = socket.gethostbyname(destination)
    self.src_addr = '192.168.1.218'#= socket.gethostbyname(socket.gethostname())
    self.data = data
    self.connection = Connection()
    self.ipheader = ip_header(src_adr=self.src_addr, dest_adr=self.dest_addr).to_struct()

  def do_handshake(self):
    self.connection.new_connection(self.dest_addr)
    self.connection.connect()

    tcpheader = tcp_header(self.src_addr, self.dest_addr, syn=1).to_struct()
    packet = self.ipheader + tcpheader
    self.connection.send(packet)
    self.connection.recv()

