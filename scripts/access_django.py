import os
import sys
import django


sys.path.append(os.getcwd())
sys.path.append(os.path.pardir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lifelog_annotation.settings")
django.setup()
