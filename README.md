epubjs-search - Full Text Indexing and Retrieval for Epub Files
=============

We had a problem searching in arabic books that has diacritics, Diacritics is a special unicode charachters can be added after any arabic letter. And it will be hard to users to write the exact diacritics every time searching for a word.

So we created this fork to mainly to support arabic epub books with diacritics, To make user able to search without diacritics and get results for the query with any diacritics in it.

Whats new
---------------------
1. Using book_id in indexing for multiable books indexing
2. Add 2 options for search (exact match, search with word stem 'جذر')
3. Changes in the usage of whooshengine to make it support arabic books with diacritics
4. Return xpath for each matched element
5. Update whoosh engine to version 2.7.4
6. Using pyarabic to maniblate query and search with xpath
7. Disable debug mode for flask and Make debug mode optional


Examples
---------------------

##### 1- Normal search:

###### Request: 
```http://localhost:5000/search?q=الصفات&id=6```
###### Response:
  ```
  {
  "matched_words": [
    "الصِّفاتِ"
  ],
  "results": [
    {
      "baseCfi": "/6/4[Section0001.xhtml]!",
      "cfi": "/6/4[Section0001.xhtml]!/4/2/28/1:19",
      "highlight": "والحمدُ: الثّناءُ ب<b class='match'>الصِّفاتِ</b> الجميلةِ، والأفعالِ الحسنةِ، سواءٌ كانَ فِي مقابلةِ نعمةٍ أمْ ...",
      "href": "Text/Section0001.xhtml",
      "matched_word": "الصفات",
      "title": "مقدمة الشارح",
      "xpath": "/html/body/div/p[13]"
    },
    {
      "baseCfi": "/6/6[Section0002.xhtml]!",
      "cfi": "/6/6[Section0002.xhtml]!/4/2/100/1:74",
      "highlight": "طعمُهُ أوْ ريحُهُ)، أوْ كثيرٌ منْ صفةٍ منْ تلكَ <b class='match'>الصِّفاتِ</b> لَا يسيرٌ مِنهَا: (بطبخِ) طاهرٍ فيهِ، (أوْ) بطاهرٍ منْ ...",
      "href": "Text/Section0002.xhtml",
      "matched_word": "الصفات",
      "title": "كتاب الطهارة",
      "xpath": "/html/body/div/p[49]"
    },
    {
      "baseCfi": "/6/118[Section0057.xhtml]!",
      "cfi": "/6/118[Section0057.xhtml]!/4/2/38/1:24",
      "highlight": "ولَا يجبُ استقصاءُ كلِّ <b class='match'>الصِّفاتِ</b>؛ لأنَّهُ يتعذّرُ.",
      "href": "Text/Section0057.xhtml",
      "matched_word": "الصفات",
      "title": "",
      "xpath": "/html/body/div/p[18]"
    }
  ],
  "total": 3
}
  ```
##### 2- Exact match search

###### Request: 
``` http://localhost:5000/search?q=الصِّفاتِ&id=6&exact_match=True ```
###### Reasponse:
```
  {
  "matched_words": [
    "الصِّفاتِ"
  ],
  "results": [
    {
      "baseCfi": "/6/6[Section0002.xhtml]!",
      "cfi": "/6/6[Section0002.xhtml]!/4/2/100/1:74",
      "highlight": "طعمُهُ أوْ ريحُهُ)، أوْ كثيرٌ منْ صفةٍ منْ تلكَ <b class='match'>الصِّفاتِ</b> لَا يسيرٌ مِنهَا: (بطبخِ) طاهرٍ فيهِ، (أوْ) بطاهرٍ منْ ...",
      "href": "Text/Section0002.xhtml",
      "matched_word": "الصِّفاتِ",
      "title": "كتاب الطهارة",
      "xpath": "/html/body/div/p[49]"
    },
    {
      "baseCfi": "/6/118[Section0057.xhtml]!",
      "cfi": "/6/118[Section0057.xhtml]!/4/2/38/1:24",
      "highlight": "ولَا يجبُ استقصاءُ كلِّ <b class='match'>الصِّفاتِ</b>؛ لأنَّهُ يتعذّرُ.",
      "href": "Text/Section0057.xhtml",
      "matched_word": "الصِّفاتِ",
      "title": "",
      "xpath": "/html/body/div/p[18]"
    }
  ],
  "total": 2
}
```
##### 3- Search using word stem (جذر)

###### Request:
``` http://localhost:5000/search?q=الصِّفاتِ&id=6&with_word_stem=True ```
###### Response:
```
  {
  "matched_words": [
    "صفتُهُ",
    "بالصِّفاتِ"
  ],
  "results": [
    {
      "baseCfi": "/6/4[Section0001.xhtml]!",
      "cfi": "/6/4[Section0001.xhtml]!/4/2/28/1:18",
      "highlight": "والحمدُ: الثّناءُ <b class='match'>بالصِّفاتِ</b> الجميلةِ، والأفعالِ الحسنةِ، سواءٌ كانَ فِي مقابلةِ نعمةٍ أمْ ...",
      "href": "Text/Section0001.xhtml",
      "matched_word": "بالصِّفاتِ",
      "title": "مقدمة الشارح",
      "xpath": "/html/body/div/p[13]"
    },
    {
      "baseCfi": "/6/4[Section0001.xhtml]!",
      "cfi": "/6/4[Section0001.xhtml]!/4/2/40/1:126",
      "highlight": "ويُوصَفُ، و«أفضلَ» منصوبٌ علَى أنَّهُ بدلٌ منْ «حمدًا»، أوْ <b class='match'>صفتُهُ</b> أوْ حالٌ مِنهُ، و«مَا» موصولٌ اسميٌّ أوْ نكِرةٌ موصوفةٌ؛ ...",
      "href": "Text/Section0001.xhtml",
      "matched_word": "صفتُهُ",
      "title": "مقدمة الشارح",
      "xpath": "/html/body/div/p[19]"
    }
  ],
  "total": 2
  }
```
Engines Supported
---------------------

* [Whoosh](https://pypi.python.org/pypi/Whoosh/)
* [Cheshire3](https://github.com/cheshire3/cheshire3) 'Not tested after adding arabic support'

How To Use 
---------------------

Prerequisites :

- Python 2.7
- pip
- virtualenv

Clone the Repository :

`$ git clone https://github.com/espace/epubjs-search.git`

`$ cd epubjs-search`

Load a virtual environment for Python :

`$ virtualenv venv`

`$ source venv/bin/activate`

`$ pip install -r requirements.txt`

Add an unzipped epub to the source directory, say /your_epub/ then run:

`$ python indexer.py --path BOOK_UNZIPED_FOLDER_PATH --bookid BOOK_UNIQUE_ID`

Finally run the search api :

`$ python search.py`

Run with debug mode enabled :

`$ python search.py -d True`
