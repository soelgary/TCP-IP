import socket, time, binascii, datetime, random

from rqst.ip import ip_header
from rqst.connection import TCP_Connection
from rqst.tcp import tcp_header
from rqst.packet import Packet

from struct import *

class bcolors:
    '''
    This class is used for debugging purposes to get pretty colors for printing
    '''
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
  '''
  This class is used to send and receive data reliably
  '''
  def __init__(self, destination, port, data):
    '''
    initialize all of the variable
    '''
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
    '''
    This method performs the tcp handshake.
    Once the handshake is complete, it sends the request with the data
    '''
    #bcolors.cprint("attempting handshake with %s %s" % (self.src_addr, self.dest_addr))

    #bcolors.cprint("sending syn packet")
    # what if the syn is dropped?
    self.send_syn()

    #bcolors.cprint("attempting to recieve syn ack")
    syn_ack_packet = self.recv_data()

    if syn_ack_packet == None:
      print "timeout"
      exit()
    self.next_seqn = syn_ack_packet.tcp_header.seqn + 1
    self.seqn_offset = self.next_seqn - 1
    self.last_len = 0

    #bcolors.cprint("recieved")

    self.seqn_counter = syn_ack_packet.tcp_header.ackn

    #bcolors.cprint('sending ack')
    self.send_ack(syn_ack_packet)

    #bcolors.cprint('sending data')
    self.send_data(syn_ack_packet.tcp_header.window)

  def received_all_seqn(self, fin_packet):
    '''
    This is a helper method to see if all sequence numbers have been received
    '''
    if fin_packet == None:
      return False
    return fin_packet.tcp_header.seqn == self.next_seqn - self.last_len

  def calculate_next_seqn(self, packet):
    '''
    This is a helper method to calculate the next sequence number that should be coming in
    '''
    if self.next_seqn == packet.tcp_header.seqn:
      self.last_len = len(packet.tcp_header.payload)
      next = self.next_seqn + len(packet.tcp_header.payload)
      while True:
        if next in self.data and len(self.data[next]) > 0:
          #yprint self.data
          next += len(self.data[next])
        else:
          return next
    else:
      return self.next_seqn

  def get_data(self):
    '''
    This method recieves data and stores the data with each packet.
    After it has received all of the sequence numbers, it reorders the
    data and returns it
    '''
    data = ""
    received_fin = False
    fin_packet = None
    while True:
      packet = self.recv_data()
      if packet == None:
        print "BAD PACKET"
        continue
      self.data[packet.tcp_header.seqn] = packet.tcp_header.payload
      self.next_seqn = self.calculate_next_seqn(packet)
      if packet.tcp_header.fin:
        received_fin = True
        fin_packet = packet
        start = True
        next_seq = 0
        for k, v in sorted(self.data.items()):
          if start:
            next_seq = k + len(v)
            start = False
          else:
            if k == next_seq:
              next_seq += len(v)

      if (received_fin or packet.tcp_header.fin) and self.received_all_seqn(fin_packet):
        self.send_fin_ack(packet)
        data = ""
        for seq, data_part in sorted(self.data.items()):
          data += data_part
        return data
      else:
        self.send_ack(packet)
        

  def recv_data(self):
    '''
    receives the next packet incoming from the server to the correct port
    '''
    start = time.time()
    time.clock()
    elapsed = 0
    while elapsed < 180:
      elapsed = time.time() - start
      rec_packet = self.rsocket.recvfrom(65565)
      rec_packet = Packet(data=rec_packet)
      if rec_packet.ip_header.src_adr == self.dest_addr and rec_packet.tcp_header.dstp == self.incoming_port:
        # recieved reset packet
        if rec_packet.tcp_header.rst == 1:
            #bcolors.wprint("Recieved reset flag, something done goofed, i think this is because the local port is closed")
            return None
        return rec_packet


  def send_data(self,window_size):
    '''
    sends data to the server
    '''
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr,
            seqn=self.seqn_counter, payload=self.request, srcp=self.incoming_port, window=window_size, psh=1, ack=1, ackn=self.temp_ackn)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    #self.connection.send(pp)
    self.sock.sendto(pp, (self.dest_addr, 0))

  def send_ack(self, packet):
    '''
    sends an ACK to the server for the given packet 
    '''
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
    '''
    sends a SYN to the server
    '''
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr, syn=1,seqn=self.seqn_counter, srcp=self.incoming_port)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    #self.connection.send(pp)
    self.sock.sendto(pp, (self.dest_addr, 0))

  def send_fin_ack(self, packet_in):
    '''
    sends a SYN/ACK to the server
    '''
    tcpheader = tcp_header(src_addr=self.src_addr, dest_addr=self.dest_addr,seqn=self.seqn_counter, srcp=self.incoming_port, ack=1, ackn=packet_in.tcp_header.seqn+len(packet_in.tcp_header.payload)+1, fin=1)
    p = Packet()
    p.tcp_header = tcpheader
    p.ip_header = self.ipheader
    pp = p.construct()
    #self.connection.send(pp)
    self.sock.sendto(pp, (self.dest_addr, 0))

  def recv_syn_ack(self):
    '''
    receives a SYN/ACK from the server
    '''
    start = datetime.datetime.now()
    while True:
      diff = datetime.datetime.now() - start
      rec_packet = self.connection.recv()
      if rec_packet.ip_header.src_adr == self.dest_addr\
          and rec_packet.tcp_header.syn and rec_packet.tcp_header.ack:
        return rec_packet
      elif diff.total_seconds() > self.timeout:
        return None

