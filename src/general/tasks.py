
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery.task import task
from celery import shared_task,current_task




from PIL import Image


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@shared_task
def image_thumb_resize_general(url,width,height):
    img = Image.open(BASE_DIR+url)
    # img.show()
    img.thumbnail((width,height))
    # img.save('Glacier-National-Park-US-thumb.jpg')
    new_img = img.resize((width,height))
    type = url.rsplit('.', 1)[1]
    if str(type).lower() == 'jpg':
        type = "JPEG"
    new_image_url = BASE_DIR+"{}-thumb-{}x{}.{}".format(url.rsplit('.', 1)[0],width,height,url.rsplit('.', 1)[1])
    new_img.save(new_image_url, str(type).upper(), optimize=True)
    return True