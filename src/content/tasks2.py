import random
import string
import copy

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery.task import task
from celery import shared_task,current_task
import googlemaps
from datetime import datetime

# from content.models import LocationDistance
from .main_functions import *
from .new_main import main_work_list as main_work_list_nm


@shared_task
def create_location_user_locations():
    from .models import Location
    from .models import LocationDistance
    locations = Location.objects.filter(status=True)
    # the list that will hold the bulk insert
    bulk_location_distances = []

    # # loop that list and make those game objects
    LocationDistance.objects.filter().delete()
    for location1 in locations:
        for location2 in locations:
            if location1.id == location2.id or location1.id > location2.id:
                pass
            else:
                new_location_distance = LocationDistance()
                if location2.our_company or location1.our_company:
                    new_location_distance.main_company=True
                if location2.our_company:
                    new_location_distance.location1 = location2
                    new_location_distance.location2 = location1
                else:
                    new_location_distance.location1 = location1
                    new_location_distance.location2 = location2
                # distance_2_point_o = distance_2_point(new_location_distance.location1,new_location_distance.location2)

                # new_location_distance.minute = distance_2_point_o[0]
                # new_location_distance.distance = distance_2_point_o[1]
                #
                distance_2_point_o = distance_2_point(
                    new_location_distance.location1.position.latitude,new_location_distance.location1.position.longitude,
                    new_location_distance.location2.position.latitude,new_location_distance.location2.position.longitude
                )
                # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                # print(distance_2_point_o[0])
                # print(distance_2_point_o[1])
                # print("location1 = ({},{})".format(new_location_distance.location1.position.latitude,new_location_distance.location1.position.longitude))
                # print("location2 = ({},{})".format(new_location_distance.location2.latitude,new_location_distance.location2.longitude))
                # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

                new_location_distance.minute = distance_2_point_o[0]
                new_location_distance.distance = distance_2_point_o[1]

                # add game to the bulk list
                bulk_location_distances.append(new_location_distance)

    # now with a list of game objects that want to be created, run bulk_create on the chosen model
    LocationDistance.objects.bulk_create(bulk_location_distances)
    print('******************************************************')
    print('{} distances created with success! '.format(len(bulk_location_distances)))
    print('******************************************************')
    return '{} distances created with success!'.format(len(bulk_location_distances))



@shared_task
def create_location_distance_locations(loc_id):
    from .models import Location
    from .models import LocationDistance
    locations = Location.objects.filter(status=True).exclude(id=loc_id)
    # the list that will hold the bulk insert
    bulk_location_distances = []

    # # loop that list and make those game objects
    # LocationDistance.objects.filter().delete()
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(loc_id)
    location1 = Location.objects.get(status=True,id=loc_id)
    print(location1.name)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # if location1.id > 0:
    for location2 in locations:
        new_location_distance = LocationDistance()
        if location2.our_company or location1.our_company:
            new_location_distance.main_company=True
        if location2.our_company:
            new_location_distance.location1 = location2
            new_location_distance.location2 = location1
        else:
            new_location_distance.location1 = location1
            new_location_distance.location2 = location2
        # distance_2_point_o = distance_2_point(new_location_distance.location1,new_location_distance.location2)

        # new_location_distance.minute = distance_2_point_o[0]
        # new_location_distance.distance = distance_2_point_o[1]
        #
        distance_2_point_o = distance_2_point(
            new_location_distance.location1.position.latitude,new_location_distance.location1.position.longitude,
            new_location_distance.location2.position.latitude,new_location_distance.location2.position.longitude
        )
        # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        # print(distance_2_point_o[0])
        # print(distance_2_point_o[1])
        # print("location1 = ({},{})".format(new_location_distance.location1.position.latitude,new_location_distance.location1.position.longitude))
        # print("location2 = ({},{})".format(new_location_distance.location2.latitude,new_location_distance.location2.longitude))
        # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

        new_location_distance.minute = distance_2_point_o[0]
        new_location_distance.distance = distance_2_point_o[1]

        # add game to the bulk list
        bulk_location_distances.append(new_location_distance)

    # now with a list of game objects that want to be created, run bulk_create on the chosen model
    LocationDistance.objects.bulk_create(bulk_location_distances)
    print('******************************************************')
    print('{} distances created with success! '.format(len(bulk_location_distances)))
    print('******************************************************')
    return True


