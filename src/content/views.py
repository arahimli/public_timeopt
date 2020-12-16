import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

# from content.main_functions import *
from content.main_fun import  calculate_minute as mf_cm
from content.new_main import opt_destination as nmf_od, get_diff_list_with
# from django_pandas.io import read_frame

from content.functions import calculate_minute as calculate_minute_f
from content.functions import opt_destination as opt_destination_f
from content.main_functions import distance_2_point as distance_2_point_mf
from .models import *
from .tasks import *
from django.db.models import Q
from celery import shared_task
# import pandas as pd

# Create your views here.

from content.new_main import  opt_destination as nmf_od
from content.new_main import  result as nmf_result
@login_required(login_url='userprofile:sign_in')
def index(request):
    from .models import LocationDistance
    from .new_main import calculate_minute_1times
    from .new_main import distance_2_point
    from .new_main import ordered_locations as nm_ordered_locations
    from .new_main import result1p1 as nm_result1p1
    print("****************************************************************************************************************")
    print("nm_result1p1 = {}".format(nm_result1p1([],280)))
    print("****************************************************************************************************************")
    return HttpResponse("nm_result1p1 = {}".format(nm_result1p1([],280)))
    # return HttpResponse(distance_2_point(55.881887,12.344352,55.645617,12.59448))
    return HttpResponse(nm_ordered_locations(433,[429, 427, 425, 423, 421, 419, 417, 415]))
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=[]) | Q(location2_id__in=[])).values('location1','location1__minute','location2','location2__minute','minute')
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=[]) | Q(location2_id__in=[]))
    # # week_dtf = pd.DataFrame.from_records(loc_destinations)
    # result_1 = read_frame(loc_destinations).sort_values(['minute'],ascending=[False])
    # for result_1_item_l1 ,result_1_item_l2 in zip(result_1.location1 ,result_1.location2):
    #     print("------{}======={}".format(result_1_item_l1,result_1_item_l2))
    # print ("--------------------------------------------------------------------------------------------------")
    # # print (result_1.filter())
    # print("mf_cm====={}".format(mf_cm([31, 32, 33],400,loc_destinations)))
    # map_data = [['Stærevej 47 2400 København NV'],['Hanehøj 11 - 2880 Søborg'],['Pelargonievej 28 - 2000 Frederiksberg'],['Kløverbladsgade 50 - 2500 Valby'],['Krimsvej 13D - 2300 København S'],['Tåsingegade 29, 1 lejlighed - 2100 København Ø']]
    # context = {'map_data':map_data}
    # return render(request, 'map2.html', context=context)
    # exc_list = []
    loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).order_by('-minute','-location1__minute','-location2__minute')
    dest_list = []
    for loc_destination_item in loc_destinations:
        dest_list.append(obj_to_dict_dest(loc_destination_item))
    calculate_minute_1times_val = calculate_minute_1times([82,81,80,79],75,31,480)
    print(calculate_minute_1times_val)
    return HttpResponse(calculate_minute_1times_val)
    # print ("--------------------------------------------------------------------------------------------------")
    # # nmf_od_v = nmf_od(31,[],480,dest_list=dest_list)
    # # nmf_od_v = nmf_result([],310,dest_list=dest_list)
    # # obj = EmployeeWorkDay.objects.filter()
    # # for obj_item in obj:
    # #     obj_item.minute = 480
    # #     obj_item.save()
    # # get_diff_list_with_val = get_diff_list_with([[1, 11, 16, 22, 25, 28,[20]], [1, 13, 15, 20, 21, 23,[20]], [1, 14, 17, 29, 26, 88,[20]], [1, 100, 106, 20, 21, 24,[20]], [1, 111, 116, 210, 211, 217,[20]], [1, 11, 16, 20, 21, 30,[20]], [1, 11, 16, 20, 21, 29,[20]], [1, 11, 16, 20, 21, 28,[20]], [1, 11, 16, 20, 21, 26,[20]], [1, 11, 16, 20, 26, 30,[20]], [1, 11, 16, 20, 26, 28,[20]], [1, 11, 16, 20, 26, 29,[20]], [1, 11, 16, 20, 26, 27,[20]]])
    # employeeworks = PlanEmployeeWork.objects.filter(is_empty=True).filter().order_by('week', 'day__day')
    # print(employeeworks.count())
    # for employeeworks_item in employeeworks[:20]:
    #     employeeworks_item.is_empty = False
    #     employeeworks_item.save()
    # print(employeeworks.count())
    # return HttpResponse("dfdfdff")
    # return HttpResponse(get_diff_list_with_val)
    # return HttpResponse(get_max_len_list([[1, 11, 16, 22, 25, 28], [1, 11, 16, 20, 21, 22], [1, 11, 16, 20, 21, 25], [1, 11, 16, 20, 21, 24], [1, 11, 16, 20, 21, 27], [1, 11, 16, 20, 21, 30], [1, 11, 16, 20, 21, 29], [1, 11, 16, 20, 21, 28], [1, 11, 16, 20, 21, 26], [1, 11, 16, 20, 26, 30], [1, 11, 16, 20, 26, 28], [1, 11, 16, 20, 26, 29], [1, 11, 16, 20, 26, 27], [1, 11, 16, 20, 28, 30], [1, 11, 16, 20, 28, 29], [1, 11, 16, 20, 25, 29], [1, 11, 16, 20, 25, 30], [1, 11, 16, 20, 25, 27], [1, 11, 16, 20, 25, 26], [1, 11, 16, 20, 25, 28], [1, 11, 16, 20, 27, 29], [1, 11, 16, 20, 27, 30], [1, 11, 16, 20, 27, 28], [1, 11, 16, 20, 22, 24], [1, 11, 16, 20, 22, 29], [1, 11, 16, 20, 22, 28], [1, 11, 16, 20, 22, 26], [1, 11, 16, 20, 22, 27], [1, 11, 16, 20, 22, 25], [1, 11, 16, 20, 22, 30], [1, 11, 16, 20, 29, 30], [1, 11, 16, 20, 24, 26], [1, 11, 16, 20, 24, 25], [1, 11, 16, 20, 24, 30], [1, 11, 16, 20, 24, 27], [1, 11, 16, 20, 24, 28], [1, 11, 16, 20, 24, 29], [1, 11, 16, 24, 26, 30], [1, 11, 16, 24, 26, 28], [1, 11, 16, 24, 26, 29], [1, 11, 16, 24, 26, 27], [1, 11, 16, 24, 25, 29], [1, 11, 16, 24, 25, 30], [1, 11, 16, 24, 25, 27], [1, 11, 16, 24, 25, 26], [1, 11, 16, 24, 25, 28], [1, 11, 16, 24, 27, 29], [1, 11, 16, 24, 27, 30], [1, 11, 16, 24, 27, 28], [1, 11, 16, 24, 28, 30], [1, 11, 16, 24, 28, 29], [1, 11, 16, 24, 29, 30], [1, 11, 16, 27, 29, 30], [1, 11, 16, 27, 28, 30], [1, 11, 16, 27, 28, 29], [1, 11, 16, 21, 22, 24], [1, 11, 16, 21, 22, 29], [1, 11, 16, 21, 22, 28], [1, 11, 16, 21, 22, 26], [1, 11, 16, 21, 22, 27], [1, 11, 16, 21, 22, 25], [1, 11, 16, 21, 22, 30], [1, 11, 16, 21, 25, 29], [1, 11, 16, 21, 25, 30], [1, 11, 16, 21, 25, 27], [1, 11, 16, 21, 25, 26], [1, 11, 16, 21, 25, 28], [1, 11, 16, 21, 24, 26], [1, 11, 16, 21, 24, 25], [1, 11, 16, 21, 24, 30], [1, 11, 16, 21, 24, 27], [1, 11, 16, 21, 24, 28], [1, 11, 16, 21, 24, 29], [1, 11, 16, 21, 27, 29], [1, 11, 16, 21, 27, 30], [1, 11, 16, 21, 27, 28], [1, 11, 16, 21, 29, 30], [1, 11, 16, 21, 28, 30], [1, 11, 16, 21, 28, 29], [1, 11, 16, 21, 26, 30], [1, 11, 16, 21, 26, 28], [1, 11, 16, 21, 26, 29], [1, 11, 16, 21, 26, 27]]))
    # main_result3.delay()
    # print(get_max_len_list([[1]]))
    # return HttpResponse(calculate_minute_f([1, 11, 16, 21, 26, 27],500))
    # return HttpResponse(opt_destination_f(1,[],100))
    # for week_list_item in week_list:
    #     for day_list_item in day_list:
    #         for employee_item in employees:
    #             if day_list_item in [x.id for x in employee_item.employee_work_days]:
    #                 return HttpResponse(result(1,[],[],500))

    # the list that will hold the bulk insert
    # print(distance_2_point_mf(43.232323,45.343434233))
    # HttpResponse(distance_2_point_mf(43.232323,45.343434233))
    # bulk_customer_distances = []
    exclude_list = []
    # print(opt_destination(19,[1, 30, 29, 28, 27],379))
    # print(all_result(0,exclude_list,500))
    # return HttpResponse(distance_2_point(1,1))
    # return HttpResponse(all_main_2([],[],[],[]))
    # return HttpResponse(all_main_2([],[],[],[]))
    # return HttpResponse(calculate_minute([1,2,3,4],500))
    # return HttpResponse(result(1,500))
    # loop that list and make those game objects
    # new_customer_distance = LocationDistance.objects.filter().delete()
    # for customer1 in customers:
    #     for customer2 in customers:
    #         if customer1.id == customer2.id or customer1.id > customer2.id:
    #             pass
    #         else:
    #             new_customer_distance = CustomerDistance()
    #             new_customer_distance.customer1 = customer1
    #             new_customer_distance.customer2 = customer2
    #             new_customer_distance.minute = random.randint(1, 500)
    #             new_customer_distance.distance = random.random()
    #
    #             # add game to the bulk list
    #             bulk_customer_distances.append(new_customer_distance)
    #
    # # now with a list of game objects that want to be created, run bulk_create on the chosen model
    # CustomerDistance.objects.bulk_create(bulk_customer_distances)
    # return HttpResponse(bulk_customer_distances)
    return HttpResponse("Success")