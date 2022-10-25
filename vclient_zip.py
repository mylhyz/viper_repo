# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


from __future__ import print_function

import os
import zipfile


def Unzip(file_path, target_file):
    zip_file = zipfile.ZipFile(file_path)
    print(target_file)
    for name in zip_file.namelist():
        print(name)
        zip_file.extract(name, target_file)
    zip_file.close()
