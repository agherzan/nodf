#!/usr/bin/env python

from nodf import nodfmeta
from setuptools import setup, find_packages

# Get requirements
f = open('requirements.txt', 'r')
lines = f.readlines()
requirements = [l.strip().strip('\n') for l in lines if l.strip() and not l.strip().startswith('#')]

# Get readme to be used for long description
readme = open('README.md').read()

setup(name=nodfmeta.title,
      version=nodfmeta.version,
      description=nodfmeta.description,
      long_description=readme,
      platforms=['linux'],
      author=nodfmeta.author,
      author_email=nodfmeta.author_email,
      url=nodfmeta.url,
      license=nodfmeta.license,
      install_requires=requirements,
      include_package_data=True,
      zip_safe=False,
      packages=find_packages(),
      entry_points={ 'console_scripts': [ '%s = nodf.client:main' % nodfmeta.title ] },
     )
