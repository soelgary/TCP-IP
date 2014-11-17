import socket, time, binascii, datetime, random

from rqst.ip import ip_header
from rqst.connection import TCP_Connection
from rqst.tcp import tcp_header
from rqst.packet import Packet

from struct import *

class bcolors:
    HEADER = '\033[95m'
    WARN = '\033[1;93m'
    END = '\033[0m'
    @staticmethod
    def cprint(data):
        print "%s%s%s" % (bcolors.HEADER, str(data), bcolors.END)
    @staticmethod
    def wprint(data):
        print "%s%s%s" % (bcolors.WARN, str(data), bcolors.END)

class TCPClient():
  def __init__(self, destination, port, data):
    self.dest_addr = destination
    self.src_addr = socket.gethostbyname(socket.gethostname()) # get local ip
    self.request = data
    self.port = port
    self.incoming_port = random.randint(2000,60000)

    #self.connection = TCP_Connection().build_connection(self.dest_addr, self.port)

    self.ipheader = ip_header(src_adr=self.src_addr, dest_adr=self.dest_addr)
    self.timeout = 5
    self.seqn_counter = random.randint(0,6000)
    self.seqn_counter_start = self.seqn_counter

    self.rsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    self.data = {}

  def do_handshake(self):
    bcolors.cprint("attempting handshake with %s %s" % (self.src_addr, self.dest_addr))

    bcolors.cprint("sending syn packet")
    # what if the syn is dropped?
    self.send_syn()

    bcolors.cprint("attempting to recieve syn ack")
    syn_ack_packet = self.recv_data()

    if syn_ack_packet == None:
      print "timeout"
      exit()

    bcolors.cprint("recieved")

    self.seqn_counter = syn_ack_packet.tcp_header.ackn

    bcolors.cprint('sending ack')
    self.send_ack(syn_ack_packet)

    bcolors.cprint('sending data')
    self.send_data(syn_ack_packet.tcp_header.window)

  def get_data(self):
    data = ""
    while True:
      packet = self.recv_data()
      if packet == None:
        print "BAD PACKET"
        continue
      self.data[packet.tcp_header.seqn] = packet.tcp_header.payload
      if packet.tcp_header.fin:
        #print data
        self.send_fin_ack(packet)
        print "DONE"
        data = ""
        for seq, data_part in sorted(self.data.items()):
          data += data_part
        return data
      else:
        self.send_ack(packet)
        

  def recv_data(self):
    start = datetime.datetime.now()

    start = time.time()
    time.clock()
    elapsed = 0
    
    while elapsed < 180:
      elapsed = time.time() - start
      #diff = datetime.datetime.now() - start
      rec_packet = self.rsocket.recvfrom(65565)
      rec_packet = Packet(data=rec_packet)
      if rec_packet.ip_header.src_adr == self.dest_addr:

        #print rec_packet

        # recieved reset packet
        if rec_packet.tcp_header.rst == 1:
            bcolors.wprint("Recieved reset flag, something done goofed, i think this is because the local port is closed")
            return None
        return rec_packet


  def send_data(self,window_size):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr,
            seqn=self.seqn_counter, payload=self.request, srcp=self.incoming_port, window=window_size, psh=1, ack=1, ackn=self.temp_ackn)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    #self.connection.send(pp)
    self.sock.sendto(pp, (self.dest_addr, 0))

  def send_ack(self, packet):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr,
            ack=1, seqn=packet.tcp_header.ackn, ackn=packet.tcp_header.seqn+1, srcp=self.incoming_port, window=packet.tcp_header.window)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    #self.connection.send(pp)
    self.sock.sendto(pp, (self.dest_addr, 0))
    self.temp_ackn = packet.tcp_header.seqn+1

  def send_syn(self):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, syn=1,seqn=self.seqn_counter, srcp=self.incoming_port)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    #self.connection.send(pp)
    self.sock.sendto(pp, (self.dest_addr, 0))

  def send_fin_ack(self, packet_in):
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr,seqn=self.seqn_counter, srcp=self.incoming_port, ack=1, ackn=packet_in.tcp_header.seqn+len(packet_in.tcp_header.payload)+1, fin=1)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    #self.connection.send(pp)
    self.sock.sendto(pp, (self.dest_addr, 0))

  def recv_syn_ack(self):
    start = datetime.datetime.now()
    while True:
      diff = datetime.datetime.now() - start
      rec_packet = self.connection.recv()
      if rec_packet.ip_header.src_adr == self.dest_addr\
          and rec_packet.tcp_header.syn and rec_packet.tcp_header.ack:
        return rec_packet
      elif diff.total_seconds() > self.timeout:
        return None

