# -*- coding: utf-8 -*-
import re
import urllib2
from bs4 import BeautifulSoup
import string
import pymongo

NUM 	= 0			#全局变量,电影数量
m_type 	= u''		#全局变量,电影类型
m_site 	= u'iqiyi'	#全局变量,电影网站

#根据指定的URL获取网页内容
def gethtml(url):
	req = urllib2.Request(url) 
	response = urllib2.urlopen(req) 
	html = response.read()
	return html

#从电影分类列表页面获取电影分类
def gettags(html):
	global m_type
	soup = BeautifulSoup(html)		#过滤出分类内容
	#print soup
	#div class="item genre" data-id="2">
	tags_all = soup.find_all('div', {'class' : 'item genre' , 'data-id' : '2'})
	#print len(tags_all), tags_all
	#print str(tags_all[1]).replace('\n', '')

	#<li data-value="11"><a href="http://list.iqiyi.com/www/1/-11-----------2-2-1-1---.html">动作</a><span><em>动作</em></span></li>
	re_tags = r'<li data-value=\".+?\"><a href=\"(.+?)\">(.+?)</a><span><em>.+?</em></span></li>'
	p = re.compile(re_tags, re.DOTALL)

	tags = p.findall(str(tags_all[0]))
	tags_url = {}

	if tags:
		#print tags
		for tag in tags:
			tag_url = tag[0].decode('utf-8')
			#print tag_url
			m_type = tag[1].decode('utf-8')
			tags_url[m_type] = tag_url 
			
	else:
			print "Not Find"
	return tags_url

#获取每个分类的页数
def get_pages(tag_url):
	tag_html = gethtml(tag_url)
	soup = BeautifulSoup(tag_html)		
	#过滤出标记页面的html
	#<div class="page">
	div_page = soup.find_all('div', {'class' : 'page'})
	#print div_page #len(div_page), div_page[0]

	#<a data-key="2" title="跳转至第2页" href="http://list.iqiyi.com/www/1/-133-----------2-2-2-1---.html">2</a> <a
	re_pages = r'<a .+?>(.+?)</a>'
	p = re.compile(re_pages, re.DOTALL)
	pages = p.findall(str(div_page[0]))
	#print pages

	if len(pages) > 1:
		return pages[-2]
	else:
		return 1
	

def getmovielist(html):
	soup = BeautifulSoup(html)

	#<div class="list0">
	divs = soup.find_all('div', {'class' : 'list0'})
	#print divs
	for div_html in divs:
		#div_html = str(div_html).replace('\n', '')
		#print str(div_html)
		getmovie(str(div_html))


def getmovie(html):
	global NUM
	global m_type
	global m_site
	#<a class="title" href="http://www.iqiyi.com/dianying/20130422/b58b5ac597e8dbb7.html?fc=a64f3700229a0bc3">非常人贩</a>

	re_movie = r'<a class=\"title\" href=\"(.+?)\">(.+?)</a>'
	p = re.compile(re_movie, re.DOTALL)
	movies = p.findall(str(html))
	if movies:
		#print movies
		#values = {'movie_site' : m_site}
		conn = pymongo.Connection('localhost', 27017)
		movie_db = conn.dianying
		playlinks = movie_db.playlinks

		for movie in movies:
			#print movie
			NUM += 1
			values = dict(
					movie_title 	= movie[1],
					movie_url 	= movie[0],
					movie_site		= m_site,
					movie_type		= m_type
					)
			
			print values
			playlinks.insert(values)
			print "%s : %d" % ("=" * 70, NUM)
		
	#else:
	#	print "Not Find"

def getmovieinfo(url):
	html = gethtml(url)
	soup = BeautifulSoup(html)

	#pack pack_album album_cover
	divs = soup.find_all('div', {'class' : 'pack pack_album album_cover'})
	#print divs[0]

	#<a href="http://www.tudou.com/albumplay/9NyofXc_lHI/32JqhiKJykI.html" target="new" title="《血滴子》独家纪录片" wl="1"> </a> 
	re_info = r'<a href=\"(.+?)\" target=\"new\" title=\"(.+?)\" wl=\".+?\"> </a>'
	p_info = re.compile(re_info, re.DOTALL)
	m_info = p_info.findall(str(divs[0]))
	if m_info:
		return m_info
	else:
		print "Not find movie info"

	return m_info


if __name__ == "__main__":
	global conn

	tags_url = "http://list.iqiyi.com/www/1/------------2-2-1-1---.html"
	#print tags_url
	tags_html = gethtml(tags_url)
	#print tags_html
	tag_urls = gettags(tags_html)
	#print tag_urls

	for url in tag_urls.items():
		print  str(url[1]).encode('utf-8') ,url[0]
		m_type = url[0]
		maxpage = int(get_pages(str(url[1]).encode('utf-8')))
		print maxpage

		for x in range(1, maxpage + 1):
			#http://list.iqiyi.com/www/1/-11-----------2-2-1-1---.html
			m_url = str(url[1]).replace('1-1---.html', '')
			movie_url = "%s%d-1---.html" % (m_url, x)
			print movie_url
			movie_html = gethtml(movie_url.encode('utf-8'))
			#print movie_html
			getmovielist(movie_html)





