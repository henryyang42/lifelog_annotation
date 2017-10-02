import json
import csv
import jieba.posseg as pseg

from access_django import *
from framenet.api import *
from annotate.models import *

"""
1,bones7456 ::: 803789052465950721 ::: @smallfishxy 高端啊！
2,fqworld ::: 538658812849557504 ::: 老县长阿不拉真的太勇了 #IFTTT
3,mason_bin ::: 540400648202641409 ::: @bfishadow Calibre 不是用来管理下载的盗版电子书的么？Amazon 上购买的正版如何管理？
4,funtone ::: 33590872687779840 ::: 分享 原来漫画里的鬼头医生是长发帅哥，不是女生。不过，电视剧里演鬼头的女演员很有说服力，也诠释出了很棒的鬼头医生。 http://plurk.com/p/aisc94
5,mason_bin ::: 828118107981963267 ::: 车子打不着火了，在等4S店过来救援。正好在深圳湾公园里看看书，休息下。 https://t.co/casNzixVlO
6,celte ::: 822731826485755904 ::: RT @iruitui: RT @Fatal1tyV:RT @Carlos_Gong: 正值中午吃饭时间，有个高中同学在朋友圈发了她儿子早上拉的一坨屎，九个角度还用了滤镜。恶心坏了。
...
1285,wwwGUIA ::: 762516597982367744 ::: 你们心心念念跪舔的女推友丑得那逼样还说自己省了整容的钱，哪来的自信？ ||| hzjab1987 ::: 762585637656498177 ::: @wwwGUIA 谁
"""


if __name__ == '__main__':
    with open('data/img_mapping.json') as f:
        img_mapping = json.load(f)

    with open('data/corpus.cn.csv', 'r') as f:
        i = 0
        for row in csv.reader(f):
            content = ''
            for tweet in row[1].split(' ||| '):
                author, _, text = tweet.split(' ::: ')
                content += '{}: {}\n\n'.format(author, text)

            preprocessed_content = tokenize(content)
            try:
                Entry.objects.create(
                    content=content,
                    raw=str(row),
                    preprocessed_content=json.dumps(preprocessed_content, ensure_ascii=False),
                    author=author,
                    source_type=Entry.TWEET,
                    media='' if img_mapping[row[0]] == 'None' else img_mapping[row[0]],
                    source_id=row[0],
                )
            except:
                print('GG')
            i += 1
            print('{}/{}'.format(i, 30445), end='\r')
