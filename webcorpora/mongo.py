# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import pymongo

def save(col, n, lang, ph1, ph2, text, n_len=6):
    """
    :n: sequential number of artice
    """
    uid = u'{}_{}_{}'.format(n, ph1, ph2)
    col.update_one(
        {
            'uid': uid,
            'lang': lang
        },
        {
            '$set':
            {
                'uid': uid,
                'lang': lang,
                'title': u'{} | {}'.format(ph1, ph2),
                'text': text
            }
        }, upsert=True)
