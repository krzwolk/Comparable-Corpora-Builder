# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import sys
import os
import re
from argparse import ArgumentParser
import pymongo
from codecs import open as copen

id_re = re.compile(r'(\d+_)(\d){1}(.*)')

def get_conf():
    """TODO: Docstring for get_conf.
    :returns: TODO

    """
    parser = ArgumentParser(description='Copies text from files to "disk" collection of "corpora" db in Mongo')
    parser.add_argument('--lang1', required=True)
    parser.add_argument('--lang2', required=True)
    parser.add_argument('source')
    return parser.parse_args()

if __name__ == '__main__':

    conf = get_conf()
    paths = os.listdir(conf.source)
    paths = [os.path.join(conf.source, p) for p in paths]
    paths = [p for p in paths if os.path.isfile(p)]
    path_map = {}
    for path in paths:
        match = id_re.match(os.path.basename(path)).group(1,2,3)
        if match and match[1] == '1':
            path2 = os.path.join(conf.source, match[0] + '2' + match[2])
            if os.path.exists(path2):
                path_map[path] = path2
    print('Articles found %s' % len(path_map))
    print('Saving articles to "disk" collection of "corpora" db')
    col = pymongo.MongoClient().corpora.disk
    col.create_index('uid')
    col.create_index('lang')
    col.create_index('done_align')
    col.create_index([('uid', pymongo.ASCENDING),
                      ('lang', pymongo.ASCENDING)])
    for i, (path1, path2) in enumerate(path_map.iteritems()):
        try:
            with copen(path1, encoding='utf-8') as f:
                text1 = f.read()
            with copen(path2, encoding='utf-8') as f:
                text2 = f.read()
        except UnicodeDecodeError:
            continue
        uid1 = os.path.basename(path1)
        uid2 = os.path.basename(path2)
        col.update_one(
            {
                'uid': uid1,
                'lang': conf.lang1
            },
            {
                '$set':
                {
                    'uid': uid1,
                    'lang': conf.lang1,
                    'title': u'{} | {}'.format(uid1, uid2),
                    'text': text1
                }
            }, upsert=True)
        col.update_one(
            {
                'uid': uid1,
                'lang': conf.lang2
            },
            {
                '$set':
                {
                    'uid': uid1,
                    'lang': conf.lang2,
                    'title': u'{} | {}'.format(uid1, uid2),
                    'text': text2
                }
            }, upsert=True)
        if i % 10 == 0:
            print('Left %s' % (len(path_map)-i-1))
