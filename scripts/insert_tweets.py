import json
import csv
import collections

from access_django import *
from framenet.api import *
from annotate.models import *

"""
30197,ibirdu ::: 9865093633 ::: 发现 了 个 小 客户端 。 。 。 itsy 还 不错 ， 如果 要 是 黑色 theme 就 好 了
30199,olivia4ever ::: 28123918971699200 ::: 最近 还 蛮 喜欢 读 几 个 日本 作家 的 书 的 清清 淡淡 在 冬天 有 别样 感觉
30200,olivia4ever ::: 540116646501683200 ::: @linxiajiang 震动 ~ 又 想 歪 了 ……
30201,mason_bin ::: 649031455046107136 ::: 豆瓣 、 网易 、 虾米 搞 了 那么 多 年 的 免费 音乐 电台 都 没 搞 起来 ， 苹果 一来 问题 就 都 解决 了 ？ 我 看 不 见 的 。 推荐 算法 、 曲 库 、 流量 危机 这 三 样 没有 一 件 是 简单 能 解决 的 。 另外 ， 国人 也 就 听听 小 苹果 ， 让 他 付费 去 听 邓 紫棋 ， 我 觉得 难 。 #AppleMusicInChina
30202,mason_bin ::: 529819054588968960 ::: 之前 积攒 了 一 堆 pdf 电子书 想 要 淘宝 找个 打印 店 打 成 纸 书 看 ， 发给 对方 报 了 价 之后 发觉 跟 直接 买 印刷版 也 差不多 ， 于是 作罢 。 结束 对话 时有 一瞬间 ， 我 在 想 ， 卖家 是 不 是 得 把 pdf 文件 还 给 我 ？ ……
30203,solomonhuang ::: 19487640802 ::: 突然 看到 浅浅 的 透明 的 甜甜 的 思念 。
30204,fqworld ::: 10079733624 ::: 好奇 公众 人物 、 政治 人物 ， 使用 social network ， 应该 会 发现 直接 面对 人民 是 有 多 不 容易 、 坦承 面对 有 多 不 容易 、 说 出 真相 有 多 不 容易 ， 支吾其词 、 顾左右而言 他 都 不好 ， 等于 直接 显示 出 畏惧 跟 自身 的 站不住脚
30206,bones7456 ::: 5096330165 ::: 说明 ： 如果 您 的 朋友 想 要 知道 如何 才 能 自由地 访问 网络 ， 请 告诉 他们 可以 向 这个 地址 freeweb.tutorial @gmail.com 发送 任意 内容 的 email ， 转瞬间 他们 就 会 得到 当前 邮件 的 内容 。
30207,justissam ::: 429190744209780736 ::: 吃饱 度 姑中｡ 在 天 祥 天主堂
30208,olivia4ever ::: 203101545968054272 ::: @seansay 第二 集 是 “ 主食 的 故事 ” 说 到 了 西安 的馍 ~ （ 好 想念 ）
"""

word2frame = collections.defaultdict(set)
for lu in LexUnit.objects.all():
    word2frame[lu.name].add(lu.frame.eng_name)


def find_lu_fast(name):
      return list(word2frame[name])


def add_frames_fast(tokens):
    tokens_ = []
    for i, tok in enumerate(tokens):
        tokens_.append({
            'token': tok.strip(),
            'pos': '',
            'frames': find_lu_fast(name=tok.strip()),
            'token_i': i
        })
    return tokens_


if __name__ == '__main__':
    with open('data/img_mapping.json') as f:
        img_mapping = json.load(f)

    with open('data/corpus.only_cn.seg.csv', 'r', encoding='utf8') as f:
        i = 0
        for row in csv.reader(f):
            content = ''
            for tweet in row[1].split(' ||| '):
                author, _, text = tweet.split(' ::: ')
                content += '{}: {}\n\n'.format(author, text)

            preprocessed_content = {'tokens': add_frames_fast(content.split())}

            try:
                Entry.objects.create(
                    content=''.join(content.split()),
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
            print('{}/{}'.format(i, 26819), end='\r')
