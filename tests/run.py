from cherrypy.test.webtest import *

tests = ('request', 'forms')

if __name__ == '__main__':
  for test in tests:
    name = '%s_test.%sTest' % (test, test.title())
    suite = ReloadingTestLoader().loadTestsFromName(name)
    
    print 'Running tests in %s...' % name
    TextTestRunner(verbosity=0).run(suite)
    print ''
