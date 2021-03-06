#!/usr/bin/env python

from setuptools import setup, find_packages
 
setup (
    name='django-bpmobile',
    version='0.2',
    description='A helper application for Japanese mobile phones.',
    author='Shinya Okano',
    author_email='tokibito@gmail.com',
    url='http://bitbucket.org/tokibito/django-bpmobile/',
    license='BSD License',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Plugins',
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'uamobile',
    ],
    test_suite='tests',
)
