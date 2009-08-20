from test import *

class RequestTest(BerryTest):
  
  def test_get(self):
    self.getPage('/')
    self.assertBody("index")
  
  def test_get_with_url_params(self):
    self.getPage('/hello/world')
    self.assertBody("Hello, world!")
  
