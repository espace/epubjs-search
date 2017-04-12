from pyarabic import araby

class EpubResult(object):
    """Contains method that return results from document"""

    def __init__(self, matched_documents, query, exact_match=False):
        self.matched_documents = matched_documents
        self.query = query
        self.exact_match = exact_match
        if not exact_match:
            self.normalize_query()

    def normalize_query(self):
        self.query = araby.strip_tashkeel(self.query) # remove tashkel
        self.query = araby.strip_tatweel(self.query) # remove tatweel

    def match_with_xpath(self, document_path):
        if self.exact_match:
            xpath = './/*[text()[contains(normalize-space(.),"' + self.query + '")]]'
        else:
            xpath = u'.//*[text()[contains(translate(normalize-space(.),"ًٌٍَُِّْـ",""),"'+ q_without_tashkel +'")]]'
        tree = etree.parse(open(document_path))
        matchedList = tree.xpath(xpath)

    def get_all_occurences_results_in_element(self, result_base, matched_element):
        word_all_text = "".join(matched_element.itertext())
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

    def get_results(self):
        return_json = {}
        return_json["results"] = []
        return_json["matched_words"] = set()

        for document in self.matched_documents:
            matched_elements = self.match_with_xpath(document['path'])
            for matched_element in matched_elements:
                result_base = {'title': document['title'], 'href':  document['href'], 'baseCfi': document['cfiBase'] + "!"}
                all_occurrences_in_element = get_all_occurences_results_in_element(result_base, matched_element)

            result = self.prepare_results(q, matchedList, hit, exact_match)
            return_json["matched_words"]  = return_json["matched_words"]  | result['matched_words']
            return_json["results"].extend(result['results'])

        return_json['matched_words'] = list(return_json['matched_words'])
        return_json['results'] = sorted(return_json['results'], key=lambda x: getCFIChapter(x['baseCfi']))





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
