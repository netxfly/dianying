# -*- coding: utf-8 -*-
import re
import urllib2
from bs4 import BeautifulSoup
import string
import pymongo

NUM 	= 0			#全局变量,电影数量
m_type 	= u''		#全局变量,电影类型
m_site 	= u'sohu'	#全局变量,电影网站


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
	#<dl class="cfix">
	tags_all = soup.find_all('dl', {'class' : 'cfix'})
	#print len(tags_all), str(tags_all[0]), #tags_all,
	#return

	#<a href="/list_p1100_p2100112_p3_p40_p5_p6_p77_p80_p9_2d1_p101_p11.html">灾难</a>
	re_tags = r'<a href=\"(.+?)\">(.+?)</a>'
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
		#del tags_url['全部']
			
	else:
			print "Not Find"

	return tags_url

#获取每个分类的页数
def get_pages(tag_url):
	tag_html = gethtml(tag_url)
	soup = BeautifulSoup(tag_html)		#过滤出标记页面的html
	# <div class="num">
	div_page = soup.find_all('div', {'class' : 'num'})

	pages = []
	if div_page:
		#print div_page #len(div_page), div_page[0]
		#return
		#<a href="/list_p1100_p2100118_p3_p40_p5_p6_p77_p80_p9_2d1_p102_p110.html">2</a>
		re_pages = r'<a href=\".+?\">(.+?)</a>'
		p = re.compile(re_pages, re.DOTALL)
		pages = p.findall(str(div_page[0]))
	
	#print pages
	#return
	if len(pages) > 1:
		return pages[-1]
	else:
		return 1
	

def getmovielist(html):
	soup = BeautifulSoup(html)

	#<div class="show-pic">
	divs = soup.find_all('div', {'class' : 'show-pic'})
	print divs
	for div_html in divs:
		div_html = str(div_html)
		#print div_html
		getmovie(div_html)


def getmovie(html):
	global NUM
	global m_type
	global m_site

	#<a class="pic" href="http://tv.sohu.com/20100926/n275272980.shtml" target="_blank" title="http://photocdn.sohu.com/20100925/vrsb88630.jpg"><img height="160" src="http://photocdn.sohu.com/20100925/vrsb88630.jpg" title="迷魂陷阱"
	re_movie = r'<a class=\"pic\" href=\"(.+?)\".+?>.+?title=\"(.+?)\"'
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

	tags_url = "http://so.tv.sohu.com/list_p1100_p2_p3_p40_p5_p6_p77_p80_p9_2d1_p101_p11.html"
	#print tags_url
	tags_html = gethtml(tags_url)
	#print tags_html
	tag_urls = gettags(tags_html)
	#print tag_urls
	wwwpath = "http://so.tv.sohu.com"

	for url in tag_urls.items():
		#print  str(url[1]) ,
		m_type = url[0]
		m_url = wwwpath + str(url[1])
		print m_url, url[0]

		#get_pages(m_url)
		#'''
		maxpage = int(get_pages(m_url))
		print maxpage

		for x in range(1, maxpage + 1):
			#http://so.tv.sohu.com/list_p1100_p2100116_p3_p40_p5_p6_p77_p80_p9_2d1_p101_p11.html
			#http://so.tv.sohu.com/list_p1100_p2100116_p3_p40_p5_p6_p77_p80_p9_2d1_p103_p110.html
			m_url = m_url.replace('1_p11.html', '')
			movie_url = "%s%d_p110.html" % (m_url, x)
			print movie_url

			movie_html = gethtml(movie_url)
			#print movie_html
			getmovielist(movie_html)
			#'''





