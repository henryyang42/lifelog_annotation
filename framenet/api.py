from django.http import HttpResponse, JsonResponse
from .models import *
import jieba.posseg as pseg


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
