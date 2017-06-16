# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

version = '1.10b1'
long_description = (
    open('README.rst').read() + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(name='collective.polls',
      version=version,
      description="A content type, workflow, and portlet for conducting "
                  "online polls, for anonymous and logged-in users.",
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Plone',
          'Framework :: Plone :: 4.2',
          'Framework :: Plone :: 4.3',
          'Framework :: Plone :: 5.0',
          'Framework :: Plone :: 5.1',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: OS Independent',
          'Programming Language :: JavaScript',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Office/Business :: News/Diary',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='plone dexterity polls',
      author='Franco Pellegrini',
      author_email='frapell@ravvit.net',
      url='https://github.com/collective/collective.polls',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'AccessControl',
          'Acquisition',
          'plone.api',
          'plone.app.content',
          'plone.app.dexterity [relations]',
          'plone.app.portlets',
          'plone.autoform',
          'plone.dexterity',
          'plone.memoize',
          'plone.portlets',
          'plone.supermodel',
          'plone.uuid',
          'Products.CMFCore',
          'Products.CMFPlone >=4.2',
          'Products.GenericSetup',
          'setuptools',
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={
          'test': [
              'plone.app.robotframework',
              'plone.app.testing [robot] >=4.2.2',
              'plone.dexterity',
              'plone.testing',
              'robotsuite',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
