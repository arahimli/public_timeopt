from django.db.models import Q
from timeopt import settings
from django.http import HttpResponseRedirect, Http404, HttpResponse

from content.models import Location,LocationDistance


def opt_destination_main(exc_list, minute):
    main_loc = Location.objects.get(our_company=True)
    current_loc_id = main_loc.id
    all_result = opt_destination_second(current_loc_id,exc_list,inc_list, minute,exc_list)
    max_location = 0
    max_list = []
    min_minute = 0
    for result in list(all_result):
        if max_location < len(result[0]):
            max_location = len(result[0])
            max_list = result[0]
            min_minute = result[1]
        elif max_location < len(result[0]):
            if min_minute>result[1]:
                max_location = len(result[0])
                max_list = result[0]
                min_minute = result[1]
    return max_list


# [2, [[7, 1777], [3, 1722], [6, 1617], [4, 1598], [5, 1545], [1, 1417]]]
# def opt_destination(current_loc_id,exc_list, minute):
#     inc_list = []
#     exc_list = list(exc_list)
#     minute_last = minute
#     print("------------------------------------------------------------------------------------------------------------")
#     loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id))
#     print(loc_destinations.count())
#     print(minute)
#
#     result_val = []
#     # return len(loc_destinations)
#     if minute > 0:
#         # print(inc_list)
#         # print(exc_list)
#         # loc_destinations = loc_destinations.filter(location1=current_loc_id)
#         exc_list.append(current_loc_id)
#         for loc_destination in loc_destinations:
#             main_location = None
#             second_location = None
#             # print(current_loc_id)
#             # print(loc_destination.location1_id)
#             # print(loc_destination.location2_id)
#             if current_loc_id == loc_destination.location1_id:
#                 main_location = loc_destination.location1
#                 second_location = loc_destination.location2
#             elif current_loc_id == loc_destination.location2_id:
#                 main_location = loc_destination.location2
#                 second_location = loc_destination.location1
#             # else:
#             #     break
#             minute = minute_last - (loc_destination.minute + second_location.minute)
#             # print(minute)
#             if minute>0:
#                 inc_list.append([second_location.id,minute])
#             else:
#                 pass
#         # result_val.append([current_loc_id, inc_list])
#         result_val.append(current_loc_id)
#         result_val.append(inc_list)
#
#     return result_val
#     # return result_val

