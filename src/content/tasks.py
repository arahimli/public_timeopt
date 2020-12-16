import os
import random
import random
import string
import copy

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.utils.crypto import get_random_string

from celery.task import task
from celery import shared_task,current_task
import googlemaps
from datetime import datetime

# from content.models import LocationDistance
from general.read_customer import read_customer_from_excel as general_read_customer_from_excel
# from .main_functions import *



@shared_task
def add_location_from_excel_list(url):
    from content.models import Location
    from geoposition import Geoposition
    import time
    all_list = general_read_customer_from_excel(url)
    # print(all_list)
    all_customer = Location.objects.filter()
    all_list_item_i = 0
    all_list_item_general_i = all_customer.count()
    if len(all_list):
        for all_list_item in all_list:
            all_list_item_general_i += 1
            if all_customer.filter(name=all_list_item[0],address=all_list_item[1]).count()==0:
                # print("all_customer.filter(name=all_list_item[0],address=all_list_item[1])")
                all_list_item_i+=1
                slip_time = 0.13 * all_list_item_general_i
                # if all_list_item_i > 100 and all_list_item_i <= 200 :
                #     time.sleep(1.5)
                # elif all_list_item_i > 200 and all_list_item_i <= 300 :
                #     time.sleep(2)
                # elif all_list_item_i > 300 and all_list_item_i <= 400 :
                #     time.sleep(2.5)
                # elif all_list_item_i > 400 and all_list_item_i <= 500 :
                #     time.sleep(3)
                # elif all_list_item_i > 500:
                #     time.sleep(3.5)
                if all_list_item_i < 400:
                    Location.objects.create(
                                            name=all_list_item[0],
                                            address=all_list_item[1],
                                            status = True,
                                            our_company = False,
                                            minute = all_list_item[3],
                                            work_times = all_list_item[2],
                                            position =  Geoposition(float(all_list_item[4]), float(all_list_item[5]))
                                            )
                    time.sleep(slip_time)
                # else:
                #     break

    return '{} customer created with success!'.format(all_list_item_i)


@shared_task
def create_location_user_locations():
    from .models import Location
    from .models import LocationDistance
    from .new_main import distance_2_point as nm_distance_2_point
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
                distance_2_point_o = nm_distance_2_point(
                    new_location_distance.location1.position.latitude,new_location_distance.location1.position.longitude,
                    new_location_distance.location2.position.latitude,new_location_distance.location2.position.longitude
                )
                # # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                # # print(distance_2_point_o[0])
                # # print(distance_2_point_o[1])
                # # print("location1 = ({},{})".format(new_location_distance.location1.position.latitude,new_location_distance.location1.position.longitude))
                # # print("location2 = ({},{})".format(new_location_distance.location2.latitude,new_location_distance.location2.longitude))
                # # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

                new_location_distance.minute = distance_2_point_o[0]
                new_location_distance.distance = distance_2_point_o[1]

                # add game to the bulk list
                bulk_location_distances.append(new_location_distance)

    # now with a list of game objects that want to be created, run bulk_create on the chosen model
    LocationDistance.objects.bulk_create(bulk_location_distances)
    # print('******************************************************')
    # print('{} distances created with success! '.format(len(bulk_location_distances)))
    # print('******************************************************')
    return '{} distances created with success!'.format(len(bulk_location_distances))



