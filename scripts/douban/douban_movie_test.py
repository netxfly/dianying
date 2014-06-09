# -*- coding: utf-8 -*-
import re
import urllib2
from bs4 import BeautifulSoup
import string, time
import pymongo

NUM = 0				#全局变量,电影数量
m_type = u''		#全局变量,电影类型
m_site = u'douban'	#全局变量,电影网站
m_start = "http://movie.douban.com/subject/2045876/"	#这里配置上次异常退出时的URL
flag = False

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
	tags_all = soup.find_all('tbody')
	#print len(tags_all), tags_all[0]
	#print str(tags_all[0])

	#<td><a href="./爱情">爱情</a><b>(6709963)</b></td>
	re_tags = r'<td><a href=\"\./(.+?)\">(.+?)</a><b>\(.+?\)</b></td>'
	p = re.compile(re_tags, re.DOTALL)

	tags = p.findall(str(tags_all[0]))
	if tags:
		tags_url = []
		#print tags
		for tag in tags:
			m_type = tag[1]
			tag_url = "http://movie.douban.com/tag/" + tag[0].decode('utf-8')
			#print tag_url
			tags_url.append(tag_url)
			
	else:
			print "Not Find"

	return tags_url

#获取每个分类的页数
def get_pages(tag_url):
	tag_html = gethtml(tag_url)
	#div class="paginator
	soup = BeautifulSoup(tag_html)		#过滤出标记页面的html
	#print soup
	div_page = soup.find_all('div', {'class' : 'paginator'})
	#print len(div_page), div_page[0]

	#...</span><a href="http://movie.douban.com/tag/%E7%88%B1%E6%83%85?start=5440&type=T">273</a><a href="http://movie.douban.com/tag/%E7%88%B1%E6%83%85?start=5460&type=T">274</a><span class="next"><a href="http://movie.douban.com/tag/%E7%88%B1%E6%83%85?start=20&type=T">后页&gt
	re_pages = r'\.\.\.</span><a href=\".+?\">.+?</a><a href=\".+?\">(.+?)</a><span class=\"next\"><a href=\".+?\">后页&gt'
	p = re.compile(re_pages, re.DOTALL)
	pages = p.findall(str(div_page))

	return pages[0]

def getmovie(html):
	global NUM
	global m_type
	global m_site
	global m_start
	global flag

	soup = BeautifulSoup(html)

	#<div id="subject_list">
	divs = soup.find_all('div', {'id' : 'subject_list'})
	#print divs

	#<a class="nbg" href="http://movie.douban.com/subject/3094909/" title="乌云背后的幸福线"><img alt="乌云背后的幸福线" src="http://img3.douban.com/spic/s11364841.jpg"/></a></td><td valign="top"><div class="pl2"><a href="http://movie.douban.com/subject/3094909/">乌云背后的幸福线 / <span style="font-size:12px;">失恋自作业(港) / 派特的幸福剧本(台)</span></a><p class="pl">2012-09-08(多伦多电影节) / 2012-12-25(美国) / 布莱德利·库珀 / 詹妮弗·劳伦斯 / 罗伯特·德尼罗 / 杰基·韦佛 / 克里斯·塔克 / 阿努潘·凯尔 / 约翰·奥提兹 / 谢伊·惠格姆 / 朱丽娅·斯蒂尔斯 / 布莱德利·库珀 Bradley Cooper / 詹妮弗·劳伦斯...</p><div class="star clearfix"><span class="allstar40"></span><span class="rating_nums">7.7</span><span class="pl">(66349人评价)</span></div></div></td></tr></table><div id="collect_form_3094909"></div>
	re_movie = r'href=\"(.+?)\" title=\"(.+?)\"><img alt=\".+?\" src=\"(.+?)\"/>.+?<a href=\".+?\">.+?<p class=\"pl\">(.+?)</p>.+?<span class=\"rating_nums\">(.+?)</span>.+?</div>'
	div_html = str(divs).replace('\n', '')

	p = re.compile(re_movie, re.DOTALL)
	movies = p.findall(div_html)
	if movies:
			#print movies
			for movie in movies:
				#print movie
				NUM += 1
				print "%s : %d" % ("=" * 70, NUM)
				#for i in movie:
				#	print i
				#如果标识一直为false，则直接返回判断下一URL
				'''
				if not flag:
					#执行中断后，设置一个URL后，可以继续接着从上次开始的地方执行
					if not cmp(movie[0], m_start):
						flag = True
					elif m_start == "":
						flag = True
					else:
						print str(movie[0]), "...[ok]"
						continue
						'''

				values = dict(
					movie_url	= movie[0],
					movie_title = movie[1],
					movie_image = movie[2],
					movie_actor = movie[3],
					movie_score = movie[4],
					movie_types = m_type,
					movie_site = m_site,
					movie_intro = getmovie_intro(movie[0])
					)
				print values

				conn = pymongo.Connection('localhost', 27017)
				movie_db = conn.dianying
				movies = movie_db.movies
				movies.insert(values)

	else:
		print "Not Find"
		return False

