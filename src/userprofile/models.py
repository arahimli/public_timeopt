import uuid

from django.db import models

# Create your models here.
from django.utils import timezone
from django.utils.translation import ugettext as _

from timeopt import settings

ADMINTYPECHOICES = (
    ('admin-person', _("Admin")),
    ('employee-person', _("Employee")),
)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    image = models.ImageField(upload_to='profile_photos',blank=True,null=True,max_length=500)
    type = models.CharField(max_length=100,choices=ADMINTYPECHOICES,default='employee-person')
    address = models.TextField(blank=True,null=True)
    activation_key = models.CharField(max_length=40, blank=True,editable=False)
    reset_token_key = models.CharField(max_length=40, blank=True,editable=False)
    key_expires = models.DateTimeField(default=timezone.now(),blank=True,null=True,editable=False)
    reset_key_expires = models.DateTimeField(default=timezone.now(), blank=True, null=True,editable=False)
    def __str__(self):
        return "{} - {} {}".format(self.user.username,self.user.first_name,self.user.last_name,)