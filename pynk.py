#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Biblioteka dla NK pod Pythona. W tej wersji pozwala tylko na pobieranie forów.

BY d33tah, LICENSED UNDER WTFPL.
"""

import mechanize
from lxml import html

nklink = "http://nasza-klasa.pl"

class NK_profile:
  
  def __init__(self,name,location,url,friends):
    self.name = name
    self.location = location
    self.url = url
    self.friends = friends
    
  def __repr__(self):
    return "<NK_profile: %s, %s" % (self.name,self.location)


class NK_forum_post:
  
  def __init__(self,date,contents,author):
    self.date = date
    self.contents = contents
    self.author = author
  
  def __repr__(self):
    return "<NK_forum_post: %s, %s>" % (self.date, self.author)


class NK_forum_thread:
  
  def __init__(
      self,
      title,
      url,
      started_author,
      started_time,
      posts_count,
      lastpost_summary,
      lastpost_author,
      lastpost_date):
      
    self.title = title
    self.url = url
    self.started_author = started_author
    self.started_time = started_time
    self.posts_count = posts_count
    self.lastpost_summary = lastpost_summary
    self.lastpost_author = lastpost_author
    self.lastpost_date = lastpost_date
    
  def __repr__(self):
    return "<NK_forum_thread: %s, %s>" % (self.title.encode('utf-8'), self.url)


class NK_forum:
  
  def __init__(self,url,school_name=''):
    
    self.url = url
    self.school_name = school_name
    
  def __repr(self):
    return "<NK_forum: %s>" % self.school_name

class PyNK:
  
  def __init__ (self,username,password):
    
    self.br = mechanize.Browser()
    
    user_agent = 'Mozilla/4.0 (compatible; MSIE 6.0; ' + \
    'Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)'
    self.br.addheaders = [("User-agent",user_agent)]
    self.br.set_handle_robots(False)
    
    self.br.open("http://nasza-klasa.pl")
    
    self.br.select_form(nr=0)
    self.br.form["login"]=username
    self.br.form["password"]=password
    
    #self.br.viewing_html=lambda: True
    self.br.submit()
    
    self.dashboard_tree = html.fromstring(self.br.response().read())

  def get_watched_forums(self, unread_only=False):
    ret = []
    for entry in self.dashboard_tree.xpath('//ul [@id="forum_max"]//li'):
      if not unread_only or not entry[0].items()[0][1].find('unread'):
	  ret.append(NK_forum(school_name = entry[1].text_content(),
			      url = nklink+entry[1].items()[1][1]))
    return ret

  def get_forum_threads(self,url):
    ret = []; page = 1
    self.br.open(url)
    while 1:
      forum_tree = html.fromstring(self.br.response().read())
      threads = forum_tree.xpath('//div [@id="threads"]//tr')[1:]
      if len(threads) > 1:
	for thread in threads:
	    
	  if thread.text_content() == " ":
	    continue

	  try: #wychrzania sie jesli posty=0 (http://tnij.org/g0un)
	    ret.append(NK_forum_thread(
	    title = thread[0].text_content(),
	    url = thread[0][1][0].items()[0][1],
	    started_author = thread[1][0].text_content(),
	    started_time = thread[1][1].text_content(),
	    posts_count = int(thread[2].text_content()),
	    lastpost_summary = thread[3][0][0][0].text_content(),
	    lastpost_author = thread[3][0][0][2].text_content(),
	    lastpost_date = thread[3][0][0][3].text_content()
		      ))
	  except: pass
		    
      nextpage = forum_tree.xpath('//a [contains(@title, "pna")]')
      if not nextpage: 
	break
      self.br.open('http://nasza-klasa.pl'+nextpage[0].items()[3][1])
    return ret
      
  def get_thread_posts(self,url):
    ret = []
    self.br.open(url)
    while 1:
      global thread_tree
      thread_tree = html.fromstring(self.br.response().read())
      posts = thread_tree.xpath('//div [@class="post"]')
      for post in posts:
	
	ret.append(NK_forum_post(
	  date = post[0].text_content(),
	  contents = post[1][1].text_content(),
	  author = NK_profile(
	    name = post[1][2][0][1][0].text_content(),
	    location = post[1][2][0][1][1].text_content(),
	    url = post[1][2][0][1].items()[2],
	    friends = post[1][2][0][2].text_content()
	    )
	  ))
      nextpage = thread_tree.xpath('//a [contains(@title, "pna")]')
      if not nextpage: 
	break
      self.br.open('http://nasza-klasa.pl'+nextpage[0].items()[3][1])
    return ret
    
if __name__ == '__main__':
  nk = PyNK('LOGIN','HASLO')
  watched_forums = nk.get_watched_forums()
  for forum in watched_forums:
    threads = nk.get_forum_threads(forum.url)
    for thread in threads:
	posts = nk.get_thread_posts(thread.url)
	break