# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
from urllib2 import HTTPError
from time import sleep
from google import search
import requests
from readability.readability import Document
from html2text import HTML2Text

log = logging.getLogger(__name__)
google_delay = 20
google_big_delay = 0

def set_google_delay(delay):
    """TODO: Docstring for set_google_delay.

    :delay: TODO
    :returns: TODO

    """
    global google_delay
    google_delay = delay

def set_google_big_delay(delay):
    """TODO: Docstring for set_google_big_delay.

    :delay: TODO
    :returns: TODO

    """
    global google_big_delay
    google_big_delay = delay

def phrase_to_html(phrase, lang, n):
    """TODO: Docstring for phrase_to_html.

    :phrase: TODO
    :lang: TODO
    :n: maximal number of entries to find
    :returns: TODO

    """
    log.debug('phrase_to_html')
    is_found = False
    try:
        log.debug('phrase_to_html start search')
        for i, url in enumerate(search(phrase, lang=lang, stop=n)):
            log.debug('phrase_to_html url %s', url)
            try:
                yield requests.get(url).text
            except:
                pass
            if i % 20 == 0:
                is_found = True
                sleep(google_delay)
            if i+1 == n:
                break
        log.debug('phrase_to_html stop search')
    except HTTPError:
        log.warn('Google is not available')
        if google_big_delay:
            log.info('Sleeping %i', google_big_delay)
            sleep(google_big_delay)
    except:
        pass
    if not is_found:
        log.debug('phrase_to_html pause %i', google_delay)
        sleep(google_delay)

def phrase_to_text(phrase, lang, n):
    """TODO: Docstring for phrase_to_text.

    :phrase: TODO
    :lang: TODO
    :n: maximal number of entries to find
    :returns: TODO

    """
    log.debug('phrase_to_text')
    h = HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_emphasis = True
    for html in phrase_to_html(phrase, lang, n):
        try:
            if html is not None:
                log.debug('phrase_to_text html len %i', len(html))
            else:
                log.debug('phrase_to_html html is None')
            html = Document(html).summary()
            log.debug('phrase_to_html summary len %i', len(html))
            yield h.handle(html)
        except:
            log.debug('phrase_to_text exception')
            yield ''
