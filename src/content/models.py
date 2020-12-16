import hashlib
import logging
import os
import random

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from general import fields as gen_field

from django.utils.translation import ugettext as _
# Create your models here.
from geoposition.fields import GeopositionField

from general.functions import path_and_rename
from general.tasks import image_thumb_resize_general
from timeopt import settings
from timeopt.celery import app
from userprofile.models import Profile
from .tasks import create_location_user_locations,create_location_distance_locations
from django.db.models import signals, Q


class ExcelDocument(models.Model):
   excelfile = models.FileField(upload_to='documents/excel')
   date = models.DateTimeField(auto_now_add=True)

class Settings(models.Model):
    title = models.CharField(max_length=255)
    main_plan = models.BooleanField(default=False)
    sub_plan = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


class CompanyInformation(models.Model):
    active = models.BooleanField(unique=True)
    company_name = models.CharField(max_length=255)
    main_email = models.EmailField()
    task_status_email = models.EmailField(blank=True,null=True)
    # position = GeopositionField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.company_name

class Employee(models.Model):
    profile = models.OneToOneField('userprofile.Profile',blank=True,null=True,editable=False)
    status = models.BooleanField(default=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=path_and_rename,blank=True,null=True,max_length=500)
    address = models.TextField(blank=True,null=True)
    email = models.EmailField(max_length=255,unique=True)
    password = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.first_name
    def get_employee_work_days(self):
        em_wds = EmployeeWorkDay.objects.filter(employee=self)
        return em_wds
    def get_employee_work_day(self,day):
        em_wd = EmployeeWorkDay.objects.filter(employee=self,day=day).first()
        return em_wd

    def get_41_41_thumb(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        width = 41
        height = 41
        new_image_url = "{}-thumb-{}x{}.{}".format(self.image.url.rsplit('.', 1)[0], width, height,
                                                   self.image.url.rsplit('.', 1)[1])
        if os.path.exists(BASE_DIR+new_image_url):
            pass
        else:
            new_image_url = self.image.url
        return new_image_url
    def clean(self, *args, **kwargs):
        password = self.password
        if len(password) < 8:
            raise ValidationError('Password must be minimum 8 character')
        if self.pk is None:
            if User.objects.filter(Q(email=self.email)|Q(username=self.email)):
                raise ValidationError(_("This email already use"))
            else:
                super(Employee, self).save(*args, **kwargs)
        else:
            if User.objects.exclude(pk=self.profile.user.pk).filter(Q(email=self.email)|Q(username=self.email)):
                raise ValidationError(_("This email already use"))
            else:
                super(Employee, self).save(*args, **kwargs)



def user_save(sender, instance, created, signal, *args, **kwargs):
    if created:
        if instance.is_superuser  or instance.is_staff:
            user_obj = User.objects.get(pk=instance.pk)
            profile_obj = Profile(user=user_obj,type='admin-person')
            profile_obj.save()
        else:
            user_obj = User.objects.get(pk=instance.pk)
            profile_obj = Profile(user=user_obj,type='employee-person')
            profile_obj.save()
    else:
        if instance.is_superuser or instance.is_staff:
            user_obj = User.objects.get(pk=instance.pk)
            profile_obj = Profile.objects.filter(user=user_obj).first()
            if profile_obj:
                employee_obj = Employee.objects.filter(profile=profile_obj).first()
                if employee_obj:
                    instance.first_name = employee_obj.first_name
                    instance.last_name = employee_obj.last_name
                    # instance.first_name = employee_obj.e
                else:
                    profile_obj.type='admin-person'
                    profile_obj.save()


signals.post_save.connect(user_save, sender=User)

def employee_post_save(sender, instance, created, signal, *args, **kwargs):
    random_string = str(random.random()).encode('utf8')
    salt = hashlib.sha1(random_string).hexdigest()[:5]

    salted = (salt + instance.email).encode('utf8')

    # activation_key = hashlib.sha1(salted).hexdigest()
    #
    # key_expires = datetime.datetime.today() + datetime.timedelta(1)
    password = make_password(instance.password, salt=salt)
    if created:
        if instance.image:
            # image_thumb_resize_general(instance.image.url,41,41).delay()
            image_thumb_resize_general.delay(instance.image.url,41,41)
        user_obj = User(first_name=instance.first_name, last_name=instance.last_name, email=instance.email, username=instance.email, password=password,
                    is_active=True, is_staff=False, is_superuser=False)
        user_obj.save()
        instance.profile=Profile.objects.get(user=user_obj)
        instance.profile.address = instance.address
        instance.profile.image = instance.image
        instance.profile.save()
    elif not created:

        user_obj = User.objects.get(pk=instance.profile.user.pk)
        user_obj.first_name = instance.first_name
        user_obj.last_name = instance.last_name
        user_obj.username = instance.email
        user_obj.email = instance.email

        user_obj.password = password
        user_obj.save()
        instance.profile.address = instance.address
        instance.profile.image = instance.image
        instance.profile.save()
        # if User.objects.exclude(pk=instance)
        # Send verification email
        # create_location_user_locations.delay()


signals.post_save.connect(employee_post_save, sender=Employee)


DayCHOICES  = (
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
    (6, _("Saturday")),
    (7, _("Sunday")),
)


Hours_CHOICES  = (
    ('', _("Choose Hours")),
    (60, _("1 Hours")),
    (120, _("2 Hours")),
    (180, _("3 Hours")),
    (240, _("4 Hours")),
    (300, _("5 Hours")),
    (360, _("6 Hours")),
    (420, _("7 Hours")),
    (480, _("8 Hours")),
)


WorkTimesCHOICES  = (
    ('', _("Choose Week")),
    (1, _("Every Week")),
    (2, _("2 Week Times")),
    (4, _("4 Week Times")),
)

class WorkDay(models.Model):
    day = gen_field.IntegerRangeField(min_value=1, max_value=7,choices=DayCHOICES,unique=True)

    def __str__(self):
        return_val = ''
        for dc in DayCHOICES:
            if dc[0] == self.day:
                return_val = dc[1]
        return return_val
    def get_day_name(self):
        return_val = ''
        for dc in DayCHOICES:
            if dc[0] == self.day:
                return_val = dc[1]
        return return_val

class EmployeeWorkDay(models.Model):
    employee = models.ForeignKey("Employee")
    day = models.ForeignKey("WorkDay")
    minute = gen_field.IntegerRangeField(min_value=0, max_value=1440,default=0,choices=Hours_CHOICES)
    class Meta:
        unique_together = (("employee", "day"),)


    def get_plans_w_d(self,w,d):
        plan_employee_work = PlanEmployeeWork.objects.filter(employee=self.employee,week=w,day__id=d).first()
        return plan_employee_work


class Location(models.Model):
    our_company = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    minute = gen_field.IntegerRangeField(min_value=0, max_value=1440)
    work_times = gen_field.IntegerRangeField(min_value=1, max_value=4,default=1)
    image = models.ImageField(upload_to=path_and_rename,blank=True,null=True,max_length=500)
    address = models.TextField()
    position = GeopositionField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-our_company","-date",]
        verbose_name_plural = "Customers"
        verbose_name = "Customer"

    def get_41_41_thumb(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        width = 41
        height = 41
        new_image_url = "{}-thumb-{}x{}.{}".format(self.image.url.rsplit('.', 1)[0], width, height,
                                                   self.image.url.rsplit('.', 1)[1])
        if os.path.exists(BASE_DIR+new_image_url):
            pass
        else:
            new_image_url = self.image.url
        return new_image_url
from .tasks import send_verification_email



def customer_post_save(sender, instance,created, signal, *args, **kwargs):
    if created:
        if instance.image:
            # image_thumb_resize_general(instance.image.url,41,41).delay()
            image_thumb_resize_general.delay(instance.image.url,41,41)
    # if instance.status:
    if created:
        # print(signal)
        # Send verification email
        create_location_distance_locations.delay(instance.id)
    # if created:



signals.post_save.connect(customer_post_save, sender=Location)
#



class LocationDistance(models.Model):
    location1 = models.ForeignKey('Location',related_name='+')
    location2 = models.ForeignKey('Location',related_name='+')
    main_company = models.BooleanField(default=False)
    minute = models.IntegerField()
    distance = models.DecimalField(max_digits=19,decimal_places=2)
    def __str__(self):
        return "{} - {} - {} - {}".format(self.location1.name,self.location2.name,self.distance,self.minute)




class PlanEmployeeWork(models.Model):
    employee = models.ForeignKey("Employee")
    week = gen_field.IntegerRangeField(min_value=1, max_value=4)
    day = models.ForeignKey("WorkDay")
    minute = gen_field.IntegerRangeField(min_value=0, max_value=1440,default=0)
    difference_minute = gen_field.IntegerRangeField(min_value=0, max_value=1440,default=0)
    is_empty = models.BooleanField(default=True)
    is_full = models.BooleanField(default=False)
    class Meta:
        unique_together = (("employee", "week", "day"),)
    def get_locations(self):
        return LocationOrder.objects.filter(plan_employee_work=self).order_by('order_index')
    def get_last_location(self):
        return LocationOrder.objects.filter(plan_employee_work=self).order_by('order_index').last()
    def get_location(self,l_id):
        return LocationOrder.objects.filter(plan_employee_work=self,location_id=l_id).first()
    def __str__(self):
        return "{} - week={}   -  day={}".format(self.employee,self.week,self.day.day)



class LocationOrder(models.Model):
    plan_employee_work = models.ForeignKey(PlanEmployeeWork)
    order_index = gen_field.IntegerRangeField(min_value=1)
    location = models.ForeignKey('Location')
    main_process = models.BooleanField(default=False)
    def __str__(self):
        return "{} ----- {}. {}".format(self.plan_employee_work,self.order_index,self.location.name)



class PlanLog(models.Model):
    complated = models.BooleanField(default=False)
    rejcected = models.BooleanField(default=False)
    update_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.date.strftime("%d %b %Y %H:%M:%S")


class DistanceErrorLog(models.Model):
    location1 = models.ForeignKey('Location',related_name='+')
    location2 = models.ForeignKey('Location',related_name='+')
    # update_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return "{} - {} {} ".format(self.location1.name,self.location2.name,self.date.strftime("%d %b %Y %H:%M:%S"))



# class GeneralLog(models.Model):
#     title = models.BooleanField(default=False)
#     content = models.TextField()
#     type = models.CharField(max_length=255)
#     date = models.DateTimeField(auto_now_add=True)
#
#
#
# class Notification(models.Model):
#     title = models.BooleanField(default=False)
#     content = models.TextField()
#     type = models.CharField(max_length=255)
#     date = models.DateTimeField(auto_now_add=True)
#
#
# class ProfileNotification(models.Model):
#     profile = models.ForeignKey('userprofile.Profile',related_name='+')
#     notification = models.ForeignKey('Notification')
#     show_navbar = models.BooleanField(default=False)
#     read = models.BooleanField(default=False)





