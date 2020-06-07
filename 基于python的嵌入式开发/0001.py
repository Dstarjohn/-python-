import requests
import time
from lxml import html
from matplotlib import pyplot as plt
import pandas as pd
import jieba
from wordcloud import WordCloud
import imageio
mask = imageio.imread('china.jpg')
# 获取影评页面并且进行解析该页面
def link_info(url):
    # 使用requests进行http请求然后获取网页的源代码
    resp = requests.get(url)
    html_data = resp.text
    return html_data
# 根据isbn爬取豆瓣电影的信息
def spider(isbn):
    movie_list = []
    url = 'https://movie.douban.com/cinema/later/'+isbn
    # 使用requests进行http请求然后获取网页的源代码
    resp = requests.get(url)
    html_data = resp.text
    # 使用xpath提取电影的信息
    selector = html.fromstring(html_data)
    ul_list = selector.xpath('//div[@id="showing-soon"]/div')
    print('您好，近期上映的电影有:',len(ul_list),'部')
    for li in ul_list:
        # 电影名
        title = li.xpath('div[@class="intro"]/h3/a/text()')[0]
        #电影链接地址
        link = li.xpath('div[@class="intro"]/h3/a/@href')[0]
        #上映日期
        date = li.xpath('div[@class="intro"]/ul/li[1]/text()')[0]
        #国家
        country = li.xpath('div[@class="intro"]/ul/li[3]/text()')[0]
        #想看人数
        num = li.xpath('div[@class="intro"]/ul/li[4]/span/text()')
        #判断有的电影想看人数是否空的，这里直接判断长度是否为空即可
        if len(num) == 0:
            num = '0人想看'
        else:
            num = num[0]
        #替换为空
        num = num.replace('人想看','')
        #显示电影列表的标签信息
        movie_list.append({
            "title": title,
            "date": date,
            "country": country,
            "num": num,
            "link":link
        })
        time.sleep(0.2)#友好型爬虫，休息0.2s在访问
        #排序，x轴为人数，纵轴按照人数排序
    movie_list.sort(key=lambda x: int(x['num']), reverse=True)
    df = pd.DataFrame(movie_list)
    #存储位置和excel形式打开，设置编码标准utf-8
    df.to_excel('D:\python-project\project\movie.xls', encoding='utf-8' )
    #选取movie_list列表的前top5
    movie_top = movie_list[:5]
    #根据num人数排序在坐标轴上，切片，x轴和y轴
    movie_top.sort(reverse=True,key=lambda x: int(x['num']))
    num_x = [int(i['num']) for i in movie_top]
    #将top前五和其电影名字同时显示在柱状图上面
    top_y = [('top'+str(1+i)+':'+movie_top[i]['title']) for i in range(5)]
    #定义一个用来存放不同电影的词云图片名字的全局变量
    temp = 1
    # 获取top前五的link地址
    newlink = [i['link'] for i in movie_top]
    #for循环用x来表示获取到更多电影评论的网页的地址
    for x in newlink:
        x = x+'comments?sort=new_score&status=F'
        res = html.fromstring(link_info(x))
        #再用xpath来获取我们需要标签评论的内容
        review_list = res.xpath('//div[@id="comments"]/div[@class="comment-item"]')
        #这里用了一个第二个for循环用到的全局变量dview，主要用来将获取的每一条评论拼接在一行显示
        dview = ""
        #第二个for循环来获取每一条评论的text（）内容
        for tag in review_list:
            view = tag.xpath('div[@class="comment"]/p/span/text()')[0]
            dview = dview+view
        #词云自动根据空格或者标点符号进行单词区分
        words = jieba.lcut(dview)
        cloud_word = []
        #获取单词
        for word in words:
            #过滤掉长度为1的单个词，否则将其添加进去词云
            if len(word) == 1:
                continue
            else:
                cloud_word.append(word)
            #通过join方法来将列表中的元素通过空格来拼接成一个新的字符串，然后显示出来
        cloud_text = " ".join(cloud_word)
        print(cloud_text)
        # 编写词云
        wc = WordCloud(
            width=800,
            height=600,
            background_color='white',
            #指定文件的路径，默认None
            font_path='msyh.ttc',
            #指定词云形状，默认为长方形，需要引用imread()函数
            mask=mask
        ).generate(cloud_text)
        #词云名字的设置
        name = 'filmWordCloud'+str(temp)+".png"
        wc.to_file(name)
        #用来输出top前五电影词云的名字
        temp = temp+1
        print("----------------------------------------------------------")
        #绘制柱状图
    plt.rcParams["font.sans-serif"] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.barh(top_y, num_x)
    plt.show()
spider('wuhan')
