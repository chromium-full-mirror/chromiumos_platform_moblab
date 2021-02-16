import logging
import os

import django

import common

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

django.setup()
