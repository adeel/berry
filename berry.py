"Berry is a minimal DSL for building a WSGI application."

import sys
import re
import cgi
import traceback

debug = False

routes = []
middlewares = []
error_handlers = {}

def app(env, start_response):
  "The WSGI application."
  
  request = Request(env, start_response)  
  response = Response(request)
  return response.get()

class Response(object):
  
  def __init__(self, request):
    self.request = request
    self.status = None
  
  def get(self):
    route, urlparams = self.request._dispatch()
    
    if not route:
      exception = NotFound()
      status = exception.status
      handler = exception.get_handler()
    else:
      status = (200, 'OK')
      handler = route.handler
      
      try:
        content = handler(self.request, *urlparams)
      except Exception, exception:
        if not isinstance(exception, HTTPError):
          exception = AppError()
        status = exception.status
        handler = exception.get_handler()
    
    self.status = status
    
    headers = getattr(handler, 'headers', {})
    if 'Content-Type' not in headers:
      headers['Content-Type'] = 'text/html'
    
    self.request._start_response('%s %s' % status, headers.items())
    
    if status[0] == 200:
      return content
    else:
      return handler(self.request)
  

class HTTPError(Exception):
  "Base class for HTTP errors."
  
  status = (500, 'Internal Server Error')
  content = ""
  headers = {}
  
  def get_handler(self):
    code = self.status[0]
    if code in error_handlers:
      handler = error_handlers[code]
    else:
      def handler(req):
        return self.content
      handler.headers = self.headers
    
    return handler
  

class Redirect(HTTPError):
  status = (303, 'See Other')
  
  def __init__(self, url):
    self.headers = {'Location': url}
  

class Forbidden(HTTPError):
  status = (403, 'Forbidden')
  content = "<h1>403 Forbidden</h1>"

class NotFound(HTTPError):
  status = (404, 'Not Found')
  content = "<h1>404 Not Found</h1>"

class AppError(HTTPError):
  status = (500, 'Internal Server Error')
  
  def __init__(self):
    content = "<h1>500 Internal Server Error</h1>"
    
    if debug:
      exc_info = sys.exc_info()
      tb = ''.join(traceback.format_exception(*exc_info))
      content += "<pre><code>%s</code></pre>" % tb
    
    self.content = content
  

class Request(object):
  "Abstraction of the WSGI request."
  
  def __init__(self, env, start_response):
    self.env = env
    self._start_response = start_response
    
    self.path = self.env.get('PATH_INFO', '').lstrip('/')
    self.query = self.env.get('QUERY_STRING', '')
    self.fullpath = '/' + self.path
    if self.query:
      self.fullpath += '?' + self.query
    self.params = self._parse_params()
    self.method = self.env.get('REQUEST_METHOD', 'GET').upper()
  
  def _dispatch(self):
    "Dispatch the request."
    
    for route in routes:
      if route.method == self.method:
        match = re.search(route.path, self.path)
        if match is not None:
          return route, list(match.groups())
    return None, []
  
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
    
    parsed = cgi.FieldStorage(fp=self.env['wsgi.input'],
                              environ=self.env,
                              keep_blank_values=True)
    params = {}
    for key in parsed:
      val = parsed[key]
      if hasattr(val, 'filename') and val.filename:
        params[key] = val
      elif any((isinstance(val, cgi.FieldStorage),
                isinstance(val, cgi.MiniFieldStorage))):
        params[key] = val.value
      else:
        params[key] = [f.value for f in val]
    return params
  

def error(code):
  "A decorator for registering error handlers."
  
  def register(handler):
    error_handlers[code] = handler
    return handler
  return register

def header(key, value):
  "A decorator for adding headers."
  
  def register(handler):
    if not getattr(handler, 'headers', {}):
      handler.headers = {}
    handler.headers[key.title()] = value
    return handler
  return register

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
  
  def __init__(self, path, handler, method='GET'):
    path = path.lstrip('/')
    self.path = path
    self.handler = handler
    self.method = method.upper()
  
