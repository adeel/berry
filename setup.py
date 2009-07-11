from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

desc = open('README').read()

setup(name='berry',
      version='0.11',
      description="a minimalist web framework",
      long_description=desc,
      url='http://adeel.github.com/berry',
      author='Adeel Ahmad Khan',
      author_email='adeel2@umbc.edu',
      py_modules=['berry'],
      include_package_data=True,
      data_files=[('', ['README'])],
      install_requires=['Paste'],
)