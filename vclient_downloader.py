# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


from __future__ import print_function

import os

try:
    import urllib2 as urllib
except ImportError:  # For Py3 compatibility
    import urllib.request as urllib


def Download(url, target_file):
    if os.path.exists(target_file):
        return target_file
    u = urllib.urlopen(url)
    tmp_file = target_file+'.tmp'
    with open(tmp_file, 'wb') as f:
        while True:
            buf = u.read(4096)
            if not buf:
                break
            f.write(buf)
    os.rename(tmp_file, target_file)
    return target_file
