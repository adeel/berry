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

@berry.get('^dict/?$')
def dict_form(req):
  return "Hello %s!  You are %s years old." % (
    req.params.get('someone')['name'],
    req.params.get('someone')['age'])

@berry.header('Content-Type', 'text/plain')
@berry.get('^static/test\.txt$')
def txt_file(req):
  return "a text file"

@berry.get('^google/?$')
def redirect(req):
  raise berry.Redirect('http://google.com')

@berry.get('^errors/404$')
def not_found(req):
  raise berry.NotFound()

@berry.get('^errors/403$')
def forbidden(req):
  raise berry.Forbidden()

@berry.get('^errors/500$')
def app_error(req):
  return 1/0

class CustomError(berry.HTTPError):
  status = (900, 'Custom')
  content = "<h1>Custom Error</h1>"

@berry.get('^errors/900$')
def custom_error(req):
  raise CustomError()

make_server('localhost', 3000, berry.app).serve_forever()