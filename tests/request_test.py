from cherrypy.test.webtest import *

class RequestTest(WebCase):
  HOST = '127.0.0.1'
  PORT = 3000
  
  def test_get(self):
    self.getPage('/')
    self.assertBody("index")
  
  def test_get_with_url_params(self):
    self.getPage('/hello/world')
    self.assertBody("Hello, world!")
  
  def test_get_form(self):
    self.getPage('/hello')
    self.assertInBody('<form action="/hello" method="post">')
  
  def test_post_form(self):
    name = 'james'
    self.getPage('/hello', method='POST', body='name=%s' % name)
    self.assertBody("Hello, %s!" % name)
  
