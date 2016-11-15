from setuptools import setup, find_packages
import sys
import os

version = '1.0'

setup(name='slowloris',
      version=version,
      description="An implementation of SlowLoris in Python",
      classifiers=[],
      keywords='',
      author='Sygnogen',
      author_email='',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      scripts=['bin/funniest-joke'],
      entry_points={'console_scripts': ['slowloris = slowloris.__main__:main']},
      )
