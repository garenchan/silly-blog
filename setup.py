#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
import os

try:
    # Use setuptools if available
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

    def find_packages():
        return [
            'silly_blog',
            'silly_blog.app',
            'silly_blog.contrib',
        ]


# Check python version info
if sys.version_info < (3, 0, 0):
    raise Exception('Silly-Blog only support Python 3.0.0+')


base = os.path.abspath(os.path.dirname(__file__))
version = re.compile(r"__version__\s*=\s*'(.*?)'")


def get_package_version():
    """return package version without importing it"""
    init_file = os.path.join(base, 'silly_blog', '__init__.py')
    with open(init_file, mode='rt', encoding='utf-8') as fp:
        for line in fp:
            m = version.match(line.strip())
            if not m:
                continue
            return m.groups()[0]


def get_long_description():
    """return package's long description"""
    readme_file = os.path.join(base, 'README.md')
    with open(readme_file, mode='rt', encoding='utf-8') as fp:
        return fp.read()


def get_classifiers():
    return [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]


def get_package_data():
    """return package data"""
    return {
        'silly_blog': [
            'migrations/*',
            'migrations/versions/*',
            'instance/*',
            'tests/*',
        ]
    }


if __name__ == '__main__':
    setup(
        name='Silly-Blog',
        version=get_package_version(),
        description='A RESTful Web Application Based on Flask',
        long_description=get_long_description(),
        #long_description_content_type='text/markdown',
        author='garenchan',
        author_email='1412950785@qq.com',
        url='https://github.com/garenchan/silly-blog',
        license='http://www.apache.org/licenses/LICENSE-2.0',
        classifiers=get_classifiers(),
        packages=find_packages(),
        package_data=get_package_data(),
        install_requires=[],
    )
