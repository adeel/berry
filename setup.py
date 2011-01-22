from setuptools import setup

desc = open('README').read()

setup(
  name='berry',
  version='0.3',
  description="a minimal DSL for building a WSGI app",
  long_description=desc,
  url='http://soundofemptiness.com/projects/berry',
  author='Adeel Ahmad Khan',
  author_email='adeel2@umbc.edu',
  py_modules=['berry'],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
  ],
)