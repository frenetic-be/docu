#!/usr/bin/env python
import docu

from distutils.core import setup

setup(name='docu',
      version=docu.__version__,
      description='Python documentation module',
      long_description='''
      Python documentation module.
      Similar to PyDoc but allows customization of output.''',
      author='Julien Spronck',
      author_email='frenticb@hotmail.com',
      url='http://frenticb.com/',
      packages=['docu'],
      scripts=['bin/docu'],
      license='Free for non-commercial use',
     )