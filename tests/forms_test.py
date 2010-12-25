from test import *

class FormsTest(BerryTest):
  
  def test_get_params(self):
    name = 'james'
    self.getPage('/hello?name=%s' % name)
    self.assertBody("Hello, %s!" % name)
  
  def test_post_params(self):
    name = 'james'
    self.getPage('/hello', method='POST', body='name=%s' % name)
    self.assertBody("Hello, %s!" % name)
  
  def test_empty_params(self):
    self.getPage('/hello', method='POST')
    self.assertStatus(303)
  
  def test_dict_params(self):
    name = 'james'
    age = '20'
    self.getPage('/dict?someone[name]=%s&someone[age]=%s' % (name, age))
    self.assertBody("Hello %s!  You are %s years old." % (name, age))
