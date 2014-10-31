import socket

class TCPClient():

  def send(self, request):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = socket.gethostbyname(request['domain'])
    s.connect((ip, 80))
    s.send(request['get_request'])
    response = ""
    while True:
      resp = s.recv(1024)
      if resp == "": break
      response += resp
    s.close()
    return response
