# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

import os

version = '1.3.2.dev0'
long_description = (
    open("README.rst").read() + "\n" +
    open(os.path.join("docs", "INSTALL.rst")).read() + "\n" +
    open(os.path.join("docs", "CREDITS.rst")).read() + "\n" +
    open(os.path.join("docs", "HISTORY.rst")).read()
)

setup(name='collective.polls',
      version=version,
      description="A content type, workflow, and portlet for conducting "
                  "online polls, for anonymous and logged-in users.",
      long_description=long_description,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
          "Programming Language :: JavaScript",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Office/Business :: News/Diary",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='plone dexterity polls',
      author='Franco Pellegrini',
      author_email='frapell@ravvit.net',
      url='https://github.com/collective/collective.polls',
      license='GPLv2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.z3cform.widgets>=1.0b3',
          'Pillow',
          'plone.app.dexterity [grok,relations]',
          'plone.app.referenceablebehavior',
          'plone.directives.dexterity',
          'Products.CMFPlone>=4.1',
          'setuptools',
          'zope.component',
          'zope.interface',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'plone.testing',
              'robotframework-selenium2library',
              'robotsuite',
              'unittest2',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
