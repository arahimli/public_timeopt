from django.test import TestCase

# Create your tests here.
from django.db.models import Q
from celery import shared_task
import pandas as pd

from content.models import LocationDistance


@shared_task
def calc_weekly(exc_list):
    loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).order_by('minute')
    week_dtf = pd.DataFrame.from_records(loc_destinations)
    weekly_table = week_dtf.groupby()
