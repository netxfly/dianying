# -*- coding: utf-8 -*-
import re
import urllib2
from bs4 import BeautifulSoup
import string
import pymongo

NUM 	= 0			#全局变量,电影数量
m_type 	= u''		#全局变量,电影类型
m_site 	= u'm1905'	#全局变量,电影网站


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
	#<span class="fl">,共11个，类型排第4个，下标为3
	tags_all = soup.find_all('span', {'class' : 'fl'})
	#print len(tags_all), str(tags_all[3]), #tags_all,

	#<a class="" href="javascript:void(0);" onclick="location.href='http://www.m1905.com/vod/list/n_1_t_1/o4u1.html';return false;" title="动作">动作</a>
	re_tags = r'<a class=\"\".+?href=\'(.+?)\'.+?>(.+?)</a>'
	p = re.compile(re_tags, re.DOTALL)

	tags = p.findall(str(tags_all[3]))
	if tags:
		tags_url = {}
		#print tags
		for tag in tags:
			tag_url = tag[0]
			#print tag_url
			m_type = tag[1]
			tags_url[m_type] = tag_url
		#del tags_url['全部']
			
	else:
			print "Not Find"

	return tags_url

#获取每个分类的页数
def get_pages(tag_url):
	tag_html = gethtml(tag_url)
	soup = BeautifulSoup(tag_html)		#过滤出标记页面的html
	# <div id="new_page">
	div_page = soup.find_all('div', {'id' : 'new_page'})

	pages = []
	if div_page:
		#print div_page #len(div_page), div_page[0]
		#return
		#<a href="http://www.m1905.com/vod/list/t_28_n_1/o4u1l0p6.html">6</a>
		re_pages = r'<a href=\".+?\">(.+?)</a>'
		p = re.compile(re_pages, re.DOTALL)
		pages = p.findall(str(div_page[0]))
	
	#print pages
	if len(pages) > 1:
		return pages[-1]
	else:
		return 1
	

def getmovielist(html):
	soup = BeautifulSoup(html)

	#<div class="cl br_Graye3">
	divs = soup.find_all('div', {'class' : 'cl br_Graye3'})
	#print divs
	for div_html in divs:
		div_html = str(div_html)
		#print div_html
		getmovie(div_html)


def getmovie(html):
	global NUM
	global m_type
	global m_site

	#<h4><span class="fr cherry_f f18">3.5</span><a class="f12" href="http://www.m1905.com/vod/info/377782.shtml" target="_blank" title="胭脂">胭脂</a></h4>
	re_movie = r'</span><a.+?href=\"(.+?)\".+?>(.+?)</a></h4>'
	p = re.compile(re_movie, re.DOTALL)
	movies = p.findall(html)
	if movies:
		#print movies
		for movie in movies:
			conn = pymongo.Connection('localhost', 27017)
			movie_db = conn.dianying
			playlinks = movie_db.playlinks
			#print movie
			values = dict(
				movie_title = movie[1],
				movie_url 	= movie[0],
				movie_site		= m_site,
				movie_type		= m_type
				)

			print values
			playlinks.insert(values)
			NUM += 1
			print "%s : %d" % ("=" * 70, NUM)

	else:
		print "Not Find movie..."

'''
def getmovieinfo(url):
	html = gethtml(url)
	soup = BeautifulSoup(html)

	#pack pack_album album_cover
	divs = soup.find_all('div', {'class' : 'pack pack_album album_cover'})
	if divs:
		#print divs[0]
		#<a href="http://www.tudou.com/albumplay/9NyofXc_lHI/32JqhiKJykI.html" target="new" title="《血滴子》独家纪录片" wl="1"> </a> 
		re_info = r'<a href=\"(.+?)\" target=\"new\" title=\"(.+?)\" wl=\".+?\"> </a>'
		m_info = p_info.findall(str(divs[0]))
	
	if m_info:
		return m_info
	else:
		print "Not find movie info"

	return m_info
'''


if __name__ == "__main__":

	tags_url = "http://www.m1905.com/vod/list/n_1/o4u1.html"
	#print tags_url
	tags_html = gethtml(tags_url)
	#print tags_html
	tag_urls = gettags(tags_html)
	#print tag_urls
	#wwwpath = "http://v.pps.tv/"

	for url in tag_urls.items():
		#print  str(url[1]) ,url[0]
		m_type = str(url[0])
		m_url = str(url[1])
		print m_url, url[0]

		#get_pages(m_url)
		maxpage = int(get_pages(m_url))
		print maxpage

		for x in range(0, maxpage + 1):
			#http://www.m1905.com/vod/list/n_1_t_1/o4u1.html
			#http://www.m1905.com/vod/list/t_1_n_1/o4u1l0p2.html
			m_url = m_url.replace('.html', '')
			movie_url = "%sl0p%d.html" % (m_url, x)
			print movie_url

			movie_html = gethtml(movie_url)
			#print movie_html
			getmovielist(movie_html)





