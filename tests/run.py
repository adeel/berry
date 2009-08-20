from cherrypy.test.webtest import *

if __name__ == '__main__':
  suite = ReloadingTestLoader().loadTestsFromName('request_test.RequestTest')
  suite = ReloadingTestLoader().loadTestsFromName('forms_test.FormsTest')
  TextTestRunner().run(suite)
