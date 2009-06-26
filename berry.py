import sys
import re
import inspect
import paste.httpserver
import paste.request

def start(host='127.0.0.1', port=4567):
  try:
    serve(host, str(port))
  except KeyboardInterrupt:
    sys.exit()

def serve(host, port):
  paste.httpserver.serve(handle_request, host=host, port=port)

def handle_request(env, start_response):
  request = Request(env, start_response)
  route, params = dispatch(request)
  if not route:
    return ErrorHandler(request, NotFound).error()
  
  urlparams = {}
  argnames = inspect.getargspec(route.handler)[0]
  for i, param in enumerate(params):
    urlparams[argnames[i]] = params[i]
  request.params.update(urlparams)
  
  try:
    output = route.handler(**dict(request.params))
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
  pass

class NotFound(HTTPError):
  status = 404

class AppError(HTTPError):
  status = 500

class Redirect(HTTPError):
  status = 303
  
  def __init__(self, url):
    self.url = url
  

class ErrorHandler(object):
  
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
    self.request.start_response('404 Not Found',
      [('Content-type', 'text/plain')])
    return 'Not Found'
  
  def error_500(self):
    self.request.start_response('500 Internal Server Error',
      [('Content-type', 'text/plain')])
    return 'Internal Server Error'
  
  def error_303(self):
    self.request.start_response('303 See Other',
      [('Content-type', 'text/plain'), ('Location', self.exception.url)])
    return ''
  

class Request(object):
  
  def __init__(self, env, start_response):
    self.env = env
    self.start_response = start_response
    
    self.path = self.env.get('PATH_INFO', '').lstrip('/')
    self.method = self.env.get('REQUEST_METHOD', 'GET').upper()
    self.query = self.env.get('QUERY_STRING', '')
    self.params = paste.request.parse_formvars(self.env)
  

def dispatch(request):
  for route in routes:
    if route.method == request.method:
      match = re.search(route.path, request.path)
      if match is not None:
        return route, list(match.groups())
  return None, []

routes = []

def get(path):
  
  def register(handler):
    route = Route(path, handler, 'GET')
    if path not in [r.path for r in routes]:
      routes.append(route)
    return handler
  return register

def post(path):
  
  def register(handler):
    route = Route(path, handler, 'POST')
    if path not in [r.path for r in routes]:
      routes.append(route)
    return handler
  return register

class Route(object):
  
  def __init__(self, path, handler=None, method='GET'):
    path = path.lstrip('/')
    self.path = path
    self.handler = handler
    self.method = method.upper()
  
  def __repr__(self):
    return "<Route: %s '%s' -> %s>" % (self.method, self.path, self.handler.__name__)
  
