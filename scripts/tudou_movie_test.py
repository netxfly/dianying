# -*- coding: utf-8 -*-
import re
import urllib2
from bs4 import BeautifulSoup
import string
import pymongo

NUM = 0		#全局常量,电影数量
m_type = u''		#全局变量,电影类型
m_site = u'tudou'	#全局变量,电影网站

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
	print soup
	print "=" * 80
	#<div class="category-item ">
	tags_all = soup.find_all('div', {'class' : 'category-item'})
	print len(tags_all), tags_all
	#print str(tags_all[1]).replace('\n', '')

	#<li> <a href="ach22a-2b2000421c-2d-2e-2f-2g-2h-2i-2j-2k-2l-2m-2n-2o-2so3pe-2pa1.html">剧情</a> </li>
    
	re_tags = r'<li> <a href=\"(.+?)\">(.+?)</a> </li>'
	p = re.compile(re_tags, re.DOTALL)

	tags = p.findall(str(tags_all[1]))
	if tags:
		tags_url = {}
		#print tags
		for tag in tags:

			tag_url = "http://www.tudou.com/cate/" + tag[0].decode('utf-8')
			#print tag_url
			m_type = tag[1].decode('utf-8')
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
	#<div class="page-nav">
	div_page = soup.find_all('div', {'class' : 'page-nav'})
	#print len(div_page), div_page[0]
	#print str(div_page).replace('\n', '')

	#<li><a href="ach22a-2b2000403c-2d-2e-2f-2g-2h-2i-2j-2k-2l-2m-2n-2o-2so3pe-2pa4.html">4</a></li>
	re_pages = r'<li><a href=\".+?\">(.+?)</a></li>'
	p = re.compile(re_pages, re.DOTALL)
	pages = p.findall(str(div_page).replace('\n', ''))
	#print pages
	if len(pages) > 1:
		return pages[-1]
	else:
		return 1

def getmovielist(html):
	soup = BeautifulSoup(html)

	#<div class="pack pack_album">
	divs = soup.find_all('div', {'class' : 'pack pack_album'})
	#print divs
	for div_html in divs:
		div_html = str(div_html).replace('\n', '')
		#print div_html
		getmovie(div_html)


def getmovie(html):
	global NUM
	global m_type
	global m_site

	#<h6 class="caption"> <a href="http://www.tudou.com/albumcover/Z7eF_40EL4I.html" target="_blank" title="徒步旅行队">徒步旅行队</a> </h6> <ul class="info"> <li class="desc">法国卖座喜剧片</li> <li class="cast"> </li> </ul> </div> <div class="ext ext_last"> <div class="ext_txt"> <h3 class="ext_title">徒步旅行队</h3> <div class="ext_info"> <span class="ext_area">地区: 法国</span> <span class="ext_cast">导演: </span> <span class="ext_date">年代: 2009</span> <span class="ext_type">类型: 喜剧</span> </div> <p class="ext_intro">理查德·达奇拥有一家小的旅游公司，主要经营法国游客到非洲大草原的旅游服务。六个法国游客决定参加理查德·达奇组织的到非洲的一...</p>

	re_movie = r'<h6 class="caption"> <a href=\"(.+?)\" target=\"_blank\" title=\".+?\">(.+?)</a> .+? <p class=\"ext_intro\">(.+?)</p>'
	p = re.compile(re_movie, re.DOTALL)
	movies = p.findall(html)
	if movies:
			#print movies
			#conn = pymongo.Connection('localhost', 27017)
			#movie_db = conn.dianying
			#playlinks = movie_db.playlinks

			for movie in movies:
				conn = pymongo.Connection('localhost', 27017)
				movie_db = conn.dianying
				playlinks = movie_db.playlinks

				#print movie
				NUM += 1
				print "%s : %d" % ("=" * 70, NUM)
				#for i in movie:
				#	print i
				#print movie[0]	#url
				#print movie[1]	#title
				#print movie[2]	#desc

				m_url = getmovieinfo(movie[0])
				#print m_url[0][0]	# playlink
				#print m_url[0][1]	# title	
				values = dict(
					movie_source 	= movie[0],
					movie_title = movie[1],
					#movie_intro = movie[2],
					movie_url = m_url[0][0],
					movie_site = m_site,
					movie_type	= m_type
					)

				print values
				playlinks.insert(values)
									
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

	tags_url = "http://www.tudou.com/cate/ach22a-2b-2c-2d-2e-2f-2g-2h-2i-2j-2k-2l-2m-2n-2o-2so3pe-2pa1.html"
	#print tags_url
	tags_html = gethtml(tags_url)
	print str(tags_html).decode('gbk').encode('utf-8')
	tag_urls = gettags(str(tags_html).decode('gbk').encode('utf-8'))
	#print tag_urls


	for url in tag_urls.items():
		#print url[0], 
		m_type = url[0] 
		maxpage = int(get_pages(str(url[1]).encode('utf-8')))
		print maxpage
		for x in range(1, maxpage + 1):
			#http://www.tudou.com/cate/ach22a-2b2000421c-2d-2e-2f-2g-2h-2i-2j-2k-2l-2m-2n-2o-2so3pe-2pa1.html
			m_url = str(url[1]).replace('1.html', '')
			movie_url = "%s%d.html" % (m_url, x)
			print movie_url
			movie_html = gethtml(movie_url.encode('utf-8'))
			#print movie_html
			getmovielist(movie_html)

	





