from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

desc = open('README').read()

setup(
  name='berry',
  version='0.2',
  description="a minimal DSL for building a WSGI app",
  long_description=desc,
  url='http://soundofemptiness.com/projects/berry',
  author='Adeel Ahmad Khan',
  author_email='adeel2@umbc.edu',
  py_modules=['berry'],
  classifiers=[
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
  ],
)