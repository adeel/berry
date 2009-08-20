from test import *

class RoutingTest(BerryTest):
  
  def test_route_get(self):
    self.getPage('/')
    self.assertBody("index")
  
  def test_route_get_with_url_params(self):
    self.getPage('/hello/world')
    self.assertBody("Hello, world!")
  
