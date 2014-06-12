#!/usr/bin/env python

from setuptools import setup
from glob import glob

execfile('tmva2bin/info.py')

setup(name=NAME,
      version=RELEASE,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      packages=['tmva2bin',],
      scripts=glob('scripts/*'))
