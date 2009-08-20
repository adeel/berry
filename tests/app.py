import berry
from wsgiref.simple_server import make_server

@berry.get('^$')
def index(req):
  return "index"

@berry.get('^hello/(.+)/?$')
def hello(req, name):
  return "Hello, %s!" % name

make_server('localhost', 3000, berry.app).serve_forever()