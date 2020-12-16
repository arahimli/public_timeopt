from django.contrib.admin.widgets import AdminFileWidget
from django.utils import timezone
import os
from uuid import uuid4

from django.utils.datetime_safe import datetime
from django.utils.safestring import mark_safe


class ImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append(('<a target="_blank" href="%s">'
                           '<img src="%s" height="200" title="%s"/></a> '
                           % (value.url, value.url, value.name)))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))




def path_and_rename(instance, filename):
    now = datetime.now()
    upload_to = 'photos/{}/{}/{}'.format(now.year,now.month,now.day)
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)



def get_name_and_ext(str):
    new = str.split('.')
    name = ''
    ext = ''
    if len(new) == 1:
        ext = new[-1]
    else:
        i = 0
        for x in new:
            i+=1
            if i!=len(new):
                if i==1:
                    name+=x
                else:
                    name+='.'+x


    print (name)
    print (ext)