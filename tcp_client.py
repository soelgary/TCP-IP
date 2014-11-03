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
    self.send_ack(self.rec_syn_ack())
    # done. now send all the datas

  def send(self, packet):
    self.connection.send(packet)

  def send_syn(self):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, syn=1).to_struct()
    packet = self.ipheader + tcpheader
    self.send(packet)

  def send_ack(self, packet):
    pass

  def rec_syn_ack(self):
    received_syn_ack = False
    while not received_syn_ack:
      packet = self.connection.recv()
      ack = packet.tcp_header.ack 
      syn = packet.tcp_header.syn
      if syn and ack:
        return packet

