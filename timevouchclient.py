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

"""Functions for registering and verifying files with the
TimeVouch.time free public timestamping service"""

import os
import urllib
import urllib2
from hashlib import sha256

import simplejson

__author__ = "Kirk Strauser"
__copyright__ = "Copyright 2011, Kirk Strauser"
__credits__ = ["Kirk Strauser"]
__license__ = "MIT License"
__maintainer__ = "Kirk Strauser"
__email__ = "kirk@strauser.com"
__status__ = "Production"

DIGESTCHUNKSIZE = 10 * 1024 * 1024
TIMEVOUCHURL = 'https://timevouch.com/api'

def registerdigest(digest, secretword):
    """Send the digest and secretword to TimeVouch.com. Returns either
    True or False to indicate success, and a dict of keys and values
    returned by the service"""
    postvars = {'digest': digest}
    if secretword:
        postvars['secretword'] = secretword
    data = urllib.urlencode(postvars)
    try:
        return simplejson.loads(urllib2.urlopen(TIMEVOUCHURL, data).read())
    except urllib2.HTTPError as error:
        if error.code != 400:
            raise
        raise IOError(simplejson.loads(error.read()))

def registerdirectorytree(directoryname, secretword, exitonchange=False):
    """Generate a digest of the given directory and all of its
    contents (directory names, file names, and file contents),
    recursively, then register it and return the results. Note that
    the name of the directory itself is not included in the final
    digest. This is analogous to registerfile().

    If 'exitonchange' is True, return False as soon as a new or
    changed file is detected."""

    if not os.path.exists(directoryname):
        raise IOError('No such file or directory: %s' % repr(directoryname))
    
    # Process all of the subdirectories under the given directory,
    # starting with the most deeply nested
    dirhash = {}
    results = None
    for dirname, subdirs, filenames in os.walk(directoryname, topdown=False):
        # First, add in the names of every subdirectory of this directory and their hashes
        thisdirhash = sha256('DIRS')
        for subdir in sorted(subdirs):
            subdirhash = dirhash.pop(os.path.join(dirname, subdir))
            thisdirhash.update('\0%s%s' % (subdirhash, subdir))
            
        # Next, add in every file in this directory
        thisdirhash.update('\0FILES')
        for filename in sorted(filenames):
            filepath = os.path.join(dirname, filename)
            results = registerfile(filepath, secretword)
            if results['olddigest']:
                print '%s %s' % (results['digest'], filepath)
            else:
                print '%s!%s' % (results['digest'], filepath)
                if exitonchange:
                    return False
            thisdirhash.update('\0%s%s' % (results['digest'], filename))

        # Finally, register all of the above as this directory's contents
        results = registerdigest(thisdirhash.hexdigest(), secretword)
        if results['olddigest']:
            print '%s %s/' % (results['digest'], dirname)
        else:
            print '%s!%s/' % (results['digest'], dirname)
            if exitonchange:
                return False
        dirhash[dirname] = results['digest']

    if results is None:
        raise IOError('Is not a walkable directory: %s' % repr(directoryname))
        
    return results

def registerfile(filename, secretword):
    """Create a digest of the contents of the named file and register
    it with TimeVouch.com. Only the file's contents are considered and
    not the file's name as two files with different names are still
    identical."""
    infile = open(filename, 'rb')
    hasher = sha256()
    while True:
        data = infile.read(DIGESTCHUNKSIZE)
        if not data:
            break
        hasher.update(data)
    return registerdigest(hasher.hexdigest(), secretword)

def registerstring(data, secretword):
    """Create a digest of the given string and register it with
    TimeVouch.com"""
    return registerdigest(sha256(data).hexdigest(), secretword)

if __name__ == '__main__':
    import sys
    print registerdirectorytree(sys.argv[1], 'passtest', False)