@shared_task
def send_verification_email():
    UserModel = settings.AUTH_USER_MODEL
    try:
        print("****************************************************************")
        print("yes")
        print("****************************************************************")
    except:
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("no")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")


import string

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery import shared_task

@shared_task
def create_random_user_accounts1():
    for i in range(20):
        username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
        email = '{}@example.com'.format(username)
        password = get_random_string(50)
        User.objects.create_user(username=username, email=email, password=password)
    return '{} random users created with success!'.format(20)


@shared_task
def main_result_prepare_plan():
    from content.models import LocationDistance,Location,Employee,PlanEmployeeWork,LocationOrder,WorkDay,PlanLog
    customers = Location.objects.filter(status=True).order_by('id')
    week_2_employee_work_list = []
    week_4_employee_work_list = []
    for customers_item in customers:
        if customers_item.work_times == 2:
            week_2_employee_work_list.append(customers_item.id)
        if customers_item.work_times == 4:
            week_4_employee_work_list.append(customers_item.id)
    week_list = [1,2,3,4]
    day_list = [1,2,3,4,5,6,7]

    # 2week_employee_work_list = []
    bulk_plan_employee_work_list = []
    bulk_location_order = []
    # exc_list = []
    employees = Employee.objects.filter()
    locations = Location.objects.filter()
    work_days = WorkDay.objects.filter()
    week_list_i = 0
    PlanEmployeeWork.objects.filter().delete()
    try:
        for week_list_item in week_list:
            week_list_i += 1
            exc_list = []
            # if week_list_item in [1,2,4]:
            for day_list_item in day_list:
                for employee_item in employees:
                    if day_list_item in [x.day.day for x in employee_item.get_employee_work_days()]:
                        new_plan_employee_work = PlanEmployeeWork()
                        new_plan_employee_work.employee = employee_item
                        new_plan_employee_work.week = week_list_item
                        new_plan_employee_work.minute = employee_item.get_employee_work_day(day_list_item).minute
                        new_plan_employee_work.day = work_days.filter(day=day_list_item).first()
                        new_plan_employee_work.save()
                        opt_loc_destinations = main_work_list_nm(exc_list=exc_list,minute=employee_item.get_employee_work_day(day_list_item).minute)
                        opt_loc_destinations_i = 0
                        for opt_loc_destinations_item in opt_loc_destinations:
                            if opt_loc_destinations_i > 0:
                                new_location_order = LocationOrder()
                                exc_list.append(opt_loc_destinations_item)
                                new_location_order.plan_employee_work = copy.deepcopy(new_plan_employee_work)
                                new_location_order.order_index = copy.deepcopy(opt_loc_destinations_i)
                                new_location_order.location_id = copy.deepcopy(opt_loc_destinations_item)
                                new_location_order.save()
                                bulk_location_order.append(new_location_order)
                                # print('opt_loc_destinations_item = ')
                            opt_loc_destinations_i+=1

        complated = True
        rejcected = False
    except:
        complated = False
        rejcected = True
    print("------------------------------------- Loading..... --------------------------------------------------------")
    # exc_list = []
    # # print(result([], 300))
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).order_by('minute')
    # dest_list = []
    # for loc_destination_item in loc_destinations:
    #     dest_list.append(obj_to_dict_dest(loc_destination_item))
    # print("calculate_minute([1, 5, 11, 20, 21, 27, 29], 300,dest_list)= {} ".format(calculate_minute([1, 5, 11, 20, 21, 27, 29], 300,dest_list)))
    # print(exc_list)
    # print(bulk_location_order)
    # LocationOrder.objects.bulk_create(bulk_location_order)

    plan_obj = PlanLog.objects.filter(complated=False, rejcected=False).first()
    if plan_obj:
        plan_obj.rejcected = rejcected
        plan_obj.complated = complated
        plan_obj.save()
    else:
        PlanLog.objects.create(complated=complated, rejcected=rejcected)
    print("------------------------------------- Loaded --------------------------------------------------------")
    return '{} random users created with success!'.format(len(bulk_location_order))

