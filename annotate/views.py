from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from framenet.api import *
from framenet.models import *
from datetime import datetime
import json
from collections import defaultdict
from django.conf import settings
from django.contrib.auth.decorators import login_required
import logging
import jieba.posseg as pseg
logger = logging.getLogger(__name__)


def get_annotation_status(user):
    all_ct = Annotation.objects.filter(user=user).count()
    done_ct = Annotation.objects.filter(user=user, status=Annotation.DONE).count()
    pending_ct = Annotation.objects.filter(user=user, status=Annotation.PENDING).count()
    undone_ct = Annotation.objects.filter(user=user, status=Annotation.UNDONE).count()
    smoothing = 300
    smct = len([ct for ct in [done_ct, pending_ct, undone_ct] if ct])
    return {
        'done_pct': done_ct and (done_ct + smoothing) / (all_ct + smct * smoothing) * 100,
        'pending_pct': pending_ct and (pending_ct + smoothing) / (all_ct + smct * smoothing) * 100,
        'remaining_pct': undone_ct and (undone_ct + smoothing) / (all_ct + smct * smoothing) * 100,
        'done': done_ct,
        'pending': pending_ct,
        'pass': pending_ct,
        'remaining': undone_ct,
        'undone': undone_ct
    }


def add_lu(name, fid):
    try:
        pos = list(pseg.cut(name))[0].flag
        frame = FrameNet.objects.get(fid=fid)
        LexUnit.objects.create(frame=frame, name=name, pos=pos)
    except:
        pass


def get_pre_annotations(sentence, pa={'frames': {}}):
    pre_annotations = []
    for i, token in enumerate(sentence):
        if token['frames']:
            pre_annotation = {'token': token,
                              'frames': [],
                              'i': token['token_i']}
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

    return pre_annotations


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
        logger.info('%s ANNOTATIING annotation.id=%s' % (user, annotation.id))
        # pre_annotated_result
        pa = {
            'checkEvent': 'notEvent',
            'triples': [{'eventType': 'explicit', 'subject': entry.author, 'object': '', 'predicate': '', 'time': '發文時間'}],
            'frames': {},
            'frames_raw': {}}

        if annotation.annotation:
            try:
                pa = json.loads(annotation.annotation)
            except:
                pass

        print(pa)
        sentence = {}
        try:
            sentence = json.loads(annotation.preprocessed_content)
        except:
            pass

        sentence = sentence.get('tokens', [])
        pre_annotations = get_pre_annotations(sentence, pa)

        return render(request, 'annotate_entry.html', locals())

    elif request.method == 'POST':
        POST = request.POST
        logger.info('%s POSTED %s' % (user, json.dumps(request.POST)))
        entry = get_object_or_404(Entry, id=POST['id'])
        annotation = get_object_or_404(Annotation, user=user, entry=entry)
        annotated_result = {
            'author': POST['author'],
            'id': POST['id'],
            'checkEvent': POST['checkEvent'],
            'imgDescEnvironment': POST.get('imgDescEnvironment'),
            'imgDescIntention': POST.get('imgDescIntention'),
            'imgDescConnection': POST.get('imgDescConnection'),
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
        logger.info('%s UPDATED annotation.id=%s annotation.annotation=%s' % (user, annotation.id, annotation.annotation))

        if 'add_lu' in POST.keys():
            custom_lu_word = POST.get('custom_lu_word', '')
            custom_lu_frame = POST.get('custom_lu_frame', '')
            if custom_lu_word and custom_lu_frame:
                add_lu(custom_lu_word, custom_lu_frame)
                preprocessed_content = json.loads(annotation.preprocessed_content)
                targets = preprocessed_content.get('targets', []) + [custom_lu_word]
                tokens = add_frames_with_targets(annotation.entry.content, targets + [annotation.entry.author])
                annotation.preprocessed_content = json.dumps({'tokens': tokens, 'targets': targets}, ensure_ascii=False)
                annotation.save()
                logger.info('%s ADD lu.name=%s lu.frame.fid=%s' % (user, custom_lu_word, custom_lu_frame))
            return redirect('/annotation/?id=%d' % entry.id)
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


@login_required(login_url='/annotation/login')
def progress(request):
    user_progress = []
    status = {
        'not_event_cost': 0.0,
        'has_event_cost': 0.0,
        'has_event_media_cost': 0.0,
        'anno_done_cost': 0.0,
        'pass_cost': 0,
        'not_event': 0,
        'has_event': 0,
        'has_event_media': 0,
        'anno_done': 0,
        'pass': 0,
        'undone': 0
    }
    for user in User.objects.all():
        if 'annotator' not in user.username:
            continue
        annotation_status = get_annotation_status(user)
        annotation_status['has_event_media'], annotation_status['has_event'], annotation_status['not_event'] = 0, 0, 0
        for annotation in Annotation.objects.filter(user=user, status=Annotation.DONE):
            try:
                anno = json.loads(annotation.annotation)
                if anno['checkEvent'] == 'hasEvent':
                    if annotation.entry.media:
                        annotation_status['has_event_media'] += 1
                    else:
                        annotation_status['has_event'] += 1
                elif anno['checkEvent'] == 'notEvent':
                    annotation_status['not_event'] += 1
            except:
                pass
        annotation_status['has_event_media_cost'] = annotation_status['has_event_media'] * 9.0
        annotation_status['has_event_cost'] = annotation_status['has_event'] * 7.0
        annotation_status['not_event_cost'] = annotation_status['not_event'] * 1.5
        annotation_status['pass_cost'] = annotation_status['pass'] * 1.5
        annotation_status['anno_done'] = annotation_status['has_event'] + annotation_status['not_event'] + annotation_status['pass']
        annotation_status['anno_done_cost'] = annotation_status['has_event_media_cost'] + annotation_status['has_event_cost'] + annotation_status['not_event_cost'] + annotation_status['pass_cost']
        for key in status.keys():
            status[key] += annotation_status[key]
        user_progress.append((user, annotation_status))

    Anno = Annotation
    return render(request, 'progress.html', locals())


@login_required(login_url='/annotation/login')
def make_framenet(request):
    user = request.user
    if request.method == 'POST':
        annotation = get_object_or_404(Annotation, id=request.POST['annotation_id'])
        targets = json.loads(request.POST['targets']) + [annotation.entry.author]
        tokens = add_frames_with_targets(annotation.entry.content, targets)

        annotation.preprocessed_content = json.dumps({'tokens': tokens, 'targets': targets}, ensure_ascii=False)
        annotation.save()
        sentence = tokens
        pre_annotations = get_pre_annotations(sentence)
        return render(request, 'annotate_frame.html', locals())


@login_required(login_url='/annotation/login')
def download_annotation(request):
    user = request.user
    annotated_entry = []
    username = request.GET.get('user', user.username)
    user = get_object_or_404(User, username=username)
    error = 0
    for annotation in Annotation.objects.filter(user=user, status__in=[Annotation.DONE, Annotation.PENDING]):
        preprocessed_content = {}
        annotation_ = {}
        try:
            annotation_ = json.loads(annotation.annotation)
        except:
            error += 1
        try:
            preprocessed_content = json.loads(annotation.preprocessed_content)
        except:
            pass

        annotated_entry.append({
            'preprocessed_content': preprocessed_content,
            'annotation': annotation_})

    status = get_annotation_status(user)
    summary = {k: status[k] for k in ['done', 'undone', 'pass']}
    summary['error'] = error

    response = HttpResponse(json.dumps({'annotated_entry': annotated_entry, 'summary': summary}, ensure_ascii=False), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="%s.json"' % user.username
    return response
