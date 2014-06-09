# -*- coding: utf-8 -*-
import pymongo
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import string
import os

from tornado.options import define, options

define("port", default=9000, help="run on the given port", type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
    	alltags = []
    	conn = pymongo.Connection(host='127.0.0.1', port=27017)
    	db_movie = conn.movies
    	movie = db_movie.movie
    	movies = db_movie.movie.count()	#movies库中电影的数量
    	print movies
    	#所有电影分类
    	tags = db_movie.movie.distinct("info.genre")

    	db_dianying = conn.dianying
    	playlinks = db_dianying.playlinks
    	#tags = playlinks.distinct("movie_type")
    	#print tags, len(tags),type(tags)	#电影的类型

    	link_urls = playlinks.count()
    	print link_urls
    	movies = movies + link_urls
    	print movies
    	print tags
    	self.render("index.html", movies=movies, tags = tags)

class SearchHandler(tornado.web.RequestHandler):
    def get(self, *args):
    	movie_name = args[0]
    	print movie_name
    	entries = None
    	if movie_name:
    		conn = pymongo.Connection(host='127.0.0.1', port=27017)
    		db_dianying = conn.dianying
    		movie = db_dianying.playlinks
    		entries = movie.find({'movie_title':movie_name})
    		self.render("search.html", entries=entries)

    def post(self, *args):
		movie_name = self.get_argument('movie_name', '')
		print movie_name
		entry = None
		if movie_name:
			conn = pymongo.Connection(host='127.0.0.1', port=27017)
			db_dianying = conn.dianying
			movie = db_dianying.playlinks
			entries = movie.find({'movie_title':movie_name})
			#for i in entries:
			#	print i
			self.render("search.html", entries=entries)


class DetailHandler(tornado.web.RequestHandler):
    def get(self, *args):
		detailinfo = args[0]
		entry = None
		userinfo = string.split(detailinfo, "2")
		username = userinfo[0]
		recvname = userinfo[1]
		#print("%sto%s:"%(username, recvname))
		if username:
			#Connect to Mongodb
			conn_mongo = pymongo.Connection(host='192.168.17.25', port=27017)
			#select db
			db = conn_mongo.rtxlogs
			#select connection
			rtxlog = db.rtxlog
			entries = db.rtxlog.find({'username':username, 'recvname':recvname})
			for item in entries:
				print item
			self.render("templates/detail.html", entries=entries)

class ListTagsHandler(tornado.web.RequestHandler):
    def get(self, *args):
		tag = args[0]
		print tag
		#entries = None
		if tag:
			conn = pymongo.Connection(host='127.0.0.1', port=27017)
			db_movie = conn.movies
			movie = db_movie.movie
			entries = db_movie.movie.find({'info.genre':tag}).limit(200)
			#print entries
			#for i in entries:
				#print i

			self.render("tags.html", entries=entries)

class AboutHandler(tornado.web.RequestHandler):
    def get(self, *args):
    	self.render("about.html")

class ContactHandler(tornado.web.RequestHandler):
    def get(self, *args):
    	self.render("contact.html")

#
#
###########################################################
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
        (r"/", MainHandler),
		(r"/search/(.*)", SearchHandler),
		(r"/detail/(.*)", DetailHandler),
		(r"/tags/(.*)", ListTagsHandler),
		(r"/about", AboutHandler),
		(r"/contact", ContactHandler),
    ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

#main function 
###########################################################
def main():
	tornado.options.parse_command_line()
	#http_server = tornado.httpserver.HTTPServer(application)
	http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

###
#When module is main, then run application
##########################################################
if __name__ == "__main__":
	main()