@shared_task
def create_location_distance_locations(loc_id):
    from django.db.models import Q
    from .models import Location
    from .models import LocationDistance , PlanEmployeeWork , LocationOrder, DistanceErrorLog
    from .new_main import distance_2_point as nm_distance_2_point
    locations = Location.objects.filter().exclude(id=loc_id)
    # the list that will hold the bulk insert
    bulk_location_distances = []
    # main_location = Location.objects.filter(our_company=True).first()

    # # loop that list and make those game objects
    # LocationDistance.objects.filter().delete()
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(loc_id)
    location1 = Location.objects.get(id=loc_id)
    # # print(location1.name)
    # # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # if location1.id > 0:
    for location2 in locations:
        # # print("LocationDistance.objects.filter(Q(location1=location1,location2=location2) | Q(location1=location2,location2=location1))={}".format(LocationDistance.objects.filter(Q(location1=location1,location2=location2) | Q(location1=location2,location2=location1)).count()))
        if LocationDistance.objects.filter(Q(location1=location1,location2=location2) | Q(location1=location2,location2=location1)).count() == 0:
        #     pass
        # else:
        #     # print("yeah")
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
            try:
                distance_2_point_o = nm_distance_2_point(
                    new_location_distance.location1.position.latitude,new_location_distance.location1.position.longitude,
                    new_location_distance.location2.position.latitude,new_location_distance.location2.position.longitude
                )
                # # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                # # print(distance_2_point_o[0])
                # # print(distance_2_point_o[1])
                # # print("location1 = ({},{})".format(new_location_distance.location1.position.latitude,new_location_distance.location1.position.longitude))
                # # print("location2 = ({},{})".format(new_location_distance.location2.latitude,new_location_distance.location2.longitude))
                # # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

                new_location_distance.minute = distance_2_point_o[0]
                new_location_distance.distance = distance_2_point_o[1]

                # add game to the bulk list
                new_location_distance.save()
                bulk_location_distances.append(copy.deepcopy(new_location_distance))
            except:
                DistanceErrorLog.objects.create(location1=location1,location2=location2)

    # now with a list of game objects that want to be created, run bulk_create on the chosen model
    # LocationDistance.objects.bulk_create(bulk_location_distances)

    print('******************************************************')
    print('{} distances created with success! '.format(len(bulk_location_distances)))
    print('******************************************************')
    # week_list = []


    # from content.new_main import calculate_minute_1times as nm_calculate_minute_1times
    # # print('##############################################################################################################')
    # if location1.work_times == 1:
    #     week_list = [1,2,3,4]
    #     for week_list_item in week_list:
    #         plan_emp_works_weeks = PlanEmployeeWork.objects.filter(week=week_list_item)
    #         plan_emp_works_weeks_i = 0
    #         opt_emp_work_id = 0
    #         opt_emp_work_loc_count = 0
    #         opt_emp_work_min_minute = -1
    #         opt_emp_work_list = []
    #         for plan_emp_works_weeks_item in plan_emp_works_weeks:
    #             plan_emp_works_weeks_item_locations = plan_emp_works_weeks_item.get_locations()
    #             plan_emp_works_weeks_item_locations_list = []
    #             for plan_emp_works_weeks_item_locations_item in plan_emp_works_weeks_item_locations:
    #                 plan_emp_works_weeks_item_locations_list.append(plan_emp_works_weeks_item_locations_item.location_id)
    #             if len(plan_emp_works_weeks_item_locations_list):
    #                 minute_r = nm_calculate_minute_1times(plan_emp_works_weeks_item_locations_list,loc_id,main_location.id,plan_emp_works_weeks_item.minute)
    #                 if minute_r[0] >= 0:
    #                     plan_emp_works_weeks_i += 1
    #                     if plan_emp_works_weeks_i == 1:
    #                         opt_emp_work_id = plan_emp_works_weeks_item.id
    #                         opt_emp_work_min_minute = minute_r[0]
    #                         opt_emp_work_loc_count = minute_r[1]
    #                     else:
    #                         if opt_emp_work_min_minute < minute_r[0] and opt_emp_work_loc_count < minute_r[1]:
    #                             opt_emp_work_min_minute = minute_r[0]
    #                             opt_emp_work_id = plan_emp_works_weeks_item.id
    #                             opt_emp_work_loc_count = minute_r[1]
    #         if opt_emp_work_id != 0 and opt_emp_work_min_minute >= 0:
    #             plan_emp_works_weeks_f = plan_emp_works_weeks.filter(id=opt_emp_work_id).first()
    #             last_loc = plan_emp_works_weeks_f.get_last_location()
    #             if last_loc:
    #                 last_loc_order = last_loc.order_index + 1
    #             else:
    #                 last_loc_order = 0
    #
    #             LocationOrder.objects.create(plan_employee_work=plan_emp_works_weeks_f,location=location1,order_index=last_loc_order,main_process=False)
    # elif location1.work_times == 2:
    #     work_list = [[1,2],[3,4]]
    #     for week_list in work_list:
    #         week_list_plan_emp_works_weeks_i = 0
    #         week_list_opt_emp_work_id = 0
    #         week_list_opt_emp_work_min_minute = -1
    #         week_list_opt_emp_work_list = []
    #         week_list_week_item = 1
    #         for week_list_item in week_list:
    #             week_list_plan_emp_works_weeks_i += 1
    #             plan_emp_works_weeks = PlanEmployeeWork.objects.filter(week=week_list_item)
    #             plan_emp_works_weeks_i = 0
    #             opt_emp_work_id = 0
    #             opt_emp_work_loc_count = 0
    #             opt_emp_work_min_minute = -1
    #             opt_emp_work_list = []
    #             for plan_emp_works_weeks_item in plan_emp_works_weeks:
    #                 plan_emp_works_weeks_item_locations = plan_emp_works_weeks_item.get_locations()
    #                 plan_emp_works_weeks_item_locations_list = []
    #                 for plan_emp_works_weeks_item_locations_item in plan_emp_works_weeks_item_locations:
    #                     plan_emp_works_weeks_item_locations_list.append(
    #                         plan_emp_works_weeks_item_locations_item.location_id)
    #                 if len(plan_emp_works_weeks_item_locations_list):
    #                     minute_r = nm_calculate_minute_1times(plan_emp_works_weeks_item_locations_list, loc_id,
    #                                                           main_location.id, plan_emp_works_weeks_item.minute)
    #                     if minute_r[0] >= 0:
    #                         plan_emp_works_weeks_i += 1
    #                         if plan_emp_works_weeks_i == 1:
    #                             opt_emp_work_id = plan_emp_works_weeks_item.id
    #                             opt_emp_work_min_minute = minute_r[0]
    #                             opt_emp_work_loc_count = minute_r[1]
    #                         else:
    #                             if opt_emp_work_min_minute < minute_r[0] and opt_emp_work_loc_count < minute_r[1]:
    #                                 opt_emp_work_min_minute = minute_r[0]
    #                                 opt_emp_work_id = plan_emp_works_weeks_item.id
    #                                 opt_emp_work_loc_count = minute_r[1]
    #
    #             if opt_emp_work_id != 0 and opt_emp_work_min_minute >= 0:
    #                 if week_list_plan_emp_works_weeks_i == 1:
    #                     week_list_opt_emp_work_id = opt_emp_work_id
    #                     week_list_opt_emp_work_min_minute = opt_emp_work_min_minute
    #                     week_list_week_item = week_list_item
    #                 else:
    #                     if week_list_opt_emp_work_min_minute > opt_emp_work_min_minute:
    #                         week_list_opt_emp_work_min_minute = opt_emp_work_min_minute
    #                         week_list_opt_emp_work_id = opt_emp_work_id
    #                         week_list_week_item = week_list_item
    #         if week_list_opt_emp_work_id != 0 and week_list_opt_emp_work_min_minute >= 0:
    #             plan_emp_works_weeks_f = PlanEmployeeWork.objects.filter(week=week_list_week_item).filter(
    #                 id=week_list_opt_emp_work_id).first()
    #             try:
    #                 last_loc = plan_emp_works_weeks_f.get_last_location()
    #                 if last_loc:
    #                     last_loc_order = last_loc.order_index + 1
    #                 else:
    #                     last_loc_order = 0
    #                 LocationOrder.objects.create(plan_employee_work=plan_emp_works_weeks_f,
    #                                              location=location1,
    #                                              order_index=last_loc_order,
    #                                              main_process=False)
    #             except:
    #                 pass
    # #
    # elif location1.work_times == 4:
    #     week_list = [1,2,3,4]
    #     week_list_plan_emp_works_weeks_i = 0
    #     week_list_opt_emp_work_id = 0
    #     week_list_opt_emp_work_min_minute = -1
    #     week_list_opt_emp_work_list = []
    #     week_list_week_item = 1
    #     for week_list_item in week_list:
    #         week_list_plan_emp_works_weeks_i += 1
    #         plan_emp_works_weeks = PlanEmployeeWork.objects.filter(week=week_list_item)
    #         plan_emp_works_weeks_i = 0
    #         opt_emp_work_id = 0
    #         opt_emp_work_loc_count = 0
    #         opt_emp_work_min_minute = -1
    #         opt_emp_work_list = []
    #         for plan_emp_works_weeks_item in plan_emp_works_weeks:
    #             plan_emp_works_weeks_item_locations = plan_emp_works_weeks_item.get_locations()
    #             plan_emp_works_weeks_item_locations_list = []
    #             for plan_emp_works_weeks_item_locations_item in plan_emp_works_weeks_item_locations:
    #                 plan_emp_works_weeks_item_locations_list.append(
    #                     plan_emp_works_weeks_item_locations_item.location_id)
    #             if len(plan_emp_works_weeks_item_locations_list):
    #                 minute_r = nm_calculate_minute_1times(plan_emp_works_weeks_item_locations_list, loc_id,
    #                                                       main_location.id, plan_emp_works_weeks_item.minute)
    #                 if minute_r[0] >= 0:
    #                     plan_emp_works_weeks_i += 1
    #                     if plan_emp_works_weeks_i == 1:
    #                         opt_emp_work_id = plan_emp_works_weeks_item.id
    #                         opt_emp_work_min_minute = minute_r[0]
    #                         opt_emp_work_loc_count = minute_r[1]
    #                     else:
    #                         if opt_emp_work_min_minute < minute_r[0] and opt_emp_work_loc_count < minute_r[1]:
    #                             opt_emp_work_min_minute = minute_r[0]
    #                             opt_emp_work_id = plan_emp_works_weeks_item.id
    #                             opt_emp_work_loc_count = minute_r[1]
    #         if opt_emp_work_id != 0 and opt_emp_work_min_minute >= 0:
    #             if week_list_plan_emp_works_weeks_i == 1:
    #                 week_list_opt_emp_work_id = opt_emp_work_id
    #                 week_list_opt_emp_work_min_minute = opt_emp_work_min_minute
    #                 week_list_week_item = week_list_item
    #             else:
    #                 if week_list_opt_emp_work_min_minute > opt_emp_work_min_minute:
    #                     week_list_opt_emp_work_min_minute = opt_emp_work_min_minute
    #                     week_list_opt_emp_work_id = opt_emp_work_id
    #                     week_list_week_item = week_list_item
    #     if week_list_opt_emp_work_id != 0:
    #         plan_emp_works_weeks_f = PlanEmployeeWork.objects.filter(week=week_list_week_item).filter(id=week_list_opt_emp_work_id).first()
    #         try:
    #             last_loc = plan_emp_works_weeks_f.get_last_location()
    #             if last_loc:
    #                 last_loc_order = last_loc.order_index + 1
    #             else:
    #                 last_loc_order = 0
    #             LocationOrder.objects.create(plan_employee_work=plan_emp_works_weeks_f,location=location1,order_index=last_loc_order,main_process=False)
    #         except:
    #             pass
    #
    print('##############################################################################################################')
    return True


