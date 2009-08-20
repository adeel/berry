from test import *

class ErrorsTest(BerryTest):
  
  def test_redirect(self):
    self.getPage('/google')
    self.assertStatus(303)
  
  def test_forbidden(self):
    self.getPage('/errors/403')
    self.assertStatus(403)
  
  def test_not_found(self):
    self.getPage('/errors/404')
    self.assertStatus(404)
  
  def test_app_error(self):
    self.getPage('/errors/500')
    self.assertStatus(500)
  
  def test_custom_error(self):
    self.getPage('/errors/900')
    self.assertStatus(900)
  
