# -*- coding: utf-8 -*-
import importlib
import sys
import engines
from epubresult import EpubResult

class EpubIndexer(object):
    epub = False
    engine = False

    def __init__(self, engineName=False, databaseName='indexdir'):
        if engineName:
            mod = importlib.import_module("epubsearch.engines.%sengine" % engineName)
            # import whooshengine as engine
            self.engine = getattr(mod,'%sEngine' % engineName.capitalize())(databaseName)
            print self.engine

    def load(self, epub):
        self.epub = epub
        self.engine.create()

        for spineItem in epub.spine:

            path = epub.base + "/" + spineItem['href']

            self.engine.add(path=path, href=spineItem['href'], title=spineItem['title'], cfiBase=spineItem['cfiBase'], spinePos=spineItem['spinePos'])

        self.engine.finished()

    def search(self, q, limit=None, exact_match=False, with_word_source=False):
        rawresults = self.engine.query(q, limit)
        results = EpubResult(rawresults, q, exact_match, with_word_source).get_results()
        return results
