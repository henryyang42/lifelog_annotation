import random
import string
from access_django import *
from django.contrib.auth.models import User
from annotate.models import *

diary_gold_source_id = [53, 109, 144, 200, 203, 230, 255, 256, 317, 368, 398, 413, 421, 464, 525, 533, 558, 562, 572, 573, 576, 638, 657, 712, 730, 747, 750, 765, 811, 931, 936, 968, 990, 1029, 1035, 1190, 1229, 1280, 1295, 1380, 1449, 1465, 1475, 1518, 1586, 1596, 1643, 1653, 1701, 1740, 1801, 1879, 1922, 1943, 1983, 2044, 2087, 2108, 2129, 2132, 2155, 2260, 2334, 2360, 2407, 2424, 2446, 2461, 2510, 2551, 2648, 2670, 2689, 2746, 2883, 2964, 2965, 2988, 2997, 3004, 3083, 3188, 3342, 3409, 3439, 3454, 3527, 3694, 3815, 3913, 3973, 4399, 4444, 4478, 4489, 4547, 4566, 4609, 4662, 4664]
tweet_gold_source_id = [5, 71, 78, 168, 190, 291, 421, 550, 590, 728, 930, 960, 1221, 1255, 1267, 1321, 1383, 1713, 1791, 1869, 1998, 2055, 2676, 2717, 2817, 3723, 3888, 4154, 4209, 4214, 4355, 4398, 4559, 4601, 4620, 4675, 4708, 4755, 5851, 6292, 7116, 7208, 7265, 7353, 7381, 8426, 9864, 10857, 11226, 11298, 12034, 12066, 12192, 13005, 13409, 13613, 14576, 15747, 15823, 16736, 16766, 17222, 17475, 18426, 18825, 20534, 20821, 20982, 21167, 22721, 22749, 22992, 23200, 23318, 23401, 23877, 24075, 24212, 25046, 25517, 25576, 25688, 26099, 26718, 27282, 27313, 27330, 27451, 27517, 27648, 27728, 28007, 28257, 28581, 28791, 28798, 29177, 29512, 29674, 30145]

def random_password(N=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(N))


def write_account_info(username, password, file):
    user = User.objects.get(username=username)
    entry_ct = Annotation.objects.filter(user=user).count()

    print('username: %s' % username, file=file)
    print('password: %s' % password, file=file)
    print('entry count: %d' % entry_ct, file=file)
    print('=======================', file=file)


def get_entries(source_type):
    golden_entries = Entry.objects.filter(source_type=source_type, golden=True)
    normal_entries = Entry.objects.filter(source_type=source_type, golden=False)
    return normal_entries, golden_entries


def put_entries(entries, user):
    for entry in entries:
        Annotation.objects.create(entry=entry, user=user)


if __name__ == '__main__':
    for entry in Entry.objects.filter(source_type=Entry.DIARY, source_id__in=diary_gold_source_id):
        entry.golden = True
        entry.save()
    for entry in Entry.objects.filter(source_type=Entry.TWEET, source_id__in=tweet_gold_source_id):
        entry.golden = True
        entry.save()
    assert(Entry.objects.filter(source_type=Entry.TWEET, golden=True).count() == 100)
    assert(Entry.objects.filter(source_type=Entry.DIARY, golden=True).count() == 100)

    golden_accounts = 4
    diary_accounts = 2
    tweet_accounts = 6

    diary_normal, diary_golden = get_entries(Entry.DIARY)
    tweet_normal, tweet_golden = get_entries(Entry.TWEET)

    with open('accounts.txt', 'w') as f:
        diary_annotators = []
        for i in range(golden_accounts):
            username = 'diary_annotator_golden00%d' % (i + 1)
            password = random_password()
            diary_annotator_golden = User.objects.create_user(username, '', password)
            put_entries(diary_golden, diary_annotator_golden)
            write_account_info(username, password, f)
            diary_annotators.append(diary_annotator_golden)
            print('%s created' % username)

        for i in range(diary_accounts):
            username = 'diary_annotator00%d' % (i + 1)
            password = random_password()
            annotator = User.objects.create_user(username, '', password)
            put_entries(diary_normal[i::diary_accounts] + list(diary_golden), annotator)
            write_account_info(username, password, f)
            diary_annotators.append(annotator)
            print('%s created' % username)
        
        tweet_annotators = []
        for i in range(golden_accounts):
            username = 'tweet_annotator_golden00%d' % (i + 1)
            password = random_password()
            tweet_annotator_golden = User.objects.create_user(username, '', password)
            put_entries(tweet_golden, tweet_annotator_golden)
            write_account_info(username, password, f)
            tweet_annotators.append(tweet_annotator_golden)
            print('%s created' % username)

        for i in range(tweet_accounts):
            username = 'tweet_annotator00%d' % (i + 1)
            password = random_password()
            annotator = User.objects.create_user(username, '', password)
            put_entries(tweet_normal[i::tweet_accounts] + list(tweet_golden), annotator)
            write_account_info(username, password, f)
            tweet_annotators.append(annotator)
            print('%s created' % username)

    # Every annotator should have golden entries
    # Normal entries should be non-overlapping
    diary_golden_set = set([entry.id for entry in diary_golden])
    diary_normal_set = set([entry.id for entry in diary_normal])
    all_entries = set()
    for annotator in diary_annotators:
        annotations = Annotation.objects.filter(user=annotator)
        entry_set = set([annotation.entry.id for annotation in annotations])
        assert(entry_set & diary_golden_set == diary_golden_set)
        assert(all_entries & entry_set == set())
        all_entries |= entry_set - diary_golden_set

    assert(diary_normal_set == all_entries)

    tweet_golden_set = set([entry.id for entry in tweet_golden])
    tweet_normal_set = set([entry.id for entry in tweet_normal])
    all_entries = set()
    for annotator in tweet_annotators:
        annotations = Annotation.objects.filter(user=annotator)
        entry_set = set([annotation.entry.id for annotation in annotations])
        assert(entry_set & tweet_golden_set == tweet_golden_set)
        assert(all_entries & entry_set == set())
        all_entries |= entry_set - tweet_golden_set

    assert(tweet_normal_set == all_entries)

    url = 'http://nlg17.csie.ntu.edu.tw/annotation'
    with open('golden_info.txt', 'w') as f:
        print('Diary_Golden_Id:', file=f)
        print(str(diary_golden_set), file=f)
        print('========================', file=f)
        for id_ in diary_golden_set:
            print('%s/?id=%d' % (url, id_), file=f)

        print('Tweet_Golden_Id:', file=f)
        print(str(tweet_golden_set), file=f)
        print('========================', file=f)
        for id_ in tweet_golden_set:
            print('%s/?id=%d' % (url, id_), file=f)

