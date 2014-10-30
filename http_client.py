from urlparse import urlparse
from rqst import Connection

def run(url):
  parsed = urlparse(url)
  print 'fetching ' + url
  request = build_request(parsed)
  conn = Connection()
  conn.new_basic_connection(parsed.netloc)
  conn.connect()
  conn.send(request)
  response = conn.recv()
  status = response[0].split(' ')[1]
  if status != '200':
    print 'An error occurred and recieved an http status of ' + status


def build_request(url):
  method = "GET"
  http_version = "HTTP/1.1"
  path = url.path
  host = url.netloc
  return method + " " + path + " " + http_version + "\r\n" + "Host: " + host + "\r\n\r\n" 