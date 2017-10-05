import json
import collections
import jieba.posseg as pseg

from access_django import *
from framenet.api import *
from annotate.models import *
import os.path

file_word2frame = 'data/word2frame.json'
word2frame = collections.defaultdict(set)
if os.path.isfile(file_word2frame):
    with open(file_word2frame, encoding='utf8') as f:
        for k, v in json.load(f).items():
            word2frame[k] = set(v)
else:
    for lu in LexUnit.objects.all():
        word2frame[lu.name].add(lu.frame.eng_name)
    with open(file_word2frame, 'w', encoding='utf8') as f:
        f.write(json.dumps({k: list(v) for k, v in word2frame.items()}, ensure_ascii=False))
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

def find_lu_fast(name):
      return list(word2frame[name])


def add_frames_fast(tokens):
    tokens_ = []
    for i, tok in enumerate(tokens):
        tokens_.append({
            'token': tok['token_cn'],
            'pos': tok['pos'],
            'frames': find_lu_fast(name=tok['token_cn']),
            'token_i': i
        })
    return tokens_


if __name__ == '__main__':
    with open('data/diary_frames_cn.json', encoding='utf8') as f:
        frames = json.load(f)

    for i, frame in enumerate(frames):
        preprocessed_content = {'tokens': add_frames_fast(frame['tokens'])}
        Entry.objects.create(
            content=frame['content_cn'],
            raw=json.dumps(frame, ensure_ascii=False),
            preprocessed_content=json.dumps(preprocessed_content, ensure_ascii=False),
            author='楊基振',
            source_type=Entry.DIARY,
            source_id=frame['id'],
        )
        print('{}/{}'.format(i + 1, len(frames)), end='\r')
