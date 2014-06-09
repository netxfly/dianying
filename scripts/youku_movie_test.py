# -*- coding: utf-8 -*-
import re
import urllib2
from bs4 import BeautifulSoup
import string, time
import pymongo

NUM = 0				#全局变量,电影数量
m_type = u''		#全局变量,电影类型
m_site = u'youku'	#全局变量,电影网站

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
	#<div class="item category">
	div = soup.find_all('div', {'class' : 'item category'})
	#print div[0]
	
	#<li class=""><a href="/channel/movielist_0_2001_0_1_1.html">喜剧</a></li>
	re_tags = r'<li class=\"\"><a href=\"(.+?)\">(.+?)</a></li>'

	p = re.compile(re_tags, re.DOTALL)

	tags = p.findall(str(div[0]))
	#print tags
	tags_url = {}
	if tags:
		#print tags
		for tag in tags:
			m_type = tag[1]
			tag_url = "http://www.soku.com" + tag[0].decode('utf-8')
			#print tag_url
			#tags_url.append(tag_url)
			tags_url[m_type] = tag_url
			
	else:
			print "Not Find"

	return tags_url

#获取每个分类的页数
def get_pages(tag_url):
	tag_html = gethtml(tag_url)
	#div class="paginator
	soup = BeautifulSoup(tag_html)		#过滤出标记页面的html
	#print soup
	#<div class="catastat">
	div_page = soup.find_all('div', {'class' : 'catastat'})
	#print len(div_page), div_page[0]

	#共3511部电影
	re_pages = r'共(.+?)部电影'
	p = re.compile(re_pages, re.DOTALL)
	pages = p.findall(str(div_page))
	#print pages

	page = int(pages[0])
	if page / 20 > 100:
		page = 100
	else:
		page = page / 20 + 1 

	return page

def getmovie_list(html):
	soup = BeautifulSoup(html)

	#<div class="showlist">，里面又分为电影信息和playlist，只取电影标题与播放源
	divs = soup.find_all('div', {'class' : 'showlist'})
	#print divs
	#
	divs_html = str(divs).replace('\n', '')
	divs_html = str(divs_html).split('<!--playarea end-->')
	del divs_html[-1]

	for div_html in divs_html:
		getmovie(div_html)
		#print str(divs_html).encode('utf-8')
		print "*" * 80

def getmovie(html):
	global NUM
	global m_type
	global m_site

	#一条正则同进匹配电影信息和播放源的话，处理起来很麻烦，还是用2条吧，顺序执行，然后加到一个字典里面
	div_html = str(html).replace('\n', '')
	#print div_html

	#匹配电影信息的正则
	re_movie = r'<div class=\"item\"><ul class=\"p pv\">.+?title=\"(.+?)\"></a></li>.+?<li class=\"p_desc\">(.+?)</li><li class=\"p_rating\">'
	
	p_movie = re.compile(re_movie, re.DOTALL)
	movies = p_movie.findall(div_html)

	values = {'movie_site' : m_site}
	values['moive_type'] = m_type
	m_source = {}

	if movies:
		#连接数据库，放在循环外，提高效率
		conn = pymongo.Connection('localhost', 27017)
		movie_db = conn.dianying
		playlinks = movie_db.playlinks

		for movie in movies:
			values['movie_title'] = movie[0]
			#values['movie_intro'] = movie[1]

			print "_" * 70
			#print movie
			#for i in movie:
			#print i
			NUM += 1
			print "%s : %d" % ("=" * 70, NUM)

		#匹配播放源的正则
		re_source = r'<span id=\".+?\" name=\"(.+?)\" sv=\".+?\" href=\"(.+?)\" speed=\".+?\"/></a></span>'
		p_source = re.compile(re_source, re.DOTALL)
		source = p_source.findall(div_html)

		if source:
			values['movie_url'] = source
			for v in values['movie_url']:
				print "_" * 70
				print v
				m_source[v[0]] =v[1]

			values['movie_url'] = m_source

		else:
			print "source Not Find"

		print values
		playlinks.insert(values)	#将播放源插入DB中
		'''
		print values['movie_title']
		print values['movie_intro']
		m_src = values['movie_source']
		for k in m_src:
			print k, m_src[k]
			'''	
	else:
			print "movie Not Find"


if __name__ == "__main__":
	global conn

	tags_url = "http://www.soku.com/channel/movielist_0_0_0_1_1.html"
	#print tags_url
	tags_html = gethtml(tags_url)
	#print tags_html
	tag_urls = gettags(tags_html)
	#print tag_urls

	for k in tag_urls:
		print k, tag_urls[k]
		m_type = k
		url = tag_urls[k]
		maxpage = int(get_pages(url.encode('utf-8')))
		print maxpage
		#url format = "http://www.soku.com/channel/movielist_0_2001_0_1_1.html"
		movie_url = url.replace('1.html', '')
		#print movie_url

		for x in range(1, maxpage + 1 , 1):
			m_url = "%s%d.html" % (movie_url, x)
			print m_url.encode('gbk')
			
			movie_html = gethtml(m_url.encode('utf-8'))
			#print movie_html
			getmovie_list(movie_html)
			time.sleep(0.01)
			

	





