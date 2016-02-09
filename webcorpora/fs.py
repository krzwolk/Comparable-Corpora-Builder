# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import os
import re
import logging
from werkzeug.utils import secure_filename
from codecs import open as copen

id_tmpl = '{:06d}_{}_{}_{}'
id_format = re.compile('^[^_]+_([^_])_.*$')

log = logging.getLogger(__name__)

def get_file_name(n, ph_id, ph1, ph2, n_len=6):
    """TODO: Docstring for get_file_name.

    :n: TODO
    :ph1: TODO
    :ph2: TODO
    :lang: TODO
    :n_len: TODO
    :returns: TODO

    """
    ph1 = secure_filename(ph1)[:10]
    ph2 = secure_filename(ph2)[:10]
    return id_tmpl.format(n, ph_id, ph1, ph2)

def save(path, n, ph_id, ph1, ph2, text, n_len=6):
    """TODO: Docstring for save.

    :path: TODO
    :n: TODO
    :ph_id: TODO
    :ph1: TODO
    :ph2: TODO
    :text: TODO
    :n_len: TODO
    :returns: TODO

    """
    filename = get_file_name(n, ph_id, ph1, ph2, n_len)
    filepath = os.path.join(path, filename)
    with copen(filepath, 'a', encoding='utf-8') as f:
        f.write(text)
        f.write('\n')

def rel_path(base, *args):
    """TODO: Docstring for rel_path.

    :*args: TODO
    :returns: TODO

    """
    return os.path.join(os.path.dirname(base), *args)

def texts_iter(path, swap):
    """TODO: Docstring for texts_iter.

    :path: TODO
    :returns: TODO

    """
    for name in os.listdir(path):
        file_id = id_format.match(name).group(1)
        if file_id == '1':
            try:
                with copen(os.path.join(path, name), encoding='utf-8') as f:
                    text1 = f.read()
                name = list(name)
                name[name.index('_')+1] = '2'
                name = ''.join(name)
                with copen(os.path.join(path, name), encoding='utf-8') as f:
                    text2 = f.read()
                if swap:
                    text1, text2 = text2, text1
                yield text1, text2
            except IOError:
                log.error('File doesn\'t exists: "%s"', name)

def ensure_dir_exists(path):
    """TODO: Docstring for ensure_dir_exists.

    :path: TODO
    :returns: TODO

    """
    if not os.path.exists(path):
        os.mkdir(path)
