# -*- coding: utf-8 -*-
"""
Description: Script uses dictionary of phrase pairs to download plain text data
from websites found with google

Installation:
    This packages should be installed:
        * python-virtualenv
        * python-dev
        * libxslt1-dev
        * libxml2-dev
        * build-essential
    Command for installation:
        $ sudo apt-get install python-virtualenv python-dev libxslt1-dev libxml2-dev build-essential

    Also script requires 3rd party libraries, install it with command:
        $ bash init.sh

    Now installation is complete, but before using script now need to run command:
        $ source ve/bin/activate

Usage:
    webc.py - web crawler for downloading plain text from web

    Using web crawler.
    As a rule crawler started with command:

        $ python webc.py --dict dict.txt --lang1 pl --lang2 en

    This means webc.py takes phrases from dictionary, phrases in dictionary have
    provided languages, text saved to Mongo DB to "web" collection of "corpora"
    db.  Script remembers progress and after restart continues work from where
    it was stopped. In order to force restart of processing use "-r" key.
    Also some configuration parameters is saved in "conf/webcorpora.yaml":
        * min_phrase_probability - minimal probability value for phrases
        * results_for_phrase - number of texts to retrieve from web per each phrase
        * google_delay - delay in seconds for one google request
        * google_big_delay - this parameter helps preventing being blocked by
            google, script stops on this value in seconds if being blocked (eg.
            if google_big_delay=3600, then script will stop on 1 hour if being
            blocked, then resume work)

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s:%(process)d-%(thread)d: %(message)s', level=logging.INFO)

import signal
import os
import shelve
from time import sleep
from argparse import ArgumentParser, RawTextHelpFormatter
from multiprocessing import Pool
from itertools import chain
import yaml
import pymongo
from webcorpora.bidict import read_bidict
from webcorpora.fs import rel_path
from webcorpora.mongo import save
from webcorpora import phrase_to_text, set_google_delay, set_google_big_delay

log = logging.getLogger('webc')

def get_conf():
    """TODO: Docstring for get_conf.
    :returns: TODO

    """
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-d', '--dict', required=True, help='Path to dictionary with phrases')
    parser.add_argument('-o', '--output', default='web', help='Mongo DB collection for saving corpora')
    parser.add_argument('--lang1', required=True, help='Language of first phrase in dictionary')
    parser.add_argument('--lang2', required=True, help='Language of second phrase in dictionary')
    parser.add_argument('-r', '--restart', action='store_true', help='Restart retrieving text')
    parser.add_argument('--min-phrase-probability', default=None, help='Minimal probability value for phrase pair')
    parser.add_argument('--results-for-phrase', default=None, help='Number of results to save for each phrase')
    parser.add_argument('-t', '--threads', default=5, type=int, help='Number of threads for downloading html from websites')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    conf = parser.parse_args()

    yaml_file = rel_path(__file__, 'conf', 'webcorpora.yaml')
    with open(yaml_file) as f:
        yaml_conf = yaml.safe_load(f) or {}
    for key, val in yaml_conf.items():
        if not hasattr(conf, key) or getattr(conf, key) is None:
            setattr(conf, key, val)
    return conf

def progress_updater(state, state_id, phrases, start):
    """TODO: Docstring for progress_updater.

    :state: TODO
    :state_id: TODO
    :phrases: TODO
    :start: TODO
    :returns: TODO

    """
    log.debug('progress_updater')
    for i, ph1, ph2 in phrases:
        state[state_id] = i + 1
        yield i, ph1, ph2

def process_phrase(phrase, lang, n):
    """TODO: Docstring for process_phrase.

    :phrase: TODO
    :lang: TODO
    :n: TODO
    :returns: TODO

    """
    log.debug('process_phrase')
    for text in phrase_to_text(phrase, lang, n):
        yield text

def get_text(phrases, lang1, lang2, n):
    """TODO: Docstring for get_text.

    :phrases: TODO
    :lang1: TODO
    :lang2: TODO
    :n: TODO
    :returns: TODO

    """
    log.debug('get_text')
    for i, ph1, ph2 in phrases:
        for text in process_phrase(ph1, lang1, n):
            yield i, lang1, ph1, ph2, text
        for text in process_phrase(ph2, lang2, n):
            yield i, lang2, ph1, ph2, text

lang1 = None
lang2 = None
n = None

def init_async(l1, l2, new_n, delay, big_delay):
    global lang1
    global lang2
    global n
    lang1 = l1
    lang2 = l2
    n = new_n
    set_google_delay(delay)
    set_google_big_delay(big_delay)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def get_text_async(phrase):
    """TODO: Docstring for get_text_async.

    :phrase: TODO
    :returns: TODO

    """
    log.debug('get_text_async')
    return list(get_text([phrase], lang1, lang2, n))

if __name__ == '__main__':
    conf = get_conf()
    if conf.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger('requests').setLevel(logging.ERROR)
        logging.getLogger('urllib3').setLevel(logging.ERROR)
    state = shelve.open(rel_path(__file__, 'conf', 'state.db'))
    log.debug('State %s', state)
    log.debug('Conf %s', conf)
    state_id = os.path.abspath(conf.dict)
    skip = state.setdefault(state_id, 0)

    if conf.restart:
        skip = 0
        state[state_id] = 0

    pool = Pool(conf.threads, init_async,
                (conf.lang1, conf.lang2, conf.results_for_phrase,
                 conf.google_delay*conf.threads, conf.google_big_delay))
    data_iter = read_bidict(conf.dict, conf.min_phrase_probability, skip=skip)
    data_iter = progress_updater(state, state_id, data_iter, skip)

    db = pymongo.MongoClient().corpora
    col = db[conf.output]
    col.create_index('uid')
    col.create_index('lang')
    col.create_index('done_align')
    col.create_index([('uid', pymongo.ASCENDING),
                      ('lang', pymongo.ASCENDING)])

    try:
        log.debug('Starting crawler')
        items = enumerate(chain.from_iterable(pool.imap_unordered(get_text_async, data_iter)))
        for step, (i, lang, ph1, ph2, text) in items:
            log.debug('Phrase "%s"', (i, lang, ph1, ph2, text))
            log.debug('Step %i', step)
            save(col, i, lang, ph1, ph2, text)
            if not step % 10:
                log.info('Saved text number %i', step+1)
    except KeyboardInterrupt:
        log.info('Stopping')
        pool.terminate()
