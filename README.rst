About
=====

Script uses dictionary of phrase pairs to download plain text data from websites found with google and save them as a Quasi-Comparable Corpora. It is 100% unsupervised and language independent. To prepare a dictionary please use this script https://github.com/machinalis/yalign/blob/develop/scripts/yalign-phrasetable-csv

If you wish to mine such data for paralle data https://github.com/krzwolk/yalign is recommended because you may directly input downloaded data with corpora_to_mongo.py

Installation
=====

 This packages should be installed in Ubuntu:
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

Usage
=====

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


Final info
====

Feel free to use this tool if you cite:
•	Wołk K., Marasek K., “Unsupervised comparable corpora preparation and exploration for bi-lingual translation equivalents”, Proceedings of the 12th International Workshop on Spoken Language Translation, Da Nang, Vietnam, December 3-4, 2015, p.118-125

For more information, see: http://arxiv.org/pdf/1512.01641

For any questions:
| Krzysztof Wolk
| krzysztof@wolk.pl