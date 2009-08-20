from cherrypy.test.webtest import *

class RequestTest(WebCase):
    HOST = '127.0.0.1'
    PORT = 3000
    
    def test_get(self):
        self.getPage('/')
        self.assertStatus(200)
        self.assertBody("index")
    
    def test_get_with_url_params(self):
        self.getPage('/hello/world')
        self.assertStatus(200)
        self.assertBody("Hello, world!")
    