def all_result(current_loc_id,exc_list,minute):
    all_result_minute = 0
    if current_loc_id <= 0:
        main_loc = Location.objects.get(our_company=True)
        current_loc_id = main_loc.id
        # print(current_loc_id)
        # print(check_go_location(current_loc_id,exc_list,minute))
        # print(len(opt_destination(current_loc_id,exc_list,minute)))
        # print(check_go_location(current_loc_id,exc_list,minute))
    if check_go_location(current_loc_id,exc_list,minute):
        print("Salam Salam Salam Salam Salam Salam Salam Salam Salam Salam Salam Salam ")
        print(check_go_location(current_loc_id,exc_list,minute))
        print("Salam Salam Salam Salam Salam Salam Salam Salam Salam Salam Salam Salam")
        destinations = opt_destination(current_loc_id,exc_list,minute)
        i = 0
        print(destinations[1])
        exc_list.append(current_loc_id)
        # for destination in destinations[1]:
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(destinations[1][0])
        print(exc_list)
        print("old loc - {}".format(current_loc_id))
        current_loc_id = destinations[1][0][0]
        print("new loc - {}".format(current_loc_id))
        print("Hasssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
        print("###################################")
        print(destinations[1][0][1])

        all_result(current_loc_id,exc_list=exc_list,minute=destinations[1][0][1])
        all_result_minute = destinations[1][0][1]
        return [exc_list,all_result_minute]
    else:
        print("Nooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
        print(minute)
        print(check_go_location(current_loc_id,exc_list,minute))
        print("Nooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    # return  [exc_list,all_result_minute]


def check_go_location(current_loc_id,exc_list,minute):
    result = opt_destination(current_loc_id,exc_list,minute)
    print("Hahahahahahhahahahahahahahahahhhahahahahahahhahahahahahahahahhahahhhahahahahahahahahaha")
    print(current_loc_id)
    # print(exc_list)
    print(minute)
    print("Hahahahahahhahahahahahahahahahhhahahahahahahhahahahahahahahahhahahhhahahahahahahahahaha")
    if len(result[1])>0:
        return True
    else:
        return False
    # if



def all_main(list, exc_list, all_list,result):
    if len(all_list)<=0 or all_list is None:
        main_loc = Location.objects.get(our_company=True)
        current_loc_id = main_loc.id
        # locations = Location.objects.exclude(our_company=True)
        list.append(current_loc_id)
        # all_list.append(list)
    if len(all_list) > 0:
        locations = Location.objects.exclude(our_company=True).order_by('id')
        try:
            print(all_list)
            locations=locations.exclude(id__in=list)
        except:
            pass
            # return HttpResponse(all_list)
        for loc_main in locations:
            # print(all_list)
            # exc_list = all_list
            # print(exc_list)
            # return  HttpResponse(all_list_item)
            try:
                # all_list.remove(all_list_item)
                list.append(loc_main.id)
                # all_list.append(all_list_item)
            except:
                pass
            # print([all_list_item,exc_list,[]])
            # return HttpResponse([all_list_item,exc_list,all_list])
            # print(all_main(all_list_item,exc_list,all_list))
            print("============================================================================================================================================================")
            # print(all_list)
            print("============================================================================================================================================================")

            all_list = all_main(list,exc_list,all_list,result)
            print("------------------------------------------------------------------------------------------------------------------------------------------------------------")
            print(all_list)
            print("------------------------------------------------------------------------------------------------------------------------------------------------------------")
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            result.append([all_list])
            print(result)
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            # return all_list
            if all_list is None:
                break
            else:
                continue
            # result.append(all_list)
            # all_list.append(all_main(all_list_item,exc_list,all_list)[2])

    return all_list


def all_main_2(list, exc_list, all_list,result):
    if len(list)<=0 or list is None:
        main_loc = Location.objects.get(our_company=True)
        current_loc_id = main_loc.id
        # locations = Location.objects.exclude(our_company=True)
        list.append(current_loc_id)
    if len(list) > 0:
        locations = Location.objects.exclude(our_company=True).order_by('id')
        locations=locations.exclude(id__in=list)
        if locations.count()>0:
            for loc_main in locations:
                list.append(loc_main.id)
                all_list.append(all_main_2(list,exc_list,all_list,result)[0])
        else:
            all_list.append(list)
            print(all_list)
    return all_list












def result(exc_list,minute):
    result_list = []
    main_loc = Location.objects.get(our_company=True)
    if len(result_list)<=0:
        current_loc_id = main_loc.id
        result_list.append([current_loc_id])
    if main_loc.id in exc_list:
        try:
            exc_list.remove(main_loc.id)
        except:
            pass
    # print("result-list = {}".format(result_list))
    while len(result_list) > 0:
        result_list_def = []
        for result_item in result_list:
            my_locs = opt_destination(result_item[-1], result_item[:-1], minute)[1]

            if len(my_locs)>=0:
                for x in list(my_locs):
                    result_t = result_item+[x[0]]
                    result_list_def.append(result_t)
        if len(result_list_def) <= 0:
            break
        result_list=add_to_list(result_list_def,result_list)
        print('--------------------------------------------------------------------------------------------------------------------------------------------')
        print(result_list)
        print('-------------------------------------------------------------- - len(result_list) = {}'.format(len(result_list)))


    print("result-list = {}".format(result_list))
    return result_list


def add_to_list(lists1,lists2):
    append_val = []
    for list1 in lists1:
        bool = False
        val = []
        for list2 in lists2:
            if list2 in list1:
                bool = True
                break
            else:
                bool = False
        if bool:
            append_val.append(list1)
    lists1+=append_val
    return lists1



def calculate_minute(loc_list,minute_all):
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list))
    i=0
    minute=0
    for loc_list_item in loc_list:
        # print('dhsjdshdjshdj')
        if i >0:
            loc_destination = LocationDistance.objects.filter(Q(location1_id=loc_list[i],location2_id=loc_list[i-1]) | Q(location1_id=loc_list[i-1],location2_id=loc_list[i])).first()
            main_location = None
            if loc_list[i] == loc_destination.location1_id:
                main_location = loc_destination.location1
            else:
                main_location = loc_destination.location2
            minute += loc_destination.minute + main_location.minute

        i+=1
    minute_all-=minute
    return minute_all



def opt_destination(current_loc_id,exc_list, minute):
    inc_list = []
    exc_list = list(exc_list)
    minute_last = minute
    # print("------------------------------------------------------------------------------------------------------------")
    # print(exc_list)
    # print("------------------------------------------------------------------------------------------------------------")
    loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    # print(loc_destinations.count())
    # print(minute)

    result_val = []
    # return len(loc_destinations)
    if minute > 0:
        # print(inc_list)
        # print(exc_list)
        # loc_destinations = loc_destinations.filter(location1=current_loc_id)
        exc_list.append(current_loc_id)
        for loc_destination in loc_destinations:
            main_location = None
            second_location = None
            # print(current_loc_id)
            # print(loc_destination.location1_id)
            # print(loc_destination.location2_id)
            if current_loc_id == loc_destination.location1_id:
                main_location = loc_destination.location1
                second_location = loc_destination.location2
            elif current_loc_id == loc_destination.location2_id:
                main_location = loc_destination.location2
                second_location = loc_destination.location1
            # else:
            #     break
            minute = minute_last - (loc_destination.minute + second_location.minute)
            # print(minute)
            if minute>0:
                inc_list.append([second_location.id,minute])
            else:
                pass
        # result_val.append([current_loc_id, inc_list])
        result_val.append(current_loc_id)
        result_val.append(inc_list)

    return result_val
    # return result_val





import googlemaps
from datetime import datetime


def distance_2_point(location1,location2):

    # gmaps = googlemaps.Client(key=settings.GEOPOSITION_GOOGLE_MAPS_API_KEY)
    gmaps = googlemaps.Client(key='AIzaSyCZzOkIyEloBqx-8MSfZZxMp3rVKCtfc3k')

    # Geocoding and address
    geocode_distance = gmaps.distance_matrix("Toronto","Montreal")
    geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
    print(geocode_result)
    # Look up an address with reverse geocoding
    reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

    # Request directions via public transit
    now = datetime.now()
    directions_result = gmaps.directions('Toronto',
                                         "Montreal",
                                         mode="transit",
                                         departure_time=now)
    return geocode_result