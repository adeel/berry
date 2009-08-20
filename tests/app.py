import berry
from wsgiref.simple_server import make_server

@berry.get('^$')
def index(req):
  return "index"

@berry.post('^post/?$')
def post(req):
  return "post"

@berry.get('^hello/(.+)/?$')
@berry.post('^hello/(.+)/?$')
def hello(req, name):
  return "Hello, %s!" % name

@berry.get('^hello/?$')
@berry.post('^hello/?$')
def hello_form(req):
  if req.params.get('name'):
    return hello(req, req.params.get('name'))
  else:
    raise berry.Redirect('/hello')

make_server('localhost', 3000, berry.app).serve_forever()