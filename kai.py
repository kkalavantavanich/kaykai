# -*- coding: utf-8 -*-
"""
kai - verification bot

kai will verify the migration whether it is done correctly. 
It accomplishes this by checking the data in the new webpage <table> 
against the data in the old webpage <table>.
Webscraping is done via requests and lxml.

The new webpage fetches the next page url via url joining the current url
to the new url. The old webpage fetches the next page url via passing a 
parameter to the base url. The new webpage contains 10 <tr> elements / records 
per page while the old webpage contains 15 <tr> elements / records per page.

Confidential elements are marked with 'xxx'.

Created on Fri Jun 30 13:44:00 2017

@author: Kris
"""

## Hungarian notation ##
# n == New Table Page
# o == Old Table Page

try:
    from urlparse import urljoin # Python2
except ImportError:
    from urllib.parse import urljoin # Python3

from lxml import html
import requests

def textFromList(l):
    if (len(l) is 0):
        return ""
    else:
        return l[0]

## RECORD DTO ##

class Record:
    def __init__(self, id, date, title, owner, filelink, filesize):
        self.id = id
        self.date = date
        self.title = title
        self.owner = owner
        self.filelink = filelink
        self.filesize = filesize

    def __str__(self):
        return   "id       :" + self.id + \
               "\ndate     :" + self.date + \
               "\ntitle    :" + self.title + \
               "\nfilelink :" + self.filelink + \
               "\nfilesize :" + self.filesize

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.id == other.id and self.date == other.date and \
                self.title == other.title)
        return False

## NEW PAGE ##

# initial link of the webpage -- the first page (new urls will be joined with this url)
init_link_new = 'xxx'

class NewPageProcessor:
    n_xpath_get_rows = 'xxx/tr'                    # data table rows excluding header
    n_xpath_get_next_link = 'xxx/span/a/@href'     # relative url of the next page
    n_xpath_get_prev_link = 'xxx/span/a/@href'     # relative url of the previous page

    next_link = ""                                 # the url of the next page
    this_link = ""                                 # the url of the current page
    prev_link = ""                                 # the url of the previous page

    current_page = 1                               # start at 1
    current_index = 0                              # start at 0, end at 9
    max_index = 9                                  # the max index of a record in a page

    records = None                                 # list of Record of a page
            
    def __init__(self, initial_link):
        self.this_link = initial_link
        self.loadPage(self.this_link)

    def loadPage(self, url):
        
        print("[DEBUG] N_THIS_URL: " + url)
        print()
        nPage = requests.get(url)
        nTree = html.fromstring(nPage.text)

        # self.this_link = url

        self.records = nTree.xpath(self.n_xpath_get_rows)
        self.next_link = textFromList(nTree.xpath(self.n_xpath_get_next_link))
        if (self.next_link == ""):
            print("[WARN ] next_link is unclickable, probably on last page")
       
        self.prev_link = textFromList(nTree.xpath(self.n_xpath_get_prev_link))
        if (self.prev_link == ""):
            print("[WARN ] prev_link is unclickable, probably on first page")

    def getNextPageUrl(self):
        return urljoin(self.this_link, self.next_link)

    def getNextRecord(self):
        if (self.current_index == self.max_index):
            self.current_index = 0
            self.current_page = self.current_page + 1
            url = self.getNextPageUrl()
            print(url)
            self.loadPage(url)
        else:
            self.current_index = self.current_index + 1

        tds = self.records[self.current_index].xpath('td')
        id       = textFromList(tds[0].xpath('text()'))
        date     = textFromList(tds[1].xpath('text()'))
        title    = textFromList(tds[2].xpath('text()'))
        owner    = textFromList(tds[3].xpath('text()'))
        filelink = textFromList(tds[4].xpath('a/@href'))
        filesize = textFromList(tds[4].xpath('a/div/text()')).replace(" size : ","")
        r = Record(id, date, title, owner, filelink, filesize)
        return r

## OLD PAGE ##

# base_link_old = 'xxx/page='

class OldPageProcessor: 
    n_xpath_get_rows = 'xxx/tr[position()>1]'     # xpath command to get all rows
    
    this_link = ""                                # the current url
    base_link = ""                                # constant base url which page numbers will be appended to
    
    current_page = 1                              # start at 1
    current_index = 0                             # start at 0, end at 14
    max_index = 14                                # max record index per page

    records = None
            
    def __init__(self, base_link):
        self.base_link = base_link
        self.this_link = base_link + "1"
        self.loadPage(self.this_link)

    def loadPage(self, url):
        print("[DEBUG] O_THIS_URL: " + url)
        print()
        nPage = requests.get(url)
        nTree = html.fromstring(nPage.text)

        self.records = nTree.xpath(self.n_xpath_get_rows)
        this_link = url

    def getNextPageUrl(self):
        return self.base_link + str(self.current_page + 1)

    def getNextRecord(self):
        if (self.current_index == self.max_index):
            self.current_index = 0
            self.current_page = self.current_page + 1
            url = self.getNextPageUrl()
            print(url)
            self.loadPage(url)
        else:
            self.current_index = self.current_index + 1

        id_date_script_frags = textFromList(self.records[self.current_index].xpath('./td[1]/script/text()')).replace("\n", "").split("'")
        idanddate = id_date_script_frags[3].split(" date: ")
        if (len(idanddate) < 2):
            return None #TODO
        id       = idanddate[0]
        date     = idanddate[1]
        
        title_script_frags = textFromList(self.records[self.current_index].xpath('./td[2]/script/text()')).replace("\n", "").replace("  ", " ").split("'")
        t = title_script_frags[5]
        title = t[t.find(">") + 1:t.rfind("<")]
        owner    = ""
        filelink = textFromList(self.records[self.current_index].xpath('./td[3]/a/@href'))
        filesize = ""
        r = Record(id, date, title, owner, filelink, filesize)
        return r

## SCRIPT ##

oldPage = OldPageProcessor(base_link_old)
newPage = NewPageProcessor(init_link_new)
on = oldPage.getNextRecord
nn = newPage.getNextRecord
ro = on()
rn = nn()
i = 0

# old website contains more records -- use this to offset
while(ro != rn):
    ro = on()
    i = i + 1
    print("i=", i)
print("======= FOUND MATCH =======")

while(True):
    # TODO: no stopping mechanism implemented
    ro = on()
    rn = nn()
    i = i + 1
    if (rn == ro):
        print("MATCH i=", i)
    else:
        print("NO MATCH i=", i)
        print("OLD")
        print(ro)
        print("NEW")
        print(rn)
        
print("======= FINISHED =======")
