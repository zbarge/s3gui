from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import io
import os
import sys

import s3gui

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)
    
try:
    long_description = read('README.rst', 'CHANGES.rst')
except FileNotFoundError as e:
    print("Couldn't find {}".format(e))
    long_description = "Go to github for long description."

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

        
setup(
    name='s3gui',
    version=s3gui.__version__,
    url='https://github.com/zbarge/s3gui.git',
    license='GNU Public License',
    author='Zeke Barge',
    tests_require=['pytest'],
    install_requires=['boto3',
                    'awscli'],
    cmdclass={'test': PyTest},
    author_email='zekebarge@gmail.com',
    description='AWS S3 Browser GUI Utility',
    long_description=long_description,
    packages=['s3gui'],
    keywords="Amazon Web Services, Cloud Storage",
    include_package_data=True,
    platforms='any',
    test_suite='s3gui.test.test_s3gui',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)