@shared_task
def send_verification_email():
    UserModel = settings.AUTH_USER_MODEL
    try:
        pass
        # print("****************************************************************")
        # print("yes")
        # print("****************************************************************")
    except:
        pass
        # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        # print("no")
        # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")


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


from content.new_main import main_work_list as main_work_list_nm, exc_list_loc, sub_result1p1_seven


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
                        opt_loc_destinations = main_work_list_nm(exc_list=exc_list,minute=(employee_item.get_employee_work_day(day_list_item).minute-30))
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
                                # # print('opt_loc_destinations_item = ')
                                # print('************* opt_loc_destinations_i = {} *************'.format(opt_loc_destinations_i))
                            opt_loc_destinations_i += 1

        complated = True
        rejcected = False
    except:
        complated = False
        rejcected = True
    # print("------------------------------------- Loading..... --------------------------------------------------------")
    # exc_list = []
    # # # print(result([], 300))
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).order_by('minute')
    # dest_list = []
    # for loc_destination_item in loc_destinations:
    #     dest_list.append(obj_to_dict_dest(loc_destination_item))
    # # print("calculate_minute([1, 5, 11, 20, 21, 27, 29], 300,dest_list)= {} ".format(calculate_minute([1, 5, 11, 20, 21, 27, 29], 300,dest_list)))
    # # print(exc_list)
    # # print(bulk_location_order)
    # LocationOrder.objects.bulk_create(bulk_location_order)

    plan_obj = PlanLog.objects.filter(complated=False, rejcected=False).first()
    if plan_obj:
        plan_obj.rejcected = rejcected
        plan_obj.complated = complated
        plan_obj.save()
    else:
        PlanLog.objects.create(complated=complated, rejcected=rejcected)
    # print("------------------------------------- Loaded --------------------------------------------------------")
    return '{} random users created with success!'.format(len(bulk_location_order))


