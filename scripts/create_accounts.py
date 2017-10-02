import random
import string
from access_django import *
from django.contrib.auth.models import User
from annotate.models import *


def random_password(N=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(N))


def write_account_info(username, password, file):
    user = User.objects.get(username=username)
    entry_ct = Annotation.objects.filter(user=user).count()

    print('username: %s' % username, file=file)
    print('password: %s' % password, file=file)
    print('entry count: %d' % entry_ct, file=file)
    print('=======================', file=file)


def get_entries():
    entries = Entry.objects.all()
    golden_entries = entries[:100]
    for entry in golden_entries:
        entry.golden = True
        entry.save()
    normal_entries = Entry.objects.filter(golden=False)
    return normal_entries, golden_entries


def put_entries(entries, user):
    for entry in entries:
        Annotation.objects.create(entry=entry, user=user)


if __name__ == '__main__':
    n_accounts = 5

    normal_entries, golden_entries = get_entries()

    with open('accounts.txt', 'w') as f:
        username = 'annotator_golden'
        password = random_password()
        annotator_golden = User.objects.create_user(username, '', password)
        put_entries(golden_entries, annotator_golden)
        write_account_info(username, password, f)

        annotators = [annotator_golden]
        for i in range(n_accounts):
            username = 'annotator00%d' % (i + 1)
            password = random_password()
            annotator = User.objects.create_user(username, '', password)
            put_entries(normal_entries[i::n_accounts] + list(golden_entries), annotator)
            write_account_info(username, password, f)
            annotators.append(annotator)

    # Every annotator should have golden entries
    # Normal entries should be non-overlapping
    golden_set = set([entry.id for entry in golden_entries])
    normal_set = set([entry.id for entry in normal_entries])
    all_entries = set()
    for annotator in annotators:
        annotations = Annotation.objects.filter(user=annotator)
        entry_set = set([annotation.entry.id for annotation in annotations])
        assert(entry_set & golden_set == golden_set)
        assert(all_entries & entry_set == set())
        all_entries |= entry_set - golden_set

    assert(normal_set == all_entries)
