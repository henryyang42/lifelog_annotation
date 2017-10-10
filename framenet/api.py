from django.http import HttpResponse, JsonResponse
from .models import *
import jieba.posseg as pseg
from itertools import chain


def find_lu(**kwargs):
    return [lu.as_dict() for lu in LexUnit.objects.filter(**kwargs)]


def lu(request):
    name = request.GET.get('name', '')
    lus = find_lu(name=name)
    return JsonResponse(lus, safe=False)


def get_fn(**kwargs):
    try:
        return FrameNet.objects.get(**kwargs)
    except:
        return None


def framenet(request):
    name = request.GET.get('name', '')
    frame = get_fn(eng_name=name)
    if frame:
        frame = frame.as_dict()
    else:
        frame = {}
    return JsonResponse(frame, safe=False)


def tokenize(s):
    tokens = []
    for i, tok in enumerate(pseg.cut(s)):
        tokens.append({
            'token': tok.word,
            'pos': tok.flag,
            'frames': list(set([lu['frame'] for lu in find_lu(name=tok.word)])),
            'token_i': i
        })
    return tokens


def tokenize_s(request):
    s = request.GET.get('s', '')
    tokens = tokenize(s)
    return JsonResponse(tokens, safe=False)


def add_frames(tokens):
    tokens_ = []
    for i, tok in enumerate(tokens):
        token = tok.get('token_cn', '') or tok.get('token')
        tokens_.append({
            'token': token,
            'pos': tok.get('pos', ''),
            'frames': [lu['frame'] for lu in find_lu(name=token)],
            'token_i': i
        })
    return tokens_


def add_frames_with_targets(content, targets):
    content = [content]
    for target in targets:
        if not target:
            continue
        content_new = []
        for ctx in content:
            ctx_split = ctx.split(target)
            content_new += list(chain(*[[c, target] for c in ctx_split[:-1]])) + ctx_split[-1:]
        content = content_new
    tokens = []
    for tok in [t for t in content if t]:
        if tok not in targets:
            tokens += list(tok)
        else:
            tokens.append(tok)

    tokens_ = []
    for i, tok in enumerate(tokens):
        tokens_.append({
            'token': tok,
            'frames': [lu['frame'] for lu in find_lu(name=tok)] if tok in targets else [],
            'token_i': i
        })
    return tokens_
