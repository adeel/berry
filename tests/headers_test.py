from test import *

class HeadersTest(BerryTest):
  
  def test_content_type(self):
    self.getPage('/static/test.txt')
    self.assertBody("a text file")
    self.assertHeader('Content-Type', 'text/plain')
  
  def test_redirect_location(self):
    self.getPage('/google')
    self.assertHeader('Location', 'http://google.com')
  