def getmovie_intro(url):
	html = gethtml(url)
	soup = BeautifulSoup(html)

	#<div id="info">
	divs = soup.find_all('div', {'id' : 'info'})
	if divs:
		div_html  = str(divs[0]).replace('\n', '')

	#print div_html 
	#return
	m_info = {}

	re_movie = r'<span class=\"pl\">导演</span>: <a class=\"\" href=\".+?\" rel=\"v:directedBy\">(.+?)</a></span><br/>.+?<span class=\"pl\">主演</span>: <a class=\"\" href=\".+?\" rel=\"v:starring\">(.+?)</a> .+?<span class=\"pl\">类型:</span> <span property=\"v:genre\">(.+?)</span>.+?<span class=\"pl\">.+?<span class=\"pl\">片长:</span> .+?\"v:runtime\">(.+?)</span>'# .+?<span class=\"pl\">又名:</span> (.+?)<br/>'
	p = re.compile(re_movie, re.DOTALL)
	movies = p.findall(div_html)
	if movies:
		#print movies
		for info in movies[0]:
			print info
	else:
		print "Not find movie info"

		#return
		re_movie = r'<span class=\"pl\">导演</span>: <a class=\"\" href=\".+?\" rel=\"v:directedBy\">(.+?)</a></span><br/><span>.+?<span class=\"pl\">主演</span>: <a class=\"\" href=\".+?\" rel=\"v:starring\">(.+?)</a> .+?</span><br/><span class=\"pl\">类型:</span> <span property=\"v:genre\">(.+?)</span> .+?<span class=\"pl\">上映日期:</span> <span content=\"(.+?)\" .+?<span class=\"pl\">片长:</span> <span content=\".+?\" property=\"v:runtime\">(.+?)</span>'#<br/><span class=\"pl\">又名:</span> (.+?)<br/>'
		p = re.compile(re_movie, re.DOTALL)
		movies = p.findall(div_html)
		if movies:
			#print movies
			for info in movies[0]:
				print info
		else:
			print "Not find movie info"

	#<div class="related_info">			
	div_info 	= soup.find_all('div', {'class' : 'related_info'})
	if not div_info :
		m_info['movie_intro'] = u'剧情简介'
		m_info['movie_detail'] = u'暂无'
		return m_info

	info_html  	= str(div_info[0]).replace('\n', '')
	#print info_html

	re_info = r'<div class=\"related_info\"><a name=\"intro\"></a><h2>(.+?)</h2><div class=\"indent\" id=\"link-report\"><span class=\"\" property=\"v:summary\">(.+?)</span><span class=\"pl\">'
	#re_info = r'<h2>(.+?)</h2><div class=\"indent\" id=\"link-report\"><span property=\"v:summary\" class=\"\">(.+?)</span><span class=\"pl\"><a'
	p_info = re.compile(re_info, re.DOTALL)
	infos = p_info.findall(info_html)

	if infos:
		m_info['movie_intro'] = infos[0][0]
		m_info['movie_detail'] = infos[0][1]
		#print infos[0][0]
		#print infos[0][1]

	else:
		print "Not find movie info"
		#print u"暂无"
		m_info['movie_intro'] = u'剧情简介'
		m_info['movie_detail'] = u'暂无'

	return m_info


def insertdb(movieinfo):
	global conn
	movie_db = conn.dianying_at
	movies = movie_db.movies
	movies.insert(movieinfo)

if __name__ == "__main__":
	#try:
	tags_url = "http://movie.douban.com/tag/?view=type"
	#print tags_url
	tags_html = gethtml(tags_url)
	#print tags_html
	tag_urls = gettags(tags_html)
	#print tag_urls
	for url in tag_urls:
		print url.encode('utf-8')
		maxpage = int(get_pages(url.encode('utf-8')))
		print maxpage
		for x in range(0, (maxpage - 1) * 20, 20):
			movie_url = "%s?start=%d&type=T" % (url, x)

			print movie_url.encode('utf-8')
			movie_html = gethtml(movie_url.encode('utf-8'))

			#print movie_html
			#如果发现URL失效，直接换下一类别的URL
			if not getmovie(movie_html):
				break

			#time.sleep(0.3)

	#except Exception, e:
		#print e
	

	





