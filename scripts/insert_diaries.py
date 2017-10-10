import json
import collections
import jieba.posseg as pseg

from access_django import *
from framenet.api import *
from annotate.models import *
import os.path

"""
{
  "event":[],
  "content_cn":"今天是俞董事葬礼",
  "content":"今天是俞董事葬禮",
  "participant":[
    {
      "token":"俞董事",
      "index":3
    }
  ],
  "place":[

  ],
  "time":" 1944年（民33年，34歲）   10月7日　土 ",
  "relative_time":[
    {
      "token":"今天",
      "index":0
    }
  ],
  "id":0,
  "tokens":[
    {
      "label":"TIME",
      "pos":"Nd",
      "token":"今天",
      "token_cn":"今天",
      "index":0
    },
    {
      "label":"O",
      "pos":"SHI",
      "token":"是",
      "token_cn":"是",
      "index":1
    },
    ...
  ]
}
"""


if __name__ == '__main__':
    with open('data/diary_frames_cn.json', encoding='utf8') as f:
        frames = json.load(f)

    for i, frame in enumerate(frames):
        Entry.objects.create(
            content='楊基振：' + frame['content_cn'],
            raw=json.dumps(frame, ensure_ascii=False),
            author='楊基振',
            source_type=Entry.DIARY,
            source_id=frame['id'],
        )
        print('{}/{}'.format(i + 1, len(frames)), end='\r')
