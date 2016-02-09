# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import csv
import logging
from codecs import open as copen
from itertools import islice

log = logging.getLogger(__name__)

def o_u8(path, mode='r'):
    """TODO: Docstring for o_u8.

    :path: TODO
    :mode: TODO
    :returns: TODO

    """
    return copen(path, mode, encoding='utf-8')

def encoder_iter(data):
    """TODO: Docstring for encoder_iter.

    :data: TODO
    :returns: TODO

    """
    for d in data:
        yield d.encode('utf-8')

def read_bidict(path, min_sim, skip=0):
    """Creates iterator for reading bilingual dictionary

    :path: path to dictionary file
    :min_sim: minimal similarity for phrase pairs
    :skip: number of entries to skip
    :returns: TODO

    """
    with o_u8(path) as f:
        reader = enumerate(csv.reader(encoder_iter(f)))
        for i, row in islice(reader, skip, None):

            ph1 = row[0].decode('utf-8')
            ph2 = row[1].decode('utf-8')
            sim = float(row[2])

            if sim < min_sim:
                continue

            yield i, ph1, ph2
