"""
Berry is a minimal web framework written in Python.

import berry
from berry import get, redirect

@get('^$')
def index(req):
  return "HOME"

@get('^(\d+)/?$')
def test(req, id):
  return str(id)

@get('^google/?$')
def google(req):
  raise redirect('http://google.com')

berry.start()
"""

import sys
import re
import cgi
import paste.httpserver

routes = []
middlewares = []

def start(host='127.0.0.1', port=4567):
  "Start the application."
  
  try:
    serve(host, port)
  except KeyboardInterrupt:
    sys.exit()

def use(middleware, options=None):
  "Use a middleware.  (Can take options.)"
  
  middlewares.append((middleware, options))

def redirect(url):
  "Wrapper for redirecting."
  
  raise Redirect(url)

def serve(host, port):
  "Run the application using the HTTP server in Paste."
  
  app = handle_request
  for middleware, options in middlewares:
    app = middleware(app, options)
  paste.httpserver.serve(app, host=host, port=str(port))

def handle_request(env, start_response):
  "The WSGI application."
  
  request = Request(env, start_response)
  route, params = dispatch(request)
  if not route:
    return ErrorHandler(request, NotFound).error()
  
  try:
    output = route.handler(request, *params)
  except Exception, exception:
    if isinstance(exception, HTTPError):
      return ErrorHandler(request, exception).error()
    else:
      return ErrorHandler(request, AppError).error()
  
  print '200: "%s"' % request.path

  content_type = getattr(route.handler, 'content_type', 'text/html')
  start_response('200 OK', [('Content-Type', content_type)])
  
  return output

class HTTPError(Exception):
  "Base class for HTTP errors."

class NotFound(HTTPError):
  status = 404

class AppError(HTTPError):
  status = 500

class Redirect(HTTPError):
  status = 303
  
  def __init__(self, url):
    self.url = url
  

class ErrorHandler(object):
  "Handle HTTP errors."
  
  def __init__(self, request, exception):
    self.request = request
    self.exception = exception
    self.status = getattr(self.exception, 'status', 404)
    print '%s: %s' % (self.status, self.exception)
  
  def error(self):
    name = 'error_' + str(self.status)
    try:
      handler = self.__getattribute__(name)
    except:
      handler = self.error_404
    return handler()
  
  def error_404(self):
    self.request._start_response('404 Not Found',
      [('Content-type', 'text/plain')])
    return 'Not Found'
  
  def error_500(self):
    self.request._start_response('500 Internal Server Error',
      [('Content-type', 'text/plain')])
    return 'Internal Server Error'
  
  def error_303(self):
    self.request._start_response('303 See Other',
      [('Content-type', 'text/plain'), ('Location', self.exception.url)])
    return ''
  

class Request(object):
  "Abstraction of the WSGI request."
  
  def __init__(self, env, start_response):
    self.env = env
    self._start_response = start_response
    
    self.path = self.env.get('PATH_INFO', '').lstrip('/')
    self.method = self.env.get('REQUEST_METHOD', 'GET').upper()
    self.query = self.env.get('QUERY_STRING', '')
    self.params = self._parse_params()
  
  def _parse_params(self):
    "Parse all form data."
    
    params = {}
    params.update(self._parse_get_params())
    params.update(self._parse_post_params())
    return params
  
  def _parse_get_params(self):
    "Parse form data passed through GET."
    
    parsed = cgi.parse_qs(self.env['QUERY_STRING'], keep_blank_values=True)
    params = {}
    for key, val in parsed.items():
      if len(val) == 0:
        params[key] = ''
      elif len(val) == 1:
        params[key] = val[0]
      else:
        params[key] = val
    return params
  
  def _parse_post_params(self):
    "Parse form data passed through POST."
    
    parsed = cgi.FieldStorage(fp=self.env['wsgi.input'], environ=self.env,
                              keep_blank_values=True)
    params = {}
    for key in parsed:
      val = parsed[key]
      if any((isinstance(val, cgi.FieldStorage),
              isinstance(val, cgi.MiniFieldStorage))):
        params[key] = val.value
      elif val.filename:
        params[key] = val
      else:
        print val
        params[key] = [f.value for f in val]
    return params
  

def dispatch(request):
  "Dispatch the request."
  
  for route in routes:
    if route.method == request.method:
      match = re.search(route.path, request.path)
      if match is not None:
        return route, list(match.groups())
  return None, []

def get(path):
  "The decorator for GET."
  
  def register(handler):
    route = Route(path, handler, 'GET')
    if (path, 'GET') not in [(r.path, r.method) for r in routes]:
      routes.append(route)
    return handler
  return register

def post(path):
  "The decorator for POST."
  
  def register(handler):
    route = Route(path, handler, 'POST')
    if (path, 'POST') not in [(r.path, r.method) for r in routes]:
      routes.append(route)
    return handler
  return register

class Route(object):
  "Abstraction of routes."
  
  def __init__(self, path, handler=None, method='GET'):
    path = path.lstrip('/')
    self.path = path
    self.handler = handler
    self.method = method.upper()
  
