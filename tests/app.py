import berry
from wsgiref.simple_server import make_server

@berry.get('^$')
def index(req):
  return "index"

@berry.get('^hello/(.+)/?$')
def hello(req, name):
  return "Hello, %s!" % name

@berry.get('^hello/?$')
def hello_form_get(req):
  return """
    <form action="/hello" method="post">
      <input type="text" name="name" value="Name" />
      <input type="submit" />
    </form>
  """.strip()

@berry.post('^hello/?$')
def hello_form_post(req):
  if req.params.get('name'):
    return hello(req, req.params.get('name'))
  else:
    raise berry.Redirect('/hello')

make_server('localhost', 3000, berry.app).serve_forever()