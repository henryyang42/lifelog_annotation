import json

import jieba.posseg as pseg

from access_django import *
from framenet.api import *
from annotate.models import *

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


def add_frames(tokens):
    tokens_ = []
    for i, tok in enumerate(tokens):
        tokens_.append({
            'token': tok['token_cn'],
            'pos': tok['pos'],
            'frames': [lu['frame'] for lu in find_lu(name=tok['token_cn'])],
            'token_i': i
        })
    return tokens_


if __name__ == '__main__':
    with open('data/diary_frames_cn.json') as f:
        frames = json.load(f)

    for i, frame in enumerate(frames):
        preprocessed_content = {'tokens': add_frames(frame['tokens'])}
        Entry.objects.create(
            content=frame['content_cn'],
            raw=json.dumps(frame, ensure_ascii=False),
            preprocessed_content=json.dumps(preprocessed_content, ensure_ascii=False),
            author='楊基振',
            source_type=Entry.DIARY,
            source_id=frame['id'],
        )
        print('{}/{}'.format(i + 1, len(frames)), end='\r')
