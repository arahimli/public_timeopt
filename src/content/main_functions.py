import json

from django.core import serializers
from django.db.models import Q
import copy
from timeopt import settings
from django.http import HttpResponseRedirect, Http404, HttpResponse

# from content.models import Location,LocationDistance
from django.db.models.fields.related import ManyToManyField
from django.db.models.fields.related import ForeignKey


def chunkify(lst, n):
    part = [lst[i::n] for i in range(0, n)]
    return_val = list(lst).remove(part)
    return return_val


def ordered_locations(main_id, list):
    from content.models import LocationDistance
    new_list = [main_id] + list
    current_id = copy.deepcopy(main_id)
    loc_destinations = LocationDistance.objects.filter(
        Q(location1_id__in=new_list) | Q(location2_id__in=new_list)).order_by('minute')
    first_loc = loc_destinations.filter(Q(location1_id=main_id) | Q(location2_id=main_id)).first()
    return_new_list = [main_id]
    if first_loc.location1_id == main_id:
        current_id = first_loc.location2_id
    elif first_loc.location2_id == main_id:
        current_id = first_loc.location1_id
    while len(return_new_list) < len(new_list):
        loc_destinations = loc_destinations.exclude(
            Q(location1_id__in=copy.deepcopy(return_new_list)) | Q(location2_id__in=copy.deepcopy(return_new_list)))
        first_min_loc = loc_destinations.filter(Q(location1_id=current_id) | Q(location2_id=current_id)).first()
        return_new_list.append(copy.deepcopy(current_id))
        print("return_new_list = {} - loc_destinations.count() = {}".format(return_new_list, loc_destinations.count()))
        if first_min_loc.location1_id == current_id:
            current_id = copy.deepcopy(first_min_loc.location2_id)
        elif first_min_loc.location2_id == current_id:
            current_id = copy.deepcopy(first_min_loc.location1_id)
    print("new_list = {}".format(new_list))
    print("new_list = {}".format(new_list[1:]))
    print("return_new_list = {}".format(return_new_list[1:]))
    return return_new_list[1:]


def exc_list_loc(lst, wc, w):
    try:
        if w > wc:
            w = w % wc
        part = [lst[i::wc] for i in range(0, wc)]
        w = w - 1
        for x in part[w]:
            lst.remove(x)
        return lst
    except:
        return []


def main_work_list(exc_list, minute):
    from content.models import LocationDistance
    # from django.forms.models import model_to_dict
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    loc_destinations = LocationDistance.objects.exclude(
        Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).exclude(
        Q(location1__work_times=3) | Q(location2__work_times=3)).order_by('-minute', '-location1__minute',
                                                                          '-location2__minute')
    dest_list = []
    for loc_destination_item in loc_destinations:
        dest_list.append(obj_to_dict_dest(loc_destination_item))
    print("exc_list = {}".format(exc_list))
    all_list = result(exc_list=exc_list, minute=minute, dest_list=dest_list)
    # get_max_len_list_with_minute_val = get_max_len_list_with_minute(list=all_list,minute=minute,dest_list=dest_list)
    # get_max_len_list_with_minute_val = all_list[0][:-1]
    get_diff_list_with_val = get_diff_list_with(all_list)
    print("get_max_len_list_with_minute_val = {}".format(get_diff_list_with_val))
    return get_diff_list_with_val


def get_diff_list_with(all_list):
    exc_list = all_list[0][1:-1]
    return_list = [exc_list]
    # return_list = [exc_list]
    i = 0
    for all_list_item in all_list[1:]:
        inc_bool = True
        for all_list_item_x in all_list_item[1:-1]:
            if all_list_item_x in exc_list:
                inc_bool = True
                break
            else:
                inc_bool = False
        if inc_bool == False:
            return_list.append(all_list_item[1:-1])
            exc_list = exc_list + all_list_item[1:-1]
    return return_list


def get_max_len_list_with_minute(list, minute, dest_list):
    return_list = list[0]
    min_minute = calculate_minute(list[0], minute, dest_list)
    get_list_max_len_val = get_list_max_len(list)
    for list_item in list:
        minute = calculate_minute(list_item, minute, dest_list)
        if get_list_max_len_val <= len(list_item):
            if minute < min_minute:
                min_minute = minute
                return_list = list_item
    return return_list


def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
        if isinstance(f, ForeignKey):
            if instance.pk is None:
                data[f.name] = 0
            else:
                data[f.name] = f.value_from_object(instance).values_list('pk', flat=True)
        else:
            data[f.name] = f.value_from_object(instance)
    return data


from django.core import serializers


def obj_to_dict_core(model_instance):
    serial_obj = serializers.serialize('json', [model_instance])
    obj_as_dict = json.loads(serial_obj)[0]['fields']
    obj_as_dict['pk'] = model_instance.pk
    return obj_as_dict


