import os
import re
import inspect
import cherrypy

_url_prefix = ''

def start(root=None, port=4567, url_prefix='', env='development', 
      sessions=True, dispatcher=None):
  cherrypy.config.update({'server.socket_host': '127.0.0.1',
              'server.socket_port': port})
  
  global _url_prefix
  _url_prefix = url_prefix
  
  if env == 'development':
    cherrypy.config.update({'log.screen': True,
                'request.show_tracebacks': True})
  elif env == 'production':
    cherrypy.config.update({'request.show_tracebacks': False})
  cherrypy.config.update({'server.environment': env})

  if sessions:
    cherrypy.config.update({'tools.sessions.on': True,
                'tools.sessions.timeout': 360})
  
  app_config = {}
  app_config['/'] = {}

  static_root = os.path.dirname(os.path.abspath(__file__))
  app_config['/'].update({'tools.staticdir.root': static_root})
  app_config['/static'] = {'tools.staticdir.on': True,
               'tools.staticdir.dir': 'static'}
  
  if not dispatcher:
    dispatcher = BerryDispatcher()
  app_config['/'].update({'request.dispatch': dispatcher})
  
  if not root:
    class Root: pass
    root = Root()
  cherrypy.quickstart(root, config=app_config)

# dispatching

urls = []

class BerryDispatcher():
  
  def __init__(self):
    global urls
    self.urls = urls
  
  def __call__(self, path_info):
    request = cherrypy.request
    resource, params = self.find_handler(path_info)
    if resource:
      # Set Allow header
      avail = [m for m in dir(resource) if m.isupper()]
      if "GET" in avail and "HEAD" not in avail:
        avail.append("HEAD")
      avail.sort()
      cherrypy.response.headers['Allow'] = ", ".join(avail)
    
      # Find the subhandler
      meth = request.method.upper()
      func = getattr(resource, meth, None)
      if func is None and meth == "HEAD":
        func = getattr(resource, "GET", None)
      if func:
        request.handler = cherrypy.dispatch.LateParamPageHandler(func)
        paramdict = {}
        argnames = inspect.getargspec(func)[0]
        for i, param in enumerate(params):
          paramdict[argnames[i]] = params[i]
        cherrypy.request.params.update(paramdict)
      else:
        request.handler = cherrypy.HTTPError(405)
    else:
      request.handler = cherrypy.NotFound()

  def find_handler(self, path_info):
    cherrypy.request.config = base = cherrypy.config.copy()
    
    def merge(curpath):
      nodeconf = cherrypy.request.app.config[curpath]
      if 'tools.staticdir.dir' in nodeconf:
        nodeconf['tools.staticdir.section'] = curpath or "/"
      base.update(nodeconf)
    
    merge("/")
    merge("/static")
    
    path_info = path_info.lstrip('/')
    for route in self.urls:
      match = re.search(route.path, path_info)
      if match is not None:
        return route, match.groups()
    return None, ()


class path:
  def __init__(self, path):
    self.path = path
    global urls
    if path not in [u.path for u in urls]:
      urls.append(self)

# useful functions

def redirect(url):
  if not url.startswith('http://'):
    url = _url_prefix + url
  raise cherrypy.HTTPRedirect(url)

# views

from jinja2 import Environment, FileSystemLoader

views = Environment(loader=FileSystemLoader('views/'))

def render(filename, data={}):
  data['url_prefix'] = _url_prefix
  data['is_logged_in'] = cherrypy.session.get('is_logged_in')
  def htmlsafe(string):
    return string.encode('ascii', 'xmlcharrefreplace')
  data['htmlsafe'] = htmlsafe
  return views.get_template(filename + '.jinja').render(data)
