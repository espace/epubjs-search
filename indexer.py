#!/usr/bin/python

"""WARNING:  Script is in beta and needs to be tested thoroughly.

The script generates a rudimentary appcache file based upon the content.opf file located in either:
an uncompressed epub directory or a compressed epub file and places it in the current directory

Usage: acm_gen.py --input='/path/to/content.opf' which links to the uncompressed epub directory that includes the content.opf
OR     --input='/path/to/book.epub' which links to the compressed epub file
"""

__author__ = 'Futurepress'
__email__ = 'luis@berkeley.edu'

import xml.etree.ElementTree as ET
import zipfile
import datetime
from optparse import OptionParser

from epubsearch import EpubParser
from epubsearch import EpubIndexer

def get_parameters():
    """
    Parse the user input
    """
    parser = OptionParser()
    parser.add_option('-p', '--path', dest='path', help='Path to the epub unzipped folder')
    parser.add_option('-i', '--bookid', dest='book_id', help='Unique Name for book')
    (options, args) = parser.parse_args()

    # code block to check for empty path, needed? path that includes proper filename, then valid file check
    if not options.path:
        options.path = "moby-dick"

    if not options.book_id:
        options.book_id = "moby-dick"

    return {'book_id': options.book_id, 'path': options.path}


def main():
    # get user defined parameters
    userParams  = get_parameters()
    folder_path = userParams['path']
    book_id = userParams['book_id']
    epub        = EpubParser(folder_path)

    index = EpubIndexer('whoosh', book_id)
    index.load(epub)

    print 'Done!'

if __name__ == '__main__':
    main()