from content.new_main import main_work_list as main_work_list_nm
# from content.models import DayCHOICES
@shared_task
def main_result_prepare_plan_new():
    from content.models import DayCHOICES,Hours_CHOICES
    from content.models import LocationDistance,Location,Employee,PlanEmployeeWork,LocationOrder,WorkDay,PlanLog,CompanyInformation
    from content.new_main import calculate_minute_1times as nm_calculate_minute_1times
    from content.new_main import result1p1_seven as nm_result1p1_seven
    from django.utils.translation import ugettext as _
    from .new_main import ordered_locations as nm_ordered_locations
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
    # print("week_4_employee_work_list={}".format(week_4_employee_work_list))
    # print("week_2_employee_work_list={}".format(week_2_employee_work_list))
    # 2week_employee_work_list = []
    bulk_plan_employee_work_list = []
    bulk_location_order = []
    # exc_list = []
    employees = Employee.objects.filter()
    # locations = Location.objects.filter()
    work_days = WorkDay.objects.filter()
    week_list_i = 0
    main_loc = Location.objects.get(our_company=True)
    plan_obj_create = PlanLog.objects.create(complated=False, rejcected=False)
    PlanEmployeeWork.objects.filter().delete()
    try:
        for week_list_item in week_list:
            week_list_i += 1
            # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

            # # print("week_2_employee_work_list={}".format(week_2_employee_work_list))
            # # print("week_4_employee_work_list={}".format(week_4_employee_work_list))
            weekly_exc_list = exc_list_loc(copy.deepcopy(week_2_employee_work_list),2,week_list_item) + exc_list_loc(copy.deepcopy(week_4_employee_work_list),4,week_list_item)
            exc_list = weekly_exc_list
            # # print("weekly_exc_list={}".format(weekly_exc_list))
            # # print("week_2_employee_work_list={}".format(week_2_employee_work_list))
            # # print("week_4_employee_work_list={}".format(week_4_employee_work_list))
            # # print("exc_list_loc(week_2_employee_work_list,2,week_list_item)={}".format(exc_list_loc(copy.deepcopy(week_2_employee_work_list),2,week_list_item)))
            # # print("exc_list_loc(week_2_employee_work_list,4,week_list_item)={}".format(exc_list_loc(copy.deepcopy(week_4_employee_work_list),4,week_list_item)))
            # print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
            # if week_list_item in [1,2,4]:
            for day_list_item in day_list:
                for employee_item in employees:
                    if day_list_item in [x.day.day for x in employee_item.get_employee_work_days()]:
                        new_plan_employee_work = PlanEmployeeWork()
                        new_plan_employee_work.employee = employee_item
                        new_plan_employee_work.week = week_list_item
                        new_plan_employee_work.is_empty = True
                        new_plan_employee_work.minute = employee_item.get_employee_work_day(day_list_item).minute
                        new_plan_employee_work.difference_minute = new_plan_employee_work.minute
                        new_plan_employee_work.day = work_days.filter(day=day_list_item).first()
                        new_plan_employee_work.save()
            for Hours_CHOICES_item in Hours_CHOICES:
                if Hours_CHOICES_item[0]:
                    # # print("DayCHOICES_item[0]={}".format(Hours_CHOICES_item[0]))
                    employeeworks = PlanEmployeeWork.objects.filter(week=week_list_item,is_empty=True).filter(minute=Hours_CHOICES_item[0]).order_by('week','day__day')
                    # # print("employeeworks={}".format(employeeworks.count()))
                    while employeeworks.count()>0:
                        # opt_loc_destinations = main_work_list_nm(exc_list=exc_list,minute=Hours_CHOICES_item[0])
                        opt_loc_destinations = nm_result1p1_seven(exc_list=exc_list,minute=Hours_CHOICES_item[0])
                        if len(opt_loc_destinations) == 0:
                            break
                        # print("opt_loc_destinations={}".format(opt_loc_destinations))
                        # # print("len(opt_loc_destinations)={}".format(len(opt_loc_destinations)))
                        employeeworks_item_i = 0
                        for employeeworks_item in employeeworks[:len(opt_loc_destinations)]:
                            opt_loc_destinations_i = 0
                            ordered_opt_loc_destination_item = opt_loc_destinations[employeeworks_item_i]
                            # ordered_opt_loc_destination_item = nm_ordered_locations(main_loc.id,opt_loc_destinations[employeeworks_item_i])
                            for opt_loc_destinations_item in ordered_opt_loc_destination_item[1:]:
                                new_location_order = LocationOrder()
                                exc_list.append(opt_loc_destinations_item)
                                new_location_order.plan_employee_work = copy.deepcopy(employeeworks_item)
                                new_location_order.order_index = copy.deepcopy(opt_loc_destinations_i)
                                new_location_order.location_id = copy.deepcopy(opt_loc_destinations_item)
                                new_location_order.main_process = True
                                new_location_order.save()
                                bulk_location_order.append(new_location_order)
                                # print('opt_loc_destinations[employeeworks_item_i] = {}'.format(opt_loc_destinations[employeeworks_item_i]))
                                opt_loc_destinations_i+=1
                            # # print("task.py 542 - employeeworks_item = {}".format(employeeworks_item))
                            # employeeworks_item.difference_minute = employeeworks_item.minute - nm_calculate_minute_1times(ordered_opt_loc_destination_item,loc_id,main_location.id,plan_emp_works_weeks_item.minute)
                            employeeworks_item.difference_minute = 0
                            employeeworks_item.is_empty = False
                            employeeworks_item.save()
                            employeeworks_item_i += 1

        complated = True
        rejcected = False
    except:
        complated = False
        rejcected = True

    # print("------------------------------------- Loading..... --------------------------------------------------------")
    # exc_list = []
    # # # print(result([], 300))
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).order_by('minute')
    # dest_list = []
    # for loc_destination_item in loc_destinations:
    #     dest_list.append(obj_to_dict_dest(loc_destination_item))
    # # print("calculate_minute([1, 5, 11, 20, 21, 27, 29], 300,dest_list)= {} ".format(calculate_minute([1, 5, 11, 20, 21, 27, 29], 300,dest_list)))
    # # print(exc_list)
    # # print(bulk_location_order)
    # LocationOrder.objects.bulk_create(bulk_location_order)

    # plan_obj = PlanLog.objects.filter(complated=False, rejcected=False).first()
    # if plan_obj:
    plan_obj_create.rejcected = rejcected
    plan_obj_create.complated = complated
    plan_obj_create.save()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    from django.core.mail import send_mail
    # EmailMultiAlternatives
    if plan_obj_create.complated:
        email_message = _('Task has complated')
    else:
        email_message = _('Task has complated')
    company_info = CompanyInformation.objects.filter(active=True).order_by('-date').first()
    if company_info and company_info.task_status_email:
        task_email = company_info.task_status_email
    else:
        task_email = 'ataxanr@gmail.com'
    send_mail(
        subject=_('Task status'),
        message=email_message,
        from_email=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD,
        recipient_list = [task_email],
        fail_silently=False,
    )
    # mail.send()
    # else:
    #     PlanLog.objects.create(complated=complated, rejcected=rejcected)
    # print("------------------------------------- Loaded --------------------------------------------------------")
    return '{} bulk locations order created with success!'.format(len(bulk_location_order))



