"""
  implements ip/tcp using raw sockets
"""
import httpclient

def parse_options(argv):
    if len(argv) < 2:
        raise Exception("invalid arguments")
    else:
        return argv[1]


def run(argv):
    url = parse_options(argv)
    httpclient.httpget(url)

