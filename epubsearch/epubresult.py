# -*- coding: utf-8 -*-
from pyarabic import araby
from lxml import etree
import re

class EpubResult(object):
    """Used to take results from engine and return it as json with more data"""

    def __init__(self, matched_documents, query, exact_match=False):
        """
            Intiliaze EpubResult object with arguments:
            - matched_documents : documents matched through whoosh engine (Mandatory)
            - query : query used for search (Mandatory)
            - exact_match : boolean flag for exact_match (Optional, default: False)s
        """
        self.matched_documents = matched_documents
        self.query = query
        self.exact_match = exact_match
        if not exact_match:
            self.normalize_query()

    def normalize_query(self):
        """
            Normalize query string by removing diacritics (tashkel) and tatweel
        """
        self.query = araby.strip_tashkeel(self.query) # remove tashkel
        self.query = araby.strip_tatweel(self.query) # remove tatweel

    def match_with_xpath(self, document_path):
        """
            Search in matched document with xpath to get elements contains results
        """
        if self.exact_match:
            xpath = './/*[text()[contains(normalize-space(.),"' + self.query + '")]]'
        else:
            xpath = u'.//*[text()[contains(translate(normalize-space(.),"ًٌٍَُِّْـ",""),"'+ self.query +'")]]'
        tree = etree.parse(open(document_path))
        matchedList = tree.xpath(xpath)
        return matchedList

    def get_results_in_element(self, result_base, matched_element):
        """ Get all occurences inside matched element"""
        r = {}
        r['results'] = []
        r['matched_words'] = set()
        word_text = etree.tostring(matched_element, encoding="utf-8", method="text", pretty_print=True ).replace('\n', ' ')
        word_text = " ".join(word_text.split())

        if word_text is None: return r

        if self.exact_match:
            regex = u"(?<![أ-ي\d])"+ q + u"(?![أ-ي\d])(?![" + u"".join(araby.TASHKEEL) + u"][أ-ي])"
            all_occurrences = re.finditer(r'('+regex+')' , word_all_text+' ')
        else:
            generate_regex_from_query = re.sub(ur'([\u0621-\u064A])', ur'\1[\u064B-\u0652|\u0640]*', self.query)
            all_occurrences = re.finditer('('+generate_regex_from_query+')', word_text.decode('utf-8'))

        for word_match in all_occurrences:
            # copy the base
            item = result_base.copy()
            matched_word_index = ("/1:" + str(word_match.start()))
            item['cfi'] = getCFI(item['baseCfi'], matched_element) + matched_word_index
            item['xpath'] = human_xpath(matched_element)
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

    def get_results(self):
        """ Return results as JSON object"""
        result_json = {}
        result_json["results"] = []
        result_json["matched_words"] = set()

        for document in self.matched_documents:
            matched_elements = self.match_with_xpath(document['path'])
            for matched_element in matched_elements:
                result_base = {'title': document['title'], 'href':  document['href'], 'baseCfi': document['cfiBase'] + "!"}
                results = self.get_results_in_element(result_base, matched_element)
                result_json["matched_words"]  = result_json["matched_words"]  | results['matched_words']
                result_json["results"].extend(results['results'])

        result_json['matched_words'] = list(result_json['matched_words'])
        result_json['total'] = len(result_json['results'])
        result_json['results'] = sorted(result_json['results'], key=lambda x: getCFIChapter(x['baseCfi']))
        return result_json





""" Helper methods to get information from results """
def human_xpath(element):
    full_xpath = element.getroottree().getpath(element)
    xpath = ''
    human_xpath = ''
    for i, node in enumerate(full_xpath.split('/')[1:]):
        xpath += '/' + node
        element = element.xpath(xpath)[0]
        namespace, tag = element.tag[1:].split('}', 1)
        if element.getparent() is not None:
            nsmap = {'ns': namespace}
            same_name = element.getparent().xpath('./ns:' + tag, namespaces=nsmap)
            if len(same_name) > 1:
                tag += '[{}]'.format(same_name.index(element) + 1)
        human_xpath += '/' + tag
    return human_xpath


def getCFI(cfiBase, word):
    cfi_list = []
    parent = word.getparent()
    child = word
    while parent is not None:
        i = parent.index(child)
        if 'id' in child.attrib:
            cfi_list.insert(0,str((i+1)*2)+'[' + child.attrib['id'] + ']')
        else:
            cfi_list.insert(0,str((i+1)*2))
        child = parent
        parent = child.getparent()

    cfi = cfiBase + '/' + '/'.join(cfi_list)
    return cfi

def getCFIChapter(cfiBase):
    cfiBase = re.sub(r'\[.*\]','',cfiBase)
    chapter_location = cfiBase[cfiBase.rfind('/')+1:cfiBase.find('!')]
    return int(chapter_location)

def createHighlight(text, start_index, end_index):
    tag = "<b class='match'>"
    closetag = "</b>"
    leading_text = trimLength(text[:start_index],-10) + tag
    word = text[start_index:end_index]
    ending_text = closetag + trimLength(text[end_index:],10)
    return leading_text + word + endWithPeriods(ending_text)

def trimLength(text, words):
    if words > 0:
        text_list = text.split(' ')[:words]
    else:
        text_list = text.split(' ')[words:]

    return ' '.join(text_list)

def endWithPeriods(text):
    if text[-1] not in '!?.':
        return text + ' ...'
    else:
        return text
