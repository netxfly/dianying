# -*- coding: utf-8 -*-
import urllib2
import string
import pymongo
import json
import re

NUM 	= 0			#全局变量,电影数量
m_type 	= u''		#全局变量,电影类型
m_site 	= u'douban'	#全局变量,电影网站
START	= NUM % 20
last 	= NUM

#根据指定的URL获取网页内容
def gethtml(url):
	req = urllib2.Request(url) 
	response = urllib2.urlopen(req) 
	html = response.read()
	return html

#从电影分类列表页面获取电影分类
def gettags():
	global m_type
	#分类页面混入了未能正常解析的模板，导致BeautifulSoup处理过程中出错，干脆自己复制出来算了
	tags_all = """
                <li><a href="#">歌舞</a></li>
                <li><a href="#">家庭</a></li>
                <li><a href="#">西部</a></li>
                <li><a href="#">奇幻</a></li>
                <li><a href="#">冒险</a></li>
                <li><a href="#">武侠</a></li>
                <li><a href="#">古装</a></li>
                <li><a href="#">鬼怪</a></li>
                <li><a href="#">戏曲</a></li>
	"""

	#<li><a href="#">剧情</a></li>
	re_tags = r'<li><a href=\"(.+?)\">(.+?)</a></li>'
	p = re.compile(re_tags, re.DOTALL)
	tags_url = {}

	tags = p.findall(tags_all)
	if tags:
		#print tags
		for tag in tags:
			tag_url = tag[0]
			#print tag_url
			m_type = tag[1]
			tags_url[m_type] = tag_url 
			
	else:
			print "Not Find"
	return tags_url


def getmovie(movieslist):
	global NUM		#电影数量
	global m_type 	#电影类型
	global m_site 	#电影所在网站

	if movieslist:
		conn = pymongo.Connection('localhost', 27017)
		movies_db = conn.dianying
		movies = movies_db.movies
		#print movies
		for movie in movieslist:
			#print movie
			movie_id = movie["id"]
			#print movie_id
			m_info = getmovieinfo(movie_id)
			NUM += 1
			values = dict(
				movie_subject 	= movie,
				movie_site		= m_site,
				movie_type		= m_type,
				movie_info		= m_info
				)
			print values
			movies.insert(values)
			print "%s : %d" % ("=" * 70, NUM)
	else:
		print "Not movie to be got"


def getmovieinfo(movie_id):
	#api_url = http://api.douban.com/v2/movie/subject/1297570
	url = "http://api.douban.com/v2/movie/subject/%s" % (movie_id)
	m_info = gethtml(url)
	movie_info = json.loads(m_info)

	if len(movie_info) == 3:
		movie_info = {}
	else:
		return movie_info

if __name__ == "__main__":
	#m_type 	#电影类型
	#START	#标志位
	#last 	#上次入库的数量

	#tags_url = "http://movie.douban.com/category/"
	tag_urls = gettags()
	#print tag_urls

	for tag in tag_urls.keys():
		m_type = tag
		print m_type

		#api_url = "http://api.douban.com/v2/movie/search?tag=%E5%85%A8%E9%83%A8&start=0"
		for start in xrange(0, 50000, 20):
			#如果已经入过库了，则继续往后查找电影
			START += start
			if START < last:
				print START
				continue

			url = "http://api.douban.com/v2/movie/search?tag=%s&start=%d" % (tag, start)
			print url

			html = gethtml(url)
			#print html
			movielist = json.loads(html)

			#如果该类别的电影内容为空，则跳出循环枚举下一类别的
			if not movielist['subjects']:
				print "Not movie"
				break
			else:
				#print movielist['subjects']
				getmovie(movielist['subjects'])

		#开始执行下一轮的循环
		print "Start Next tag"
		continue






