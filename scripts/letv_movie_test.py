# -*- coding: utf-8 -*-
import re
import urllib2
from bs4 import BeautifulSoup
import string
import pymongo

NUM 	= 0			#全局变量,电影数量
m_type 	= u''		#全局变量,电影类型
m_site 	= u'letv'	#全局变量,电影网站

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
	#<dl class="soydl">
	divs_html = soup.find_all('dl', {'class' : 'soydl'})
	divs =  str(divs_html[1]).replace('\n', '').replace('\r', '').replace('\t', '')
	#print divs

	#<a href="http://so.letv.com/list/c1_t26_a-1_y-1_f_at_o1_i-1_p.html" id="iq">家庭</a>     
	re_tags = r'<a href=\"(.+?)\" id=\"iq\">(.+?)</a>'

	p = re.compile(re_tags, re.DOTALL)

	tags = p.findall(divs)
	#print tags
	tags_url = {}
	if tags:
		#print tags
		for tag in tags:
			m_type = tag[1]
			tags_url[tag[1].decode('utf-8')] = tag[0].decode('utf-8')

	else:
		print "Not Find"

	return tags_url

#获取每个分类的页数
def get_pages(tag_url):
	tag_html = gethtml(tag_url)
	#div class="paginator
	soup = BeautifulSoup(tag_html)		#过滤出标记页面的html
	#print soup
	#<div class="page">
	div_page = soup.find_all('div', {'class' : 'page'})
	#print len(div_page), div_page[0]

	#<a href="http://so.letv.com/list/c1_t10_a-1_y-1_f-1_at1_o1_i-1_p64.html">64</a>
	re_pages = r'<a href=\".+?\">(.+?)</a>'
	p = re.compile(re_pages, re.DOTALL)
	pages = p.findall(str(div_page))
	#print pages
	if len(pages):
		return pages[-2]
	else:
		return 1


def getmovie(html):
	global NUM
	global m_type
	global m_site

	soup = BeautifulSoup(html)

	#<dl class="m_dl">
	divs = soup.find_all('dl', {'class' : 'm_dl'})
	#print divs
	#
	divs_html = str(divs).replace('\n', '')

	#匹配电影信息的正则
	#<dl class="m_dl"><dt><a href="http://www.letv.com/ptv/pplay/52767/1.html" target="_blank" title="双重危机"><img alt="双重危机" onerror=
	re_movie = r'<dl class=\"m_dl\"><dt><a href=\"(.+?)\" target=\"_blank\" title=\"(.+?)\"><img alt=\".+?\" onerror='
	
	p_movie = re.compile(re_movie, re.DOTALL)
	movies = p_movie.findall(divs_html)

	values = {'movie_site' : m_site}
	values['movie_type'] = m_type
	conn = pymongo.Connection('localhost', 27017)
	movie_db = conn.dianying
	playlinks = movie_db.playlinks

	if movies:
			#print movies
			for movie in movies:
				values['movie_title']  = str(movie[1]).decode('utf-8')
				values['movie_url'] = str(movie[0]).decode('utf-8')

				print values
				playlinks.insert(values)
				NUM += 1
				print "%s : %d" % ("=" * 70, NUM)
				
	else:
			print "movie Not Find"


if __name__ == "__main__":
	global conn

	tags_url = "http://so.letv.com/list/c1_t_a_y_f_at_o_p.html"
	#print tags_url
	tags_html = gethtml(tags_url)
	#print tags_html
	tag_urls = gettags(tags_html)
	#print tag_urls

	for k in tag_urls:
		url = tag_urls[k]
		m_type = k
		print k, url
		
		maxpage = int(get_pages(url.encode('utf-8')))
		print maxpage
		
		#url format = "http://so.letv.com/list/c1_t8_a-1_y-1_f_at_o1_i-1_p.html"
		movie_url = url.replace('.html', '')
		#print movie_url

		for x in range(1, maxpage + 1 , 1):
			if x == 1:
				m_url = url
			else:
				m_url = "%s%d.html" % (movie_url, x)
			print m_url
			
			movie_html = gethtml(m_url.encode('utf-8'))
			#print movie_html
			getmovie(movie_html)







