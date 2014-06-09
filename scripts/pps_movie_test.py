# -*- coding: utf-8 -*-
import re
import urllib2
from bs4 import BeautifulSoup
import string
import pymongo

NUM 	= 0			#全局变量,电影数量
m_type 	= u''		#全局变量,电影类型
m_site 	= u'pps'	#全局变量,电影网站

#根据指定的URL获取网页内容
def gethtml(url):
	req = urllib2.Request(url) 
	response = urllib2.urlopen(req) 
	html = response.read()
	return html

#从电影分类列表页面获取电影分类
def gettags(html):
	global m_type
	soup = BeautifulSoup(html.decode('gbk').encode('utf-8'))		#过滤出分类内容
	#<dd class="type shrink">
	tags_all = soup.find_all('dd', {'class' : 'type shrink'})
	#print len(tags_all), str(tags_all[0])

	#<a href="/v_list/c_movie_st_%BE%E7%C7%E9.html">剧情</a>
	re_tags = r'<a href=\"/(.+?)\">(.+?)</a>'
	p = re.compile(re_tags, re.DOTALL)

	tags = p.findall(str(tags_all[0]))
	if tags:
		tags_url = {}
		#print tags
		for tag in tags:
			tag_url = tag[0]
			#print tag_url
			m_type = tag[1]
			tags_url[m_type] = tag_url
		del tags_url['全部']
		print tags_url
			
	else:
			print "Not Find"
	return tags_url

#获取每个分类的页数
def get_pages(tag_url):
	tag_html = gethtml(tag_url)
	soup = BeautifulSoup(tag_html.decode('gbk'))		#过滤出标记页面的html
	#<div class="page-nav">
	div_page = soup.find_all('div', {'class' : 'page-nav'})
	#print div_page #len(div_page), div_page[0]

	#<span class="sp">1</span></a>
	re_pages = r'<span class=\"sp\">(.+?)</span></a>'
	p = re.compile(re_pages, re.DOTALL)
	pages = p.findall(str(div_page[0]))
	#print pages
	if len(pages) > 1:
		return pages[-2]
	else:
		return 1
	

def getmovielist(html):
	soup = BeautifulSoup(html)

	#<ul class="infro-list">
	divs = soup.find_all('ul', {'class' : 'infro-list'})
	#print divs
	for div_html in divs:
		div_html = str(div_html).replace('\n', '')
		#print div_html
		#print "+" * 70
		getmovie(div_html)


def getmovie(html):
	global NUM
	global m_type
	global m_site

	re_movie = r'<ul class=\"infro-list\"><li><h2 class=\"t\"><a href="(.+?)" target=\"_blank\" title=\".+?\">(.+?)</a><strong .+?</ul>'
	p = re.compile(re_movie, re.DOTALL)
	movies = p.findall(html)
	if movies:
		#print movies
		for movie in movies:
			conn = pymongo.Connection('localhost', 27017)
			movie_db = conn.dianying
			playlinks = movie_db.playlinks
			#print movie
			NUM += 1
			values = dict(
				movie_title = movie[1].decode('gbk'),
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

	tags_url = "http://v.pps.tv/v_list/c_movie.html"
	#print tags_url
	tags_html = gethtml(tags_url)
	#print tags_html
	tag_urls = gettags(tags_html)
	#print tag_urls
	wwwpath = "http://v.pps.tv/"

	for url in tag_urls.items():
		print  str(url[1]) #,url[0]
		m_type = str(url[0])
		m_url =  wwwpath + str(url[1])

		maxpage = int(get_pages(m_url))
		print maxpage

		for x in range(0, maxpage + 1):
			#http://v.pps.tv/v_list/c_movie_st_%BE%E7%C7%E9_p_2.html
			#http://v.pps.tv/v_list/c_movie_st_%BE%E7%C7%E9.html
			m_url = m_url.replace('.html', '')
			movie_url = "%s_p_%d.html" % (m_url, x)
			print movie_url
			movie_html = gethtml(movie_url)
			#print movie_html
			getmovielist(movie_html)




