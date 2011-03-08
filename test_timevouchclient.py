#!/usr/bin/python
# -*- coding: utf-8 -*-

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Unit testing for the timevouchclient module"""

import unittest
from hashlib import sha256

import timevouchclient

__author__ = "Kirk Strauser"
__copyright__ = "Copyright 2011, Kirk Strauser"
__credits__ = ["Kirk Strauser"]
__license__ = "MIT License"
__maintainer__ = "Kirk Strauser"
__email__ = "kirk@strauser.com"
__status__ = "Production"

class TestTimeVouchClient(unittest.TestCase):
    """Exercise the TimeVouch.com client"""
    
    secretword = 'passtest'

    def testdigest(self):
        """Check the registration of a digest"""
        results = timevouchclient.registerdigest(sha256(open('testdata', 'rb').read()).hexdigest(),
                                                 self.secretword)
        for key, value in (
            ('registered', '2011-03-08T18:42:24Z'),
            ('olddigest', True),
            ('digest', '103f381bbdf93f1ea674b35e6177f7204bdd0618054ddd65f2190e130f7f35f3')):
            self.assertEqual(results[key], value)

    def testdirectorytree(self):
        """Check the registration of an entire directory structure"""
        results = timevouchclient.registerdirectorytree('/home/kirk/projects/newtrino/Newtrino',
                                                        self.secretword)
        for key, value in (
            ('registered', '2011-03-08T22:37:33Z'),
            ('olddigest', True),
            ('digest', '7f3a7b5b0bb03081eb41c97aac6801aa20463abb5885e502f5aa2bdedb8405e7')):
            self.assertEqual(results[key], value)
    
    def testfile(self):
        """Check the registration of a named file"""
        results = timevouchclient.registerfile('testdata', self.secretword)
        for key, value in (
            ('registered', '2011-03-08T18:42:24Z'),
            ('olddigest', True),
            ('digest', '103f381bbdf93f1ea674b35e6177f7204bdd0618054ddd65f2190e130f7f35f3')):
            self.assertEqual(results[key], value)

    def teststring(self):
        """Check the registration of a string"""
        results = timevouchclient.registerstring('foo', self.secretword)
        for key, value in (
            ('registered', '2011-03-08T16:32:49Z'),
            ('olddigest', True),
            ('digest', '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae')):
            self.assertEqual(results[key], value)

if __name__ == '__main__':
    unittest.main()