def obj_to_dict_dest(model_instance):
    from content.models import Location
    serial_obj = serializers.serialize('json', [model_instance])
    obj_as_dict = json.loads(serial_obj)[0]['fields']
    obj_as_dict['pk'] = model_instance.pk
    location_obj = Location.objects
    obj_as_dict['location2_obj'] = obj_to_dict_core(location_obj.get(id=model_instance.location2.id))
    obj_as_dict['location1_obj'] = obj_to_dict_core(location_obj.get(id=model_instance.location1.id))
    # print(model_instance.location2.id)
    # print(obj_as_dict['location2'])
    return obj_as_dict


def result(exc_list, minute, dest_list):
    from content.models import Location
    from django.forms.models import model_to_dict
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    result_list = []
    main_loc = Location.objects.get(our_company=True)
    if len(result_list) <= 0:
        current_loc_id = main_loc.id
        result_list.append([current_loc_id, [minute]])
    if main_loc.id in exc_list:
        try:
            exc_list.remove(main_loc.id)
        except:
            pass
    # print("result-list = {}".format(result_list)) [[1,[480]]]
    while len(result_list) > 0:

        result_list_def = []
        for result_item in result_list:
            if result_item[-1][0] > 0:
                # print("result_item = {}".format(result_item))
                opt_destination_fun = opt_destination(result_item[-2], result_item[:-2], result_item[-1][0],dest_list)
                try:
                    my_locs = opt_destination_fun
                    # print("******* opt_destination_fun = {}".format(opt_destination_fun))
                    if len(my_locs) >= 0:
                        for x in list(my_locs):
                            record = result_item[:-1]
                            result_t = record + [x[0]] + [[x[1]]]
                            result_list_def.append(copy.deepcopy(result_t))
                except:
                    pass
        if len(result_list_def) <= 0:
            break
        # result_list=add_to_list(result_list_def,result_list)
        # print("result_list = result_list_def = {}".format(result_list_def))
        result_list = result_list_def
        # print('--------------------------------------------------------------------------------------------------------------------------------------------')
        # print(result_list)
        # print('-------------------------------------------------------------- - len(result_list) = {}'.format(len(result_list)))

    print("result-list = {}".format(result_list))
    return result_list


def opt_destination(current_loc_id,exc_list, minute,dest_list):
    from content.models import Location
    from content.models import LocationDistance
    inc_list = []
    exc_list = list(exc_list)
    minute_last = minute

    result_val = []
    i=0
    j=0
    # loc_destinations = LocationDistance.objects.exclude(
    #     Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).exclude(
    #     Q(location1__work_times=3) | Q(location2__work_times=3)).filter(location1_id=current_loc_id).order_by('-minute', '-location1__minute',
    #                                                                       '-location2__minute')
    # print("***** exc_list = {}".format(exc_list))
    for dest_list_item in dest_list:
        minute_local = 0
        # print("dest_list_item['location1'] = {} -------  dest_list_item['location2'] = {}  -- ----------------- exc_list = {}".format(dest_list_item['location1'],dest_list_item['location2'],exc_list))
        if not (dest_list_item['location1'] in exc_list or dest_list_item['location2'] in exc_list):
            if dest_list_item['location1'] == current_loc_id or dest_list_item['location2'] == current_loc_id:
                # main_location = None
                go_location = None
                if current_loc_id == dest_list_item['location1']:
                    # main_location = dest_list_item['location1_obj']
                    go_location = dest_list_item['location2_obj']
                elif current_loc_id == dest_list_item['location2']:
                    # main_location = dest_list_item['location2_obj']
                    go_location = dest_list_item['location1_obj']
                # else:
                #     break
                minute_local = minute_last - (dest_list_item['minute'] + go_location['minute'])
                if minute_local>0:
                    inc_list.append([go_location['pk'],minute_local])
                    j+=1
                else:
                    pass
        i+=1
    return inc_list








# def opt_destination(current_loc_id, exc_list, minute):
#     from content.models import Location
#     from content.models import LocationDistance
#     inc_list = []
#     exc_list = list(exc_list)
#     minute_last = minute
#
#     result_val = []
#     i = 0
#     j = 0
#     loc_destinations = LocationDistance.objects.exclude(
#         Q(location1_id__in=exc_list) | Q(location2_id__in= exc_list)).exclude(
#         Q(location1__work_times=3) | Q(location2__work_times=3)).filter(
#         Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id))
#     for loc_destination in loc_destinations:
#         #     minute_local = 0
#         #     # print("dest_list_item['location1'] = {} -------  dest_list_item['location2'] = {}  -- ----------------- exc_list = {}".format(dest_list_item['location1'],dest_list_item['location2'],exc_list))
#         #     if not (dest_list_item['location1'] in exc_list or dest_list_item['location2'] in exc_list):
#         #         if dest_list_item['location1']  == current_loc_id or dest_list_item['location1'] == current_loc_id:
#         # main_location = None
#         go_location = None
#         if current_loc_id == loc_destination.location1_id:
#             # main_location = dest_list_item['location1_obj']
#             go_location = loc_destination.location2
#         elif current_loc_id == loc_destination.location2_id:
#             # main_location = dest_list_item['location2_obj']
#             go_location = loc_destination.location1
#         # else:
#         #     break
#         # print("********* go_location.name = {}".format(go_location.name))
#         # minute_local = minute_last - (loc_destination.minute + go_location.minute)
#         minute_local = minute_last - (loc_destination.minute + go_location.minute)
#         if minute_local > 0:
#             # print("minute_local>0 ********* go_location.name = {}".format(go_location.name))
#             inc_list.append([go_location.pk, minute_local])
#             j += 1
#         else:
#             pass
#         i += 1
#     return inc_list


