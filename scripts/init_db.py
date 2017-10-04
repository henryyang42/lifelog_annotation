import json

import jieba.posseg as pseg

from access_django import *
from framenet.models import *


""" CFN Example:
{
  "info":{
    "chi_name":"身体装饰品",
    "description":"该框架描述的是人类穿戴或用在身体上的装饰物。",
    "eng_name":"Body_decoration"
  },
  "lus":[
    "粉底/n;",
    "化妆品/n;",
    "口红/n;",
    "腮红/n;",
    "纹身/n;",
    "胭脂/n;",
    "眼线笔/n;",
    "眼影/n;",
    "眼影粉/n;",
    "遮瑕霜/n;"
  ],
  "noncore_fes":[
    {
      "chi_name":"身体部位",
      "description":"这个框架元素表示身体上有装饰品的位置。",
      "eng_name":"Body_location",
      "abbr":"bodp"
    },
    {
      "chi_name":"戴装饰的个体",
      "description":"身体有装饰品的个体。",
      "eng_name":"Decorated_individual",
      "abbr":"dec_ind"
    },
    {
      "chi_name":"装饰描述语",
      "description":"装饰描述语指的是装饰品的描述语。",
      "eng_name":"Decoration_desriptor",
      "abbr":"dec_desc"
    },
    {
      "chi_name":"图案",
      "description":"该框架元素描述的是装饰物呈现的形状。",
      "eng_name":"Picture",
      "abbr":"pic"
    },
    {
      "chi_name":"类型",
      "description":"类型指的是身体装饰的不同种类。该框架元素通常是多词或复合词的一部分。",
      "eng_name":"Type",
      "abbr":"type"
    },
    {
      "chi_name":"用途",
      "description":"该框架元素指的是身体装饰物的用途。",
      "eng_name":"Use",
      "abbr":"use"
    }
  ],
  "core_fes":[
    {
      "chi_name":"装饰品",
      "description":"装饰品指的是装饰身体的装饰性物品。",
      "eng_name":"Decoration",
      "abbr":"dec"
    }
  ]
}
"""


def insert_frame(frame):
    info = frame['info']
    frame_obj, _ = FrameNet.objects.update_or_create(
        eng_name=info['eng_name'].strip(),
        chi_name=info['chi_name'].strip(),
        description=info['description'],
        fid=info['fid'],
    )
    for fe in frame['core_fes']:
        frame_obj.frame_elements.add(
            FrameElement.objects.update_or_create(
                eng_name=fe['eng_name'].strip(),
                chi_name=fe['chi_name'].strip(),
                description=fe['description'],
                abbr=fe['abbr'],
                fe_type='CORE'
            )[0]
        )
    for fe in frame['noncore_fes']:
        frame_obj.frame_elements.add(
            FrameElement.objects.update_or_create(
                eng_name=fe['eng_name'].strip(),
                chi_name=fe['chi_name'].strip(),
                description=fe['description'],
                abbr=fe['abbr'],
                fe_type='NON_CORE'
            )[0]
        )


def insert_lu(fname, lus):
    try:
        frame_obj = FrameNet.objects.get(eng_name=fname.strip())
        for lu in lus:
            pos = list(pseg.cut(lu))[0].flag
            LexUnit.objects.update_or_create(
                name=lu.strip(),
                pos=pos.strip(),
                frame=frame_obj
            )
    except:
        print('insert_lu %s, %s failed' % (fname, lus))

if __name__ == '__main__':
    with open('data/CFN_Frames.json', encoding='utf8') as f:
        frames = json.load(f)
    fname = set()
    for fid, frame in frames.items():
        frame['info']['fid'] = fid
        if frame['info']['eng_name'] not in fname:
            insert_frame(frame)
        else:
            print(frame['info']['eng_name'], 'Duplicate Frame, ignored')
        fname.add(frame['info']['eng_name'])

    with open('data/CFN_Expand.json', encoding='utf8') as f:
        frames = json.load(f)
        for fname, lus in frames.items():
            insert_lu(fname, lus)
    
    print('%d Frame, %d LU added.' % (
        FrameNet.objects.all().count(),
        LexUnit.objects.all().count(),
    ))
