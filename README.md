电影爬虫及搜索网站说明
==========
本份代码中包含了国内大多数电影网站的爬虫，详细列表为：
1. 爱奇艺
1. 乐视
1. m1905
1. PPTV 
1. QQ电影 
1. 搜狐电影 
1. 土豆电影 
1. 迅雷电影 
1. 优酷 
1. 豆瓣电影库

# 爬虫
代码是一年前写好的，所以爬虫可能已经失效，不过在此基础上改改应该就可以了。

```python
K:\GIT\dianying\scripts>tree /f
文件夹 PATH 列表
卷序列号为 EE77-EC45
K:.
│  iqiyi_movie_test.py
│  letv_movie_test.py
│  m1905_movie_test.py
│  pps_movie_test.py
│  pptv_movie_test.py
│  qq_movie_test.py
│  sohu_movie_test.py
│  tudou_movie_test.py
│  xunlei_movie_test.py
│  youku_movie_test.py
│
└─douban
        doubanapi_1.py
        doubanapi_2.py
        doubanapi_3.py
        doubanapi_xj.py
        douban_movie_test.py

```

# 搜索网站

dianying_web.py支持将爬虫保存到mongodb中的数十万条记录以WEB方式的形式展示，并支持关键字查询。