@shared_task
def second_result_prepare_plan():
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
    work_days = WorkDay.objects.filter()
    week_list_i = 0
    PlanEmployeeWork.objects.filter().delete()
    try:
        for week_list_item in week_list:
            week_list_i += 1
            exc_list = []
            exc_locs = LocationOrder.objects.filter(plan_employee_work__week=week_list_item,main_process=True)
            for exc_locs_item in exc_locs:
                exc_list.append(exc_locs_item)
            employeeworks = PlanEmployeeWork.objects.filter(week=week_list_item).filter(
                minute__gt=0).order_by('-difference_minute',)

    except:
        pass










from content.new_main import main_work_list as main_work_list_nm
# from content.models import DayCHOICES
@shared_task
def main_result_prepare_plan_new_plan():
    from content.models import DayCHOICES,Hours_CHOICES
    from content.models import LocationDistance,Location, CompanyInformation, Employee,PlanEmployeeWork,LocationOrder,WorkDay,PlanLog
    from content.new_main import calculate_minute_1times as nm_calculate_minute_1times
    from content.new_main import calculate_minute as nm_calculate_minute
    from django.utils.translation import ugettext as _
    from content.new_main import result1p1_seven as nm_result1p1_seven
    from .new_main import ordered_locations as nm_ordered_locations
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
    # print("week_4_employee_work_list={}".format(week_4_employee_work_list))
    # print("week_2_employee_work_list={}".format(week_2_employee_work_list))
    # 2week_employee_work_list = []
    bulk_plan_employee_work_list = []
    bulk_location_order = []
    # exc_list = []
    employees = Employee.objects.filter()
    # locations = Location.objects.filter()
    work_days = WorkDay.objects.filter()
    week_list_i = 0
    main_loc = Location.objects.get(our_company=True)
    plan_obj_create = PlanLog.objects.create(complated=False, rejcected=False)
    PlanEmployeeWork.objects.filter().delete()
    # try:
    for week_list_item in week_list:
        week_list_i += 1
        # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

        # # print("week_2_employee_work_list={}".format(week_2_employee_work_list))
        # # print("week_4_employee_work_list={}".format(week_4_employee_work_list))
        weekly_exc_list = exc_list_loc(copy.deepcopy(week_2_employee_work_list),2,week_list_item) + exc_list_loc(copy.deepcopy(week_4_employee_work_list),4,week_list_item)
        exc_list = weekly_exc_list
        # # print("weekly_exc_list={}".format(weekly_exc_list))
        # # print("week_2_employee_work_list={}".format(week_2_employee_work_list))
        # # print("week_4_employee_work_list={}".format(week_4_employee_work_list))
        # # print("exc_list_loc(week_2_employee_work_list,2,week_list_item)={}".format(exc_list_loc(copy.deepcopy(week_2_employee_work_list),2,week_list_item)))
        # # print("exc_list_loc(week_2_employee_work_list,4,week_list_item)={}".format(exc_list_loc(copy.deepcopy(week_4_employee_work_list),4,week_list_item)))
        # print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
        # if week_list_item in [1,2,4]:
        for day_list_item in day_list:
            for employee_item in employees:
                if day_list_item in [x.day.day for x in employee_item.get_employee_work_days()]:
                    new_plan_employee_work = PlanEmployeeWork()
                    new_plan_employee_work.employee = employee_item
                    new_plan_employee_work.week = week_list_item
                    new_plan_employee_work.is_empty = True
                    new_plan_employee_work.minute = employee_item.get_employee_work_day(day_list_item).minute
                    new_plan_employee_work.difference_minute = new_plan_employee_work.minute
                    new_plan_employee_work.day = work_days.filter(day=day_list_item).first()
                    new_plan_employee_work.save()
        for Hours_CHOICES_item in Hours_CHOICES:
            if Hours_CHOICES_item[0]:
                # # print("DayCHOICES_item[0]={}".format(Hours_CHOICES_item[0]))
                employeeworks = PlanEmployeeWork.objects.filter(week=week_list_item,is_empty=True).filter(minute=Hours_CHOICES_item[0]).order_by('week','day__day')
                # # print("employeeworks={}".format(employeeworks.count()))
                while employeeworks.count()>0:
                    opt_loc_destinations = nm_result1p1_seven(exc_list=exc_list,minute=Hours_CHOICES_item[0])
                    if len(opt_loc_destinations) == 0:
                        break
                    print("*************************************************************************************")
                    print("opt_loc_destinations={}".format(opt_loc_destinations))
                    print("*************************************************************************************")
                    # print("opt_loc_destinations={}".format(opt_loc_destinations))
                    # # print("len(opt_loc_destinations)={}".format(len(opt_loc_destinations)))
                    employeeworks_item_i = 0
                    for employeeworks_item in employeeworks[:len(opt_loc_destinations)]:
                        opt_loc_destinations_i = 0
                        ordered_opt_loc_destination_item = opt_loc_destinations[employeeworks_item_i]
                        # ordered_opt_loc_destination_item = nm_ordered_locations(main_loc.id,opt_loc_destinations[employeeworks_item_i])
                        for opt_loc_destinations_item in ordered_opt_loc_destination_item[1:-1]:
                            new_location_order = LocationOrder()
                            exc_list.append(opt_loc_destinations_item)
                            new_location_order.plan_employee_work = copy.deepcopy(employeeworks_item)
                            new_location_order.order_index = copy.deepcopy(opt_loc_destinations_i+1)
                            new_location_order.location_id = copy.deepcopy(opt_loc_destinations_item)
                            new_location_order.main_process = True
                            new_location_order.save()
                            bulk_location_order.append(new_location_order)
                            # print('opt_loc_destinations[employeeworks_item_i] = {}'.format(opt_loc_destinations[employeeworks_item_i]))
                            opt_loc_destinations_i+=1
                        # # print("task.py 542 - employeeworks_item = {}".format(employeeworks_item))
                        # employeeworks_item.difference_minute = employeeworks_item.minute - nm_calculate_minute_1times(ordered_opt_loc_destination_item,loc_id,main_location.id,plan_emp_works_weeks_item.minute)
                        if employeeworks_item.difference_minute - 20 <= ordered_opt_loc_destination_item[-1][0]:
                            employeeworks_item.is_full = True

                        employeeworks_item.difference_minute = employeeworks_item.difference_minute - ordered_opt_loc_destination_item[-1][0]
                        employeeworks_item.is_empty = False
                        employeeworks_item.save()
                        employeeworks_item_i += 1

    complated = True
    rejcected = False
    # except:
    #     complated = False
    #     rejcected = True
    # print("------------------------------------- Loading..... --------------------------------------------------------")
    # exc_list = []
    # # # print(result([], 300))
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).order_by('minute')
    # dest_list = []
    # for loc_destination_item in loc_destinations:
    #     dest_list.append(obj_to_dict_dest(loc_destination_item))
    # # print("calculate_minute([1, 5, 11, 20, 21, 27, 29], 300,dest_list)= {} ".format(calculate_minute([1, 5, 11, 20, 21, 27, 29], 300,dest_list)))
    # # print(exc_list)
    # # print(bulk_location_order)
    # LocationOrder.objects.bulk_create(bulk_location_order)

    plan_obj = PlanLog.objects.filter(complated=False, rejcected=False).first()
    if plan_obj:
        plan_obj.rejcected = rejcected
        plan_obj.complated = complated
        plan_obj.save()
    else:
        PlanLog.objects.create(complated=complated, rejcected=rejcected)

    from django.core.mail import send_mail
    # EmailMultiAlternatives
    if plan_obj_create.complated:
        email_message = _('Task has complated')
    else:
        email_message = _('Task has complated')
    company_info = CompanyInformation.objects.filter(active=True).order_by('-date').first()
    if company_info and company_info.task_status_email:
        task_email = company_info.task_status_email
    else:
        task_email = 'ataxanr@gmail.com'
    send_mail(
        subject=_('Task status'),
        message=email_message,
        from_email=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD,
        recipient_list = [task_email],
        fail_silently=False,
    )



    # print("------------------------------------- Loaded --------------------------------------------------------")
    return '{} bulk locations order created with success!'.format(len(bulk_location_order))


