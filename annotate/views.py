from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from framenet.api import *
from datetime import datetime
import json
from collections import defaultdict
from django.conf import settings
from django.contrib.auth.decorators import login_required


def color_map(index):
    colors = ['red', 'green', 'blue', 'yellow', 'orange']
    return colors[index % len(colors)]


def get_annotation_status(user):
    all_ct = Annotation.objects.filter(user=user).count()
    done_ct = Annotation.objects.filter(user=user, status=Annotation.DONE).count()
    pending_ct = Annotation.objects.filter(user=user, status=Annotation.PENDING).count()
    undone_ct = Annotation.objects.filter(user=user, status=Annotation.UNDONE).count()
    smoothing = 5000
    smct = len([ct for ct in [done_ct, pending_ct, undone_ct] if ct])
    return {
        'done_pct': done_ct and (done_ct + smoothing) / (all_ct + smct * smoothing) * 100,
        'pending_pct': pending_ct and (pending_ct + smoothing) / (all_ct + smct * smoothing) * 100,
        'remaining_pct': undone_ct and (undone_ct + smoothing) / (all_ct + smct * smoothing) * 100,
        'done': done_ct,
        'pending': pending_ct,
        'remaining': undone_ct,
    }


def auth_required(view):
    """A decorator to ensure user has login."""
    def f(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    return f


@login_required(login_url='/annotation/login')
def annotate(request):
    user = request.user
    annotation_status = get_annotation_status(user)
    Anno = Annotation
    if request.method == 'GET':
        id_ = request.GET.get('id')
        if id_:
            entry = get_object_or_404(Entry, id=id_)
            annotation = Annotation.objects.get(user=user, entry=entry)
        else:
            if annotation_status['remaining']:
                annotation = Annotation.objects.filter(user=user, status=Annotation.UNDONE)[0]
                entry = annotation.entry
            else:
                all_finished = True
                return render(request, 'annotate_entry.html', locals())

        # pre_annotated_result
        pa = {
            'checkEvent': 'notEvent',
            'imgDesc': '',
            'triples': [{'eventType': 'explicit', 'subject': '我', 'object': '', 'predicate': '', 'time': '發文時間'}],
            'frames': {},
            'frames_raw': {}}

        if annotation.annotation:
            try:
                pa = json.loads(annotation.annotation)
            except:
                pass
        print(annotation.id, annotation.annotation)

        print(pa)
        pre_annotations = []
        sentence = json.loads(entry.preprocessed_content)
        if 'tokens' in sentence:
            sentence = sentence['tokens']
        for i, token in enumerate(sentence):
            if token['frames']:
                pre_annotation = {'token': token,
                                  'frames': [],
                                  'i': token['token_i'],
                                  'color': color_map(i)}
                for frame_name in token['frames']:
                    frame = get_fn(eng_name=frame_name).as_dict()
                    annotated_frame = pa['frames'].get(str(token['token_i']), {})
                    if annotated_frame and annotated_frame.get('fname') == frame_name:
                        frame['selected'] = True
                    frame_elems_by_type = defaultdict(list)
                    for fe in frame['frame_elements']:
                        if annotated_frame and annotated_frame.get('fname') == frame_name:
                            fe['value'] = annotated_frame['fe'].get(fe['eng_name'], '')
                        frame_elems_by_type[fe['fe_type']].append(fe)
                    frame['fe_by_type'] = frame_elems_by_type
                    pre_annotation['frames'].append(frame)
                pre_annotations.append(pre_annotation)

        return render(request, 'annotate_entry.html', locals())

    elif request.method == 'POST':
        POST = request.POST

        entry = get_object_or_404(Entry, id=POST['id'])
        annotation = get_object_or_404(Annotation, user=user, entry=entry)
        annotated_result = {
            'user': POST['user'],
            'id': POST['id'],
            'checkEvent': POST['checkEvent'],
            'imgDesc': POST.get('imgDesc'),
            'triples': [],
            'frames': {},
            'frames_raw': {}
        }

        for key in [key for key in POST.keys() if key.startswith('eventType')]:
            tid = key.replace('eventType', '')
            print(tid)
            triple = {}
            for attr in ['eventType', 'subject', 'object', 'predicate', 'time']:
                triple[attr] = POST[attr + tid]
            annotated_result['triples'].append(triple)

        for k, v in POST.items():
            if v:
                print(k, v)

                if '-' in k:
                    annotated_result['frames_raw'][k] = v

                    ksplit = k.split('-')
                    if ksplit[0] == 'select':
                        token_i = ksplit[1]
                        frame = annotated_result['frames'].get(token_i, {'fe': {}})
                        frame['fname'] = v.split('-')[1]
                        annotated_result['frames'][token_i] = frame
                    elif len(ksplit) == 3:
                        token_i = ksplit[0]
                        frame = annotated_result['frames'].get(token_i, {'fe': {}})
                        fe = ksplit[2]
                        frame['fe'][fe] = v
                        annotated_result['frames'][token_i] = frame

        if POST['checkEvent'] == 'pass':
            annotation.status = Annotation.PENDING
        else:
            annotation.status = Annotation.DONE
        annotation.raw = json.dumps(POST, ensure_ascii=False)
        annotation.annotation = json.dumps(annotated_result, ensure_ascii=False)
        annotation.update_time = datetime.now()
        annotation.save()
        print(annotation.id, annotation.annotation)

        return redirect('/annotation/')


@login_required(login_url='/annotation/login')
def list_sentence(request):
    user = request.user
    status = request.GET.get('status')
    page = request.GET.get('page')

    anno_list = Annotation.objects.filter(user=user).order_by('-update_time')
    if status in [Annotation.DONE, Annotation.UNDONE, Annotation.PENDING]:
        anno_list = anno_list.filter(status=status)

    paginator = Paginator(anno_list, 100)  # Show 100 contacts per page

    try:
        annotations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        annotations = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        annotations = paginator.page(paginator.num_pages)
    Anno = Annotation
    annotation_status = get_annotation_status(user)
    return render(request, 'list_sentence.html', locals())
