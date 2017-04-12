# -*- coding: utf-8 -*-
import importlib
import sys
import engines
from lxml import etree
import re
from pyarabic import araby

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

    def prepare_results(self, q, matchedList, hit, exact_match):
        baseitem = {}
        baseitem['title'] = hit["title"]
        baseitem['href'] = hit["href"]
        #baseitem['path'] = hit["path"]
        # find base of cfi
        cfiBase = hit['cfiBase'] + "!"
        r = {}
        r['results'] = []
        r['matched_words'] = set()
        for word in matchedList:
            word_all_text = "".join(word.itertext())
            if word_all_text is None: continue

            word_text = etree.tostring(word, encoding="utf-8", method="text", pretty_print=True ).replace('\n', ' ')
            word_text = " ".join(word_text.split())
            if exact_match:
                regex = u"(?<![أ-ي\d])"+ q + u"(?![أ-ي\d])(?![" + u"".join(araby.TASHKEEL) + u"][أ-ي])"
                all_occurrences = re.finditer(r'('+regex+')' , word_all_text+' ')
            else:
                generate_regex_from_query = re.sub(ur'([\u0621-\u064A])', ur'\1[\u064B-\u0652|\u0640]*', q)
                all_occurrences = re.finditer('('+generate_regex_from_query+')', word_text.decode('utf-8'))

            for word_match in all_occurrences:
                # copy the base
                item = baseitem.copy()
                item['baseCfi'] = cfiBase
                matched_word_index = ("/1:" + str(word_match.start()))
                item['cfi'] = getCFI(cfiBase, word) + matched_word_index
                item['xpath'] = human_xpath(word)
                # Create highlight snippet in try / except
                # because I'm not convinced its error free for all
                # epub texts
                r['matched_words'].add(word_match.group(1))
                try:
                    item['highlight'] = createHighlight(word_text.decode('utf-8'), word_match.start(), word_match.end()) # replace me with above
                except Exception as e:
                    print "Exception when creating highlight for query", q
                    print(e)
                    print word_text
                    item['highlight'] = ''

                #item['highlight'] = word.text
                r['results'].append(item)
        return r

    def search(self, q, limit=None, exact_match=False):
        rawresults = self.engine.query(q, limit)
        # print len(rawresults)
        r = {}
        r["results"] = []
        r["matched_words"] = set()
        q = q.lower()

        for hit in rawresults:

            with open(hit["path"]) as fileobj:
                tree = etree.parse(fileobj)

                if exact_match:
                    xpath = './/*[text()[contains(normalize-space(.),"' + q + '")]]'
                    matchedList = tree.xpath(xpath)
                    result = self.prepare_results(q, matchedList, hit, exact_match)
                else:
                    remove_tashkel_from_query = re.compile(ur'[\u064B-\u065f|\u0640]',re.UNICODE)
                    q_without_tashkel = remove_tashkel_from_query.sub('', q)

                    xpath = u'.//*[text()[contains(translate(normalize-space(.),"ًٌٍَُِّْـ",""),"'+ q_without_tashkel +'")]]'
                    matchedList = tree.xpath(xpath)
                    result = self.prepare_results(q, matchedList, hit, exact_match)

                r["matched_words"]  = r["matched_words"]  | result['matched_words']
                r["results"].extend(result['results'])
        ## Sort results by chapter
        r['matched_words'] = list(r['matched_words'])
        r['results'] = sorted(r['results'], key=lambda x: getCFIChapter(x['baseCfi']))
        return r
