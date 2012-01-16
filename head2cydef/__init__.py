from __future__ import with_statement

import inspect
import os

from head2cydef import CFileParser

local_path = os.path.split(inspect.getfile(inspect.currentframe() ))[0]

with open(os.path.join(local_path, 'VERSION.txt'), 'r') as f:
    __version__ = f.read().strip()
