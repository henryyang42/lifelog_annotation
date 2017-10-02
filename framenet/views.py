from django.shortcuts import get_object_or_404, render
from collections import defaultdict

from .api import *


def color_map(index):
    colors = ['red', 'green', 'blue', 'yellow', 'orange']
    return colors[index % len(colors)]


def annotate(request):
    s = request.GET.get('s', '')
    annotation_status = {
        'done_pct': 60,
        'invalid_pct': 10,
        'remaining_pct': 30,
        'done': 60,
        'invalid': 10,
        'remaining': 30,
    }
    sentence = tokenize(s)

    pre_annotations = []
    for i, token in enumerate(sentence):
        if token['frames']:
            pre_annotation = {'token': token,
                              'frames': [],
                              'i': token['token_i'],
                              'color': color_map(i)}
            for frame_name in token['frames']:
                frame = get_fn(eng_name=frame_name).as_dict()
                frame_elems_by_type = defaultdict(list)
                for fe in frame['frame_elements']:
                    frame_elems_by_type[fe['fe_type']].append(fe)
                frame['fe_by_type'] = frame_elems_by_type
                pre_annotation['frames'].append(frame)
            pre_annotations.append(pre_annotation)

    return render(request, 'annotate.html', {'annotation_status': annotation_status, 'sentence': sentence, 'pre_annotations': pre_annotations, 'id': 0})
