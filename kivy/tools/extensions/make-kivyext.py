#!/usr/bin/env python
"""
    make-kivyext
    ~~~~~~~~~~~~~

    Little helper script that helps creating new Kivy extensions.
    To use it, just run it::

        python make-kivyext.py

    :copyright: (c) 2011: Adjusted by the Kivy Authors,
                    2010: Courtesy of Armin Ronacher
                          (Originally developed for flask.pocoo.org)
    :license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement
import re
import os
import sys
import getpass
from datetime import datetime
from subprocess import Popen
from urllib import quote


_sep_re = re.compile(r'[\s.,;_-]+')


FILE_HEADER_TEMPLATE = u'''\
# -*- coding: utf-8 -*-
"""
    %(module)s
    %(moduledecor)s

    Please describe your extension here...

    :copyright: (c) %(year)s by %(name)s.
"""
'''

SETUP_PY_TEMPLATE = u'''\
"""
%(name)s
%(namedecor)s

Description goes here...

"""
from setuptools import setup
from distutils.cmd import Command

from subprocess import call


class PackageBuild(Command):
    description = 'Create Extension Package'
    user_options = []

    def run(self):
        # Call this file and make a distributable .zip file that has our desired
        # folder structure
        call(['python', 'setup.py', 'install', '--root', 'output/', '--install-lib',
              '/', '--install-platlib', '/', '--install-data', '/%(extname)s/data',
              'bdist', '--formats=zip'])

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


cmdclass = {'create_package': PackageBuild}


setup(
    name='%(name)s',
    version='0.1',
    url='<enter URL here>',
    license='<specify license here>',
    author='%(author)s',
    author_email='your-email-here@example.com',
    description='<enter short description here>',
    long_description=__doc__,
    zip_safe=False,
    platforms='any',
    cmdclass=cmdclass,
    install_requires=[
        # 'Kivy'
    ],
    classifiers=[
        # Add your own classifiers here
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
'''


def prompt(name, default=None):
    prompt = name + (default and ' [%s]' % default or '')
    prompt += name.endswith('?') and ' ' or ': '
    while True:
        rv = raw_input(prompt)
        if rv:
            return rv
        if default is not None:
            return default


def prompt_bool(name, default=False):
    while True:
        rv = prompt(name + '?', default and 'Y' or 'N')
        if not rv:
            return default
        if rv.lower() in ('y', 'yes', '1', 'on', 'true', 't'):
            return True
        elif rv.lower() in ('n', 'no', '0', 'off', 'false', 'f'):
            return False


def prompt_choices(name, choices):
    while True:
        rv = prompt(name + '? - (%s)' % ', '.join(choices), choices[0])
        rv = rv.lower()
        if not rv:
            return choices[0]
        if rv in choices:
            if rv == 'none':
                return None
            else:
                return rv


def guess_package(name):
    """Guess the package name"""
    words = [x.lower() for x in _sep_re.split(name)]
    return '_'.join(words) or None


class Extension(object):

    def __init__(self, name, shortname, author, output_folder):
        self.name = name
        self.shortname = shortname
        self.author = author
        self.output_folder = output_folder

    def make_folder(self):
        root = os.path.join(self.output_folder, self.shortname)
        os.makedirs(root)
        os.mkdir(os.path.join(root, 'data'))

    def create_files(self):
        decor = '~' * len(self.shortname)
        with open(os.path.join(self.output_folder, self.shortname,
                               '__init__.py'), 'w') as f:
            f.write(FILE_HEADER_TEMPLATE % dict(
                module=self.shortname,
                moduledecor=decor,
                year=datetime.utcnow().year,
                name=self.author,
            ))
        with open(os.path.join(self.output_folder, self.shortname,
                'README'), 'w') as f:
            f.write(self.shortname + '\n' + decor
                    + '\n\nDescription goes here\n')
        with open(os.path.join(self.output_folder, 'setup.py'), 'w') as f:
            f.write(SETUP_PY_TEMPLATE % dict(
                name=self.name,
                namedecor='~' * len(self.name),
                urlname=quote(self.name),
                author=self.author,
                extname=self.shortname,
            ))


# def is_valid_ext_name(name):
#     try:
#         extname, version = name.split('_')
#         major, minor = version.split('.')
#         major, minor = int(major), int(minor)
#     except Exception, e:
#         print "The name '%s' is not a valid extension name." % name
#         return False
#     return (extname, (major, minor))


def main():
    if len(sys.argv) not in (1, 2):
        print 'usage: make-kivyext.py [output-folder]'
        return
    msg = 'Welcome to the Kivy Extension Creator Wizard'
    print msg
    print '~' * len(msg)

    name = prompt('Extension Name (human readable)')
    shortname = prompt('Extension Name (for filesystem)', guess_package(name))
    author = prompt('Author', default=getpass.getuser())

    output_folder = len(sys.argv) == 2 and sys.argv[1] or shortname + '-dev'
    while 1:
        folder = prompt('Output folder', default=output_folder)
        if os.path.isfile(folder):
            print 'Error: output folder is a file'
        elif os.path.isdir(folder) and os.listdir(folder):
            if prompt_bool('Warning: output folder is not empty. Continue'):
                break
        else:
            break
    output_folder = os.path.abspath(folder)

    ext = Extension(name, shortname, author, output_folder)
    ext.make_folder()
    ext.create_files()
    msg = '''
    Congratulations!
    Your initial Kivy extension code skeleton has been created in:
        %(output_folder)s
    The next step is to look at the files that have been created and to
    populate the placeholder values. Obviously you will also need to add the
    actual extension code.
    ''' % dict(output_folder=output_folder)
    print msg


if __name__ == '__main__':
    main()