from test import *

class RoutingTest(BerryTest):
  
  def test_route_get(self):
    self.getPage('/')
    self.assertBody("index")
  
  def test_route_get_with_url_params(self):
    self.getPage('/hello/world')
    self.assertBody("Hello, world!")
  
  def test_route_post(self):
    self.getPage('/post', method='POST')
    self.assertBody("post")
  
  def test_route_post_with_url_params(self):
    self.getPage('/hello/world', method='POST')
    self.assertBody("Hello, world!")
  
  def test_routes_are_case_insensitive(self):
    self.getPage('/HELLO/world')
    self.assertStatus(200)
  