def add_to_list(lists1, lists2):
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
    lists1 += append_val
    return lists1


def calculate_minute(loc_list, minute_all, dest_list):
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list))
    i = 0
    minute = 0
    for loc_list_item in loc_list:
        # print('dhsjdshdjshdj')
        if i > 0:
            j = 0
            for dest_list_item in dest_list:

                if (dest_list_item['location1'] == loc_list[i] and dest_list_item['location2'] == loc_list[i - 1]) or (
                        dest_list_item['location1'] == loc_list[i - 1] and dest_list_item['location2'] == loc_list[i]):
                    main_location = None
                    if loc_list[i] == dest_list_item['location1']:
                        main_location = dest_list_item['location1_obj']
                    else:
                        main_location = dest_list_item['location2_obj']
                    minute += dest_list_item['minute'] + main_location['minute']

        i += 1
    minute_all -= minute
    return minute_all


def calculate_minute_1times(loc_list, new_loc_id, main_loc_id, all_minute):
    from content.models import LocationDistance
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list))
    i = 0
    # result_val=0
    minute = 0
    loc_list.insert(0, main_loc_id)
    loc_list.append(new_loc_id)
    loc_destinations = LocationDistance.objects
    for loc_list_item in loc_list:
        # print("loc_list_item = {}".format(loc_list_item))
        if i > 0:
            print(
                "------------------------------------------------------------------------------------------------------------------------------")
            if loc_destinations:
                print("loc_destinations.count()".format(loc_destinations.count()))
            loc_destinations_item = loc_destinations.filter(
                Q(location1=loc_list[i], location2=loc_list[i - 1]) | Q(location1=loc_list[i - 1],
                                                                        location2=loc_list[i])).first()
            # main_location = None
            print(loc_destinations_item)
            if loc_destinations_item:
                if loc_list[i] == loc_destinations_item.location1.id:
                    main_location = loc_destinations_item.location1
                else:
                    main_location = loc_destinations_item.location2
                minute += loc_destinations_item.minute + main_location.minute
                print('loc_destinations_item.minute + main_location.minute = {}'.format(
                    loc_destinations_item.minute + main_location.minute))
            else:
                new_location_distance = LocationDistance()
                new_location_distance.location1_id = loc_list[i - 1]
                new_location_distance.location2_id = loc_list[i]
                distance_2_point_o = distance_2_point(
                    new_location_distance.location1.position.latitude,
                    new_location_distance.location1.position.longitude,
                    new_location_distance.location2.position.latitude,
                    new_location_distance.location2.position.longitude
                )
                new_location_distance.minute = distance_2_point_o[0]
                new_location_distance.distance = distance_2_point_o[1]
                new_location_distance.save()
                minute += new_location_distance.location2.minute + new_location_distance.minute

                print("loc_list[i]={}  ---- loc_list[i-1]={}".format(loc_list[i], loc_list[i - 1]))
            print('minute = {}'.format(minute))

        i += 1

    if all_minute >= minute:
        result_val = all_minute - minute
    else:
        result_val = -1
    return [result_val, len(loc_list) - 1]


def get_list_max_len(list):
    max_count = 0
    for list_item in list:
        if max_count <= len(list_item):
            max_count = len(list_item)
    return max_count


def get_max_len_list(list):
    return_list = []
    for list_item in list:
        if get_list_max_len(list) <= len(list_item):
            return_list.append(list_item)
    return return_list


# def


# def read_customer_from_excel(url):
#     import xlrd
#     file_location = url
#     work_book = xlrd.open_workbook(file_location)
#     sheet = work_book.sheet_by_index(0)
#     nrows = sheet.nrows
#     ncols = sheet.ncols
#     for nrows_item in range(nrows):
#         for ncols_item in range(ncols):
#             print(sheet.cell(nrows,ncols))


def week_dtf_(week_dtf):
    return week_dtf


# def week_dtf_(week_dtf):
#     return week_dtf





def distance_2_point(location1_lat, location1_lon, location2_lat, location2_lon):
    import googlemaps
    from datetime import datetime
    # GEOPOSITION_GOOGLE_MAPS_API_KEY = settings.GEOPOSITION_GOOGLE_MAPS_API_KEY
    gmaps = googlemaps.Client(key=settings.GEOPOSITION_GOOGLE_MAPS_API_KEY)
    # gmaps = googlemaps.Client(key='AIzaSyAhAUDoUJWxE294kOzQuvI5u-hOMfCA24A')

    # Geocoding and address
    geocode_distance = gmaps.distance_matrix((location1_lat, location1_lon), (location2_lat, location2_lon),
                                             mode="driving")
    geocode_distance_es = geocode_distance['rows'][0]['elements'][0]
    return [int(round(geocode_distance_es['duration']['value'] / 60)), geocode_distance_es['distance']['value']]