@shared_task
def sub_main_result_prepare_plan_new_plan():
    from content.models import LocationOrder, Location, PlanEmployeeWork
    # from general.task_functions import result1p1 as nm_result1p1
    from content.new_main import sub_result1p1
    # from content.common import Hours_CHOICES
    from content.new_main import exc_list_loc
    # from .new_main import ordered_customers as nm_ordered_customers
    sub_proses = LocationOrder.objects.filter(main_process=False)
    sub_proses_customer_list = []
    for sub_proses_item in sub_proses:
        sub_proses_customer_list.append(copy.deepcopy(sub_proses_item.customer_id))
    sub_proses.delete()
    customers = Location.objects.filter(id__in=sub_proses_customer_list).order_by('id')
    week_2_employee_work_list = []
    week_4_employee_work_list = []
    week_no_standart_employee_work_list = []
    for customers_item in customers:
        if customers_item.work_times == 1 and customers_item.standart_task is False:
            week_no_standart_employee_work_list.append(customers_item.id)
        if customers_item.work_times == 2:
            week_2_employee_work_list.append(customers_item.id)
        if customers_item.work_times == 4:
            week_4_employee_work_list.append(customers_item.id)

    week_list = [1,2,3,4]
    day_list = [1,2,3,4,5,6,7]
    bulk_plan_employee_work_list = []
    bulk_customer_order = []

    week_list_i = 0
    for week_list_item in week_list:
        weekly_exc_list = week_no_standart_employee_work_list + exc_list_loc(copy.deepcopy(week_2_employee_work_list),2,week_list_item) + exc_list_loc(copy.deepcopy(week_4_employee_work_list),4,week_list_item)
        # exc_list = weekly_exc_list

        week_list_i += 1

        employeeworks = PlanEmployeeWork.objects.filter(week=week_list_item).filter(
            is_full=False).order_by('is_empty', '-difference_minute')

        employeeworks_item_i = 0
        for employeeworks_item in employeeworks:
            employeeworks_item_i += 1
            if employeeworks_item:
                employeeworks_item_get_customers = employeeworks_item.get_customers()
                exc_list = weekly_exc_list
                # exc_list = daily_exc_list + weekly_exc_list
                try:
                    opt_loc_destinations_customer_id = employeeworks_item_get_customers.last().customer.id
                except:
                    opt_loc_destinations_customer_id = 0
                opt_loc_destinations = sub_result1p1_seven(0,opt_loc_destinations_customer_id,exc_list=exc_list,
                                                        minute=employeeworks_item.difference_minute)
                try:
                    opt_loc_destinations_i = employeeworks_item_get_customers.last().order_index
                except:
                    opt_loc_destinations_i = 0
                ordered_opt_loc_destination_item = opt_loc_destinations[0]
                # employeeworks = PlanEmployeeWork.objects.filter(week=1,day__day=day_list_item,is_empty=True).filter(minute=Hours_CHOICES_item[0]).order_by('week','day__day')
                ordered_opt_loc_destination_item = opt_loc_destinations[0]
                # ordered_opt_loc_destination_item = nm_ordered_customers(main_loc.id,opt_loc_destinations[employeeworks_item_i])
                for opt_loc_destinations_item in ordered_opt_loc_destination_item[1:-1]:
                    new_customer_order = LocationOrder()
                    # daily_exc_list.append(opt_loc_destinations_item)
                    new_customer_order.plan_employee_work = copy.deepcopy(employeeworks_item)
                    new_customer_order.order_index = copy.deepcopy(opt_loc_destinations_i + 1)
                    new_customer_order.customer_id = copy.deepcopy(opt_loc_destinations_item)
                    new_customer_order.main_process = False
                    new_customer_order.save()
                    # bulk_customer_order.append(new_customer_order)
                    # print('opt_loc_destinations[employeeworks_item_i] = {}'.format(opt_loc_destinations[employeeworks_item_i]))
                    opt_loc_destinations_i += 1
                # # print("task.py 542 - employeeworks_item = {}".format(employeeworks_item))
                # employeeworks_item.difference_minute = employeeworks_item.minute - nm_calculate_minute_1times(ordered_opt_loc_destination_item,loc_id,main_customer.id,plan_emp_works_weeks_item.minute)
                if employeeworks_item.difference_minute - 20 <= ordered_opt_loc_destination_item[-1][0]:
                    employeeworks_item.is_full = True
                employeeworks_item.minute = ordered_opt_loc_destination_item[-1][0]
                employeeworks_item.is_empty = False
                employeeworks_item.save()
                employeeworks_item_i += 1

        # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

        # # print("week_2_employee_work_list={}".format(week_2_employee_work_list))
        # # print("week_4_employee_work_list={}".format(week_4_employee_work_list))
        weekly_exc_list = week_no_standart_employee_work_list + exc_list_loc(copy.deepcopy(week_2_employee_work_list),2,week_list_item) + exc_list_loc(copy.deepcopy(week_4_employee_work_list),4,week_list_item)
        exc_list = weekly_exc_list




    return True



