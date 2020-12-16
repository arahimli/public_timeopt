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
        # print("return_new_list = {} - loc_destinations.count() = {}".format(return_new_list, loc_destinations.count()))
        if first_min_loc.location1_id == current_id:
            current_id = copy.deepcopy(first_min_loc.location2_id)
        elif first_min_loc.location2_id == current_id:
            current_id = copy.deepcopy(first_min_loc.location1_id)
    # print("new_list = {}".format(new_list))
    # print("new_list = {}".format(new_list[1:]))
    # print("return_new_list = {}".format(return_new_list[1:]))
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
    # print("exc_list = {}".format(exc_list))
    all_list = result(exc_list=exc_list, minute=minute, dest_list=dest_list)
    # get_max_len_list_with_minute_val = get_max_len_list_with_minute(list=all_list,minute=minute,dest_list=dest_list)
    # get_max_len_list_with_minute_val = all_list[0][:-1]
    get_diff_list_with_val_most_opt = get_diff_list_with(all_list[0])
    get_diff_list_with_val_more_opt = get_diff_list_with(all_list[1])
    get_diff_list_with_val_more_opt_last = more_opt_last_generator(get_diff_list_with_val_most_opt,get_diff_list_with_val_more_opt)
    # print("get_diff_list_with_val_most_opt = {}".format(get_diff_list_with_val_most_opt))
    # print("get_diff_list_with_val_more_opt = {}".format(get_diff_list_with_val_more_opt))
    # print("get_diff_list_with_val_more_opt_last = {}".format(get_diff_list_with_val_more_opt_last))
    return get_diff_list_with_val_more_opt_last


def get_diff_list_with(all_list):
    # print("get_diff_list_with = ")
    try:
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
    except:
        return []


def more_opt_last_generator(most_opt,more_opt):
    exc_list = []
    return_list = []
    return_list_all = []
    for most_opt_item in most_opt:
        for most_opt_item_x in most_opt_item:
            exc_list.append(most_opt_item_x)
    # print("121 exc_list = {}".format(exc_list))
    for more_opt_item in more_opt:
        inc_bool = False
        for more_opt_item_x in more_opt_item:
            if more_opt_item_x in exc_list:
                inc_bool = True
                break
        if inc_bool == False:
            return_list.append(more_opt_item)
    return_list_all = most_opt + return_list
    return return_list_all




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
    # from django.forms.models import model_to_dict
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
    while_count = 1
    result_list_last = []
    while len(result_list) > 0:
        # print("while_count = {}".format(while_count))
        while_count += 1
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
        result_list_last = copy.deepcopy(result_list)
        result_list = result_list_def
        # print("result-list = {}".format(result_list))
        # print('--------------------------------------------------------------------------------------------------------------------------------------------')
        # print(result_list)
        # print('-------------------------------------------------------------- - len(result_list) = {}'.format(len(result_list)))

    # print("result-list = {}".format(result_list))
    # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
    # print("result_list_last = {}".format(result_list_last))
    return [result_list,result_list_last]


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
    for dest_list_item in [item for item in dest_list if not (item['location1'] in exc_list or item['location2'] in exc_list) and (item['location1'] == current_loc_id or item['location2'] == current_loc_id)]:
        minute_local = 0
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
            # print("---------------------------------------------------------------------------------------------------------")
            if loc_destinations:
                pass
                # print("loc_destinations.count()".format(loc_destinations.count()))
            loc_destinations_item = loc_destinations.filter(
                Q(location1=loc_list[i], location2=loc_list[i - 1]) | Q(location1=loc_list[i - 1],
                                                                        location2=loc_list[i])).first()
            # main_location = None
            # print(loc_destinations_item)
            if loc_destinations_item:
                if loc_list[i] == loc_destinations_item.location1.id:
                    main_location = loc_destinations_item.location1
                else:
                    main_location = loc_destinations_item.location2
                minute += loc_destinations_item.minute + main_location.minute
                # print('loc_destinations_item.minute + main_location.minute = {}'.format(
                #     loc_destinations_item.minute + main_location.minute))
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

                # print("loc_list[i]={}  ---- loc_list[i-1]={}".format(loc_list[i], loc_list[i - 1]))
            # print('minute = {}'.format(minute))

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





# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def result1p1(exc_list, minute):
    from content.models import Location,LocationDistance
    # from django.forms.models import model_to_dict
    # from content.new_main import calculate_minute_1times as nm_calculate_minute_1times

    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    result_list = []
    result_exc_list = []

        # .order_by('-minute', '-location1__minute','-location2__minute')
    # dest_list = []
    # for loc_destination_item in loc_destinations:
    #     dest_list.append(obj_to_dict_dest(loc_destination_item))
    loc_destinations = LocationDistance.objects.exclude(
        Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).exclude(
        Q(location1__work_times=3) | Q(location2__work_times=3)).order_by('minute')
    main_location = Location.objects.filter(our_company=True).first()
    customers = Location.objects.exclude(id__in=exc_list).exclude(our_company=True)
    while_bool = True
    before_vals = []
    customers_11_bool = False
    # res_val = []
    while_bool = True
    for_bool = True
    return_while = False
    for order_index in range(9, 0, -1):
        if for_bool is False:
            # print('return_while = {}'.format(return_while))
            break
        print('return for')
        # print(while_bool)
        print("<order_index> = <{}>".format(order_index))
        print("<while_bool> = <{}>".format(while_bool))
        print("<return_while> = <{}>".format(return_while))
        while_bool = True
        return_while = False
        print('return for')
        while while_bool:
            print('head yoxdu return_while = {}'.format(return_while))
            # if while_bool is False:
            #     # print('return_while = {}'.format(return_while))
            #     break
            customers_9_item_i = 0
            customers_8_item_i = 0
            customers_7_item_i = 0
            return_while = False
            res_val = [
                       main_location.id,
                    ]
            # print("while_bool  res_val= {}".format(res_val))
            first_dests = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=main_location.id) | Q(location2_id=main_location.id)).order_by('minute')

            if first_dests.count() == 0:
                # # print('var first_dests= {}'.format(first_dests.count()))
                break
            else:
                pass
            print('foot yoxdu first_dests = {}'.format(first_dests.count()))
            for customers_1_item in first_dests:
                if return_while:
                    # print('return_while = {}'.format(return_while))
                    break
                # for_break = False
                # if for_break:
                #     continue
                # before_vals.append(customers_1_item.id)
                if customers_1_item.location1_id == main_location.id:
                    customers_1_item_GO = customers_1_item.location2
                    customers_1_item_ord = 2
                else:
                    customers_1_item_GO = customers_1_item.location1
                    customers_1_item_ord = 1
                # res_val += [customers_1_item_GO.id]
                minute_sum = 0
                # print("customers_1_item.minute , customers_1_item_GO.minute= {}  ,   {}".format(customers_1_item.minute , customers_1_item_GO.minute))
                if order_index > 1 and minute_sum + customers_1_item.minute + customers_1_item_GO.minute <= minute:
                    print("@@@@@@@@@@@ if 1")
                    minute_sum += customers_1_item.minute + customers_1_item_GO.minute
                    res_val += [
                        customers_1_item_GO.id,
                    ]
                    # pass
                elif order_index > 1 and minute_sum + customers_1_item.minute + customers_1_item_GO.minute > minute:
                    print("@@@@@@@@@@@ elif 1")
                    continue
                else:
                    print("@@@@@@@@@@@ else 1")
                    print("@@@@@@@@@@@ {} - {} - {}".format(order_index , minute_sum + customers_1_item.minute + customers_1_item_GO.minute , minute))
                    # print("order_index else = {}".format(order_index))
                    if minute_sum + customers_1_item.minute + customers_1_item_GO.minute <= minute:
                        # print("@@@@@@@@@@@ if 1")
                        minute_sum += customers_1_item.minute + customers_1_item_GO.minute
                        res_val += [
                            customers_1_item_GO.id,
                        ]
                        # print('+++++++++++++++++++++++++++++++++++++++minute_sum <= minute++++++++++++++++++++++++++++++++++++++++')
                        # print('+++++++++++++++++++++++++++++++++++++++ res_val = {} ++++++++++++++++++++++++++++++++++++++++'.format(res_val))
                        res_val_i = 0
                        for res_val_item in res_val:
                            res_val_i += 1
                            if res_val_i > 0:
                                result_exc_list.append(copy.deepcopy(res_val_item))
                        result_list.append(copy.deepcopy(res_val))

                        return_while = True
                        # print('+++++++++++++++++++++++++++++++++++++++ return_while = {} ++++++++++++++++++++++++++++++++++++++++'.format(return_while))
                        break
                    else:
                        if order_index == 1 and first_dests.last().id == customers_1_item.id:
                            return_while = True
                            while_bool = False
                            break
                        else:
                            continue
                print("customers_1_item  res_val= {}, = minute_sum= {}".format(res_val,minute_sum))
                # print("customers_1_item  minute_sum= {}".format(minute_sum))
                dests_2 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_1_item_GO.id) | Q(location2_id=customers_1_item_GO.id)).order_by('minute')
                if dests_2.count() == 0:
                    while_bool = False
                    return_while = True
                    print('var dests_2= {}'.format(dests_2.count()))
                    break
                else:
                    print('yoxdu dests_2 = {}'.format(dests_2.count()))
                    pass
                res_val_1 = copy.deepcopy(res_val)
                minute_sum_1 = copy.deepcopy(minute_sum)
                for customers_2_item in dests_2:
                    res_val = copy.deepcopy(res_val_1)
                    minute_sum = copy.deepcopy(minute_sum_1)
                    if return_while:
                        break

                    if customers_2_item.location1_id == customers_1_item_GO.id:
                        customers_2_item_GO = customers_2_item.location2
                    else:
                        customers_2_item_GO = customers_2_item.location1
                    # res_val += [customers_2_item_GO.id]
                    # print("customers_2_item  res_val= {}".format(res_val))
                    # before_vals.append(customers_2_item.id)
                    # minute_sum += customers_2_item.minute + customers_2_item_GO.minute
                    # print("customers_2_item  minute_sum= {}".format(minute_sum))
                    # print("customers_2_item.minute , customers_2_item_GO.minute= {}  ,   {}".format(customers_2_item.minute , customers_2_item_GO.minute))
                    if order_index > 2 and minute_sum + customers_2_item.minute + customers_2_item_GO.minute <= minute:
                        minute_sum += customers_2_item.minute + customers_2_item_GO.minute
                        res_val += [
                            customers_2_item_GO.id,
                        ]
                        # pass
                    elif order_index > 2 and minute_sum + customers_2_item.minute + customers_2_item_GO.minute > minute:
                        continue
                    else:
                        print("order_index else = {}".format(order_index))
                        if minute_sum + customers_2_item.minute + customers_2_item_GO.minute <= minute:
                            minute_sum += customers_2_item.minute + customers_2_item_GO.minute
                            res_val += [
                                customers_2_item_GO.id,
                            ]
                            res_val_i = 0
                            for res_val_item in res_val:
                                if res_val_i > 0:
                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                res_val_i += 1
                            result_list.append(copy.deepcopy(res_val))
                            return_while = True
                            break
                        else:
                            if order_index == 2 and first_dests.last().id == customers_1_item.id:
                                return_while = True
                                while_bool = False
                                break
                            else:
                                continue
                    print("customers_2_item  res_val= {}, = minute_sum= {}".format(res_val,minute_sum))
                    dests_3 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_2_item_GO.id) | Q(location2_id=customers_2_item_GO.id)).order_by('minute')
                    if dests_3.count() == 0:
                        while_bool = False
                        return_while = True
                        print('var dests_3= {}'.format(dests_3.count()))
                        break
                    else:
                        print('yoxdu dests_3= {}'.format(dests_3.count()))
                        pass
                    res_val_2 = copy.deepcopy(res_val)
                    minute_sum_2 = copy.deepcopy(minute_sum)
                    for customers_3_item in dests_3:
                        res_val = copy.deepcopy(res_val_2)
                        minute_sum = copy.deepcopy(minute_sum_2)
                        if return_while:
                            break
                        # before_vals.append(customers_3_item.id)
                        if customers_3_item.location1_id == customers_2_item_GO.id:
                            customers_3_item_GO = customers_3_item.location2
                        else:
                            customers_3_item_GO = customers_3_item.location1
                        # res_val += [customers_3_item_GO.id]
                        # # print("customers_3_item  res_val= {}".format(res_val))
                        # minute_sum += customers_3_item.minute + customers_3_item_GO.minute
                        if order_index > 3 and minute_sum + customers_3_item.minute + customers_3_item_GO.minute <= minute:
                            minute_sum += customers_3_item.minute + customers_3_item_GO.minute
                            res_val += [
                                customers_3_item_GO.id,
                            ]
                            # pass
                        elif order_index > 3 and minute_sum + customers_3_item.minute + customers_3_item_GO.minute > minute:
                            continue
                        else:
                            # print("order_index else = {}".format(order_index))
                            if minute_sum + customers_3_item.minute + customers_3_item_GO.minute <= minute:
                                minute_sum += customers_3_item.minute + customers_3_item_GO.minute
                                res_val += [
                                    customers_3_item_GO.id,
                                ]
                                res_val_i = 0
                                for res_val_item in res_val:
                                    if res_val_i > 0:
                                        result_exc_list.append(copy.deepcopy(res_val_item))
                                    res_val_i += 1
                                result_list.append(copy.deepcopy(res_val))
                                return_while = True
                                break
                            else:
                                if order_index == 3 and first_dests.last().id == customers_1_item.id:
                                    return_while = True
                                    while_bool = False
                                    break
                                else:
                                    continue
                        # print("customers_3_item  minute_sum= {}".format(minute_sum))
                        # print("customers_3_item.minute , customers_3_item_GO.minute= {}  ,   {}".format(customers_3_item.minute , customers_3_item_GO.minute))
                        dests_4 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_3_item_GO.id) | Q(location2_id=customers_3_item_GO.id)).order_by('minute')
                        if dests_4.count() == 0:
                            while_bool = False
                            return_while = True
                            print('var dests_4= {}'.format(dests_4.count()))
                            break
                        else:
                            print('yoxdu dests_4= {}'.format(dests_4.count()))
                            pass
                        res_val_3 = copy.deepcopy(res_val)
                        minute_sum_3 = copy.deepcopy(minute_sum)
                        print("customers_3_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                        for customers_4_item in dests_4:
                            res_val = copy.deepcopy(res_val_3)
                            minute_sum = copy.deepcopy(minute_sum_3)
                            if return_while:
                                break
                            # before_vals.append(customers_4_item.id)
                            if customers_4_item.location1_id == customers_3_item_GO.id:
                                customers_4_item_GO = customers_4_item.location2
                            else:
                                customers_4_item_GO = customers_4_item.location1
                            # res_val += [customers_4_item_GO.id]
                            # # print("customers_4_item  res_val= {}".format(res_val))
                            # minute_sum += customers_4_item.minute + customers_4_item_GO.minute
                            if order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.minute <= minute:
                                minute_sum += customers_4_item.minute + customers_4_item_GO.minute
                                res_val += [
                                    customers_4_item_GO.id,
                                ]
                                # pass
                            elif order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.minute > minute:
                                continue
                            else:
                                # print("order_index else = {}".format(order_index))
                                if minute_sum + customers_4_item.minute + customers_4_item_GO.minute <= minute:
                                    minute_sum += customers_4_item.minute + customers_4_item_GO.minute
                                    res_val += [
                                        customers_4_item_GO.id,
                                    ]
                                    res_val_i = 0
                                    for res_val_item in res_val:
                                        if res_val_i > 0:
                                            result_exc_list.append(copy.deepcopy(res_val_item))
                                        res_val_i += 1
                                    result_list.append(copy.deepcopy(res_val))
                                    return_while = True
                                    break
                                else:
                                    if order_index == 4 and first_dests.last().id == customers_1_item.id:
                                        return_while = True
                                        while_bool = False
                                        break
                                    else:
                                        continue
                            # print("customers_4_item  minute_sum= {}".format(minute_sum))
                            # print("customers_4_item.minute , customers_4_item_GO.minute= {}  ,   {}".format(customers_4_item.minute , customers_4_item_GO.minute))
                            print("customers_4_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                            dests_5 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_4_item_GO.id) | Q(location2_id=customers_4_item_GO.id)).order_by('minute')
                            if dests_5.count() == 0:
                                while_bool = False
                                return_while = True
                                print('var dests_5= {}'.format(dests_5.count()))
                                break
                            else:
                                pass
                                print('yoxdu dests_5= {}'.format(dests_5.count()))
                            res_val_4 = copy.deepcopy(res_val)
                            minute_sum_4 = copy.deepcopy(minute_sum)
                            for customers_5_item in dests_5:
                                res_val = copy.deepcopy(res_val_4)
                                minute_sum = copy.deepcopy(minute_sum_4)
                                if return_while:
                                    break
                                if customers_5_item.location1_id == customers_4_item_GO.id:
                                    customers_5_item_GO = customers_5_item.location2
                                else:
                                    customers_5_item_GO = customers_5_item.location1
                                # res_val += [customers_5_item_GO.id]
                                print("customers_5_item  res_val= {}".format(res_val))
                                # before_vals.append(customers_5_item.id)
                                if order_index > 5 and minute_sum + customers_5_item.minute + customers_5_item_GO.minute <= minute:
                                    minute_sum += customers_5_item.minute + customers_5_item_GO.minute
                                    res_val += [
                                        customers_5_item_GO.id,
                                    ]
                                    # pass
                                elif order_index > 5 and minute_sum + customers_5_item.minute + customers_5_item_GO.minute > minute:
                                    continue
                                else:
                                    print("order_index else = {}".format(order_index))
                                    if minute_sum + customers_5_item.minute + customers_5_item_GO.minute <= minute:
                                        minute_sum += customers_5_item.minute + customers_5_item_GO.minute
                                        res_val += [
                                            customers_5_item_GO.id,
                                        ]
                                        res_val_i = 0
                                        for res_val_item in res_val:
                                            if res_val_i > 0:
                                                result_exc_list.append(copy.deepcopy(res_val_item))
                                            res_val_i += 1
                                        result_list.append(copy.deepcopy(res_val))
                                        return_while = True
                                        break
                                    else:
                                        if order_index == 5 and first_dests.last().id == customers_1_item.id:
                                            return_while = True
                                            while_bool = False
                                            break
                                        else:
                                            continue
                                # print("customers_5_item  minute_sum= {}".format(minute_sum))
                                # print("customers_5_item.minute , customers_5_item_GO.minute= {}  ,   {}".format(customers_5_item.minute , customers_5_item_GO.minute))
                                dests_6 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_5_item_GO.id) | Q(location2_id=customers_5_item_GO.id)).order_by('minute')
                                if dests_6.count() == 0:
                                    while_bool = False
                                    return_while = True
                                    print('var dests_6= {}'.format(dests_6.count()))
                                    break
                                else:
                                    pass
                                    print('yoxdu dests_6= {}'.format(dests_6.count()))
                                res_val_5 = copy.deepcopy(res_val)
                                minute_sum_5 = copy.deepcopy(minute_sum)
                                for customers_6_item in dests_6:
                                    # while_bool = False
                                    # return_while = True
                                    # break
                                    res_val = copy.deepcopy(res_val_5)
                                    minute_sum = copy.deepcopy(minute_sum_5)
                                    if return_while:
                                        break
                                    if customers_6_item.location1_id == customers_5_item_GO.id:
                                        customers_6_item_GO = customers_6_item.location2
                                    else:
                                        customers_6_item_GO = customers_6_item.location1
                                    # res_val += [customers_6_item_GO.id]
                                    # print("customers_6_item  res_val= {}".format(res_val))
                                    # # before_vals.append(customers_6_item.id)
                                    # # minute_sum += customers_6_item.minute + customers_6_item_GO.minute
                                    # print("customers_6_item  minute_sum = {}".format(minute_sum))
                                    # print("customers_6_item.minute , customers_6_item_GO.minute= {}  ,   {}".format(customers_6_item.minute , customers_6_item_GO.minute))
                                    if order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.minute <= minute:
                                        minute_sum += customers_6_item.minute + customers_6_item_GO.minute
                                        res_val += [
                                            customers_6_item_GO.id,
                                        ]
                                        # pass
                                    elif order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.minute > minute:
                                        print("order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.minute > minute")
                                        customers_8_item_i += (copy.deepcopy(dests_6.count()) - 1) * (
                                        copy.deepcopy(dests_6.count()) - 2)
                                        if customers_8_item_i == dests_6.count() * (dests_6.count() - 1) * (dests_6.count() - 2) or order_index == 8 and first_dests.last().id == customers_1_item.id:
                                            print("customers_8_item_i == dests_6.count() * (dests_6.count() - 1) * (dests_6.count() - 2) or order_index == 8 and first_dests.last().id == customers_1_item.id")
                                            return_while = True
                                            while_bool = False
                                            break
                                        continue
                                    else:
                                        print("6 else")
                                        print("order_index else = {}".format(order_index))
                                        if minute_sum + customers_6_item.minute + customers_6_item_GO.minute <= minute:
                                            print("minute_sum + customers_6_item.minute + customers_6_item_GO.minute <= minute")
                                            minute_sum += customers_6_item.minute + customers_6_item_GO.minute
                                            res_val += [
                                                customers_6_item_GO.id,
                                            ]
                                            res_val_i = 0
                                            for res_val_item in res_val:
                                                if res_val_i > 0:
                                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                                res_val_i += 1
                                            result_list.append(copy.deepcopy(res_val))
                                            return_while = True
                                            break
                                        else:
                                            if order_index == 6 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            else:
                                                continue
                                    dests_7 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_6_item_GO.id) | Q(location2_id=customers_6_item_GO.id)).order_by('minute')
                                    if dests_7.count() == 0:
                                        while_bool = False
                                        return_while = True
                                        break
                                    res_val_6 = copy.deepcopy(res_val)
                                    minute_sum_6 = copy.deepcopy(minute_sum)
                                    # print("customers_6_item  minute_sum = {}".format(minute_sum))
                                    # print("customers_6_item  res_val = {}".format(res_val))
                                    print("customers_6_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                                    for customers_7_item in dests_7:
                                        # while_bool = False
                                        # return_while = True
                                        # break
                                        res_val = copy.deepcopy(res_val_6)
                                        minute_sum = copy.deepcopy(minute_sum_6)
                                        if return_while:
                                            break
                                        if customers_7_item.location1_id == customers_6_item_GO.id:
                                            customers_7_item_GO = customers_7_item.location2
                                        else:
                                            customers_7_item_GO = customers_7_item.location1
                                        # res_val += [
                                        #             customers_7_item_GO.id,
                                        #         ]
                                        # print("customers_7_item  res_val= {}".format(res_val))
                                        # before_vals.append(customers_7_item.id)
                                        # minute_sum += customers_7_item.minute + customers_7_item_GO.minute
                                        if order_index > 7 and minute_sum + customers_7_item.minute + customers_7_item_GO.minute <= minute:
                                            minute_sum += customers_7_item.minute + customers_7_item_GO.minute
                                            res_val += [
                                                customers_7_item_GO.id,
                                            ]
                                            # pass
                                        elif order_index > 7 and minute_sum + customers_7_item.minute + customers_7_item_GO.minute > minute:
                                            customers_8_item_i += copy.deepcopy(dests_7.count()) - 1
                                            customers_9_item_i += (copy.deepcopy(dests_7.count())-1)*(copy.deepcopy(dests_7.count())-2)
                                            if customers_9_item_i == dests_7.count() * (dests_7.count() - 1) * (
                                                dests_7.count() - 2) or order_index == 9 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            if customers_8_item_i == dests_6.count() * (dests_6.count() - 1) * (
                                                dests_6.count() - 2) or order_index == 8 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            continue
                                        else:
                                            print("order_index else = {}".format(order_index))

                                            if minute_sum + customers_7_item.minute + customers_7_item_GO.minute <= minute:
                                                minute_sum += customers_7_item.minute + customers_7_item_GO.minute
                                                res_val += [
                                                    customers_7_item_GO.id,
                                                ]
                                                res_val_i = 0
                                                for res_val_item in res_val:
                                                    if res_val_i > 0:
                                                        result_exc_list.append(copy.deepcopy(res_val_item))
                                                    res_val_i += 1
                                                result_list.append(copy.deepcopy(res_val))
                                                return_while = True
                                                break
                                            else:
                                                if order_index == 7 and first_dests.last().id == customers_1_item.id:
                                                    return_while = True
                                                    while_bool = False
                                                    break
                                                else:
                                                    continue
                                        # print("customers_7_item update  res_val= {}".format(res_val))
                                        # print("customers_7_item  minute_sum= {}".format(minute_sum))
                                        # print("customers_7_item.minute , customers_7_item_GO.minute= {}  ,   {}".format(customers_7_item.minute , customers_7_item_GO.minute))
                                        dests_8 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_7_item_GO.id) | Q(location2_id=customers_7_item_GO.id)).order_by('minute')
                                        if dests_8.count() == 0:
                                            while_bool = False
                                            return_while = True
                                            break
                                        res_val_7 = copy.deepcopy(res_val)
                                        minute_sum_7 = copy.deepcopy(minute_sum)
                                        print("customers_7_item  res_val= {}, = minute_sum= {}".format(res_val,
                                                                                                       minute_sum))
                                        for customers_8_item in dests_8:
                                            customers_8_item_i += 1
                                            res_val = copy.deepcopy(res_val_7)
                                            minute_sum = copy.deepcopy(minute_sum_7)
                                            if return_while:
                                                break
                                            if customers_8_item.location1_id == customers_7_item_GO.id:
                                                customers_8_item_GO = customers_8_item.location2
                                            else:
                                                customers_8_item_GO = customers_8_item.location1
                                            # before_vals.append(customers_8_item.id)

                                            if order_index > 8 and minute_sum + customers_8_item.minute + customers_8_item_GO.minute <= minute:
                                                minute_sum += customers_8_item.minute + customers_8_item_GO.minute
                                                res_val += [
                                                            customers_8_item_GO.id,
                                                        ]
                                                # pass
                                            elif order_index > 8 and minute_sum + customers_8_item.minute + customers_8_item_GO.minute > minute:
                                                customers_9_item_i += copy.deepcopy(dests_8.count())-1
                                                if customers_9_item_i == dests_7.count() * (dests_7.count() - 1) * (
                                                    dests_7.count() - 2) and order_index == 9 or order_index == 9 and first_dests.last().id == customers_1_item.id:
                                                    return_while = True
                                                    while_bool = False
                                                    break
                                                continue
                                            else:
                                                print("order_index else = {}".format(order_index))
                                                if minute_sum + customers_8_item.minute + customers_8_item_GO.minute <= minute:
                                                    minute_sum += customers_8_item.minute + customers_8_item_GO.minute
                                                    res_val += [
                                                                customers_8_item_GO.id,
                                                            ]
                                                    res_val_i = 0
                                                    for res_val_item in res_val:
                                                        if res_val_i > 0:
                                                            result_exc_list.append(copy.deepcopy(res_val_item))
                                                        res_val_i += 1
                                                    result_list.append(copy.deepcopy(res_val))
                                                    return_while = True
                                                    break
                                                else:
                                                    if order_index == 8 and first_dests.last().id == customers_1_item.id:
                                                        return_while = True
                                                        while_bool = False
                                                        break
                                                    else:
                                                        continue
                                            # print("customers_8_item  minute_sum= {}".format(minute_sum))
                                            # print("customers_8_item  res_val= {}".format(res_val))
                                            # print("customers_8_item.minute , customers_8_item_GO.minute= {}  ,   {}".format(customers_8_item.minute , customers_8_item_GO.minute))
                                            print("customers_8_item  res_val= {}, = minute_sum= {}".format(res_val,minute_sum))
                                            dests_9 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_8_item_GO.id) | Q(location2_id=customers_8_item_GO.id))
                                            if dests_9.count() == 0:
                                                while_bool = False
                                                return_while = True
                                                break
                                            res_val_8 = copy.deepcopy(res_val)
                                            minute_sum_8 = copy.deepcopy(minute_sum)
                                            for customers_9_item in dests_9:
                                                customers_9_item_i += 1
                                                res_val = copy.deepcopy(res_val_8)
                                                minute_sum = copy.deepcopy(minute_sum_8)
                                                if return_while:
                                                    break
                                                if customers_9_item.location1_id == customers_8_item_GO.id:
                                                    customers_9_item_GO = customers_9_item.location2
                                                else:
                                                    customers_9_item_GO = customers_9_item.location1
                                                customers_9_bool = True
                                                # before_vals.append(customers_9_item.id)
                                                # print("customers_9_item  res_val= {}".format(res_val))
                                                # calculate_minute_val =  calculate_minute(res_val,minute_all=minute,dest_list=dest_list)
                                                # return calculate_minute_val
                                                # minute_sum = customers_1_item.minute + customers_2_item_GO.minute + customers_3_item.minute + customers_3_item_GO.minute + customers_4_item.minute + customers_4_item_GO.minute + customers_5_item.minute + customers_5_item_GO.minute + customers_6_item.minute + customers_6_item_GO.minute + customers_7_item.minute + customers_7_item_GO.minute + customers_8_item.minute + customers_8_item_GO.minute + customers_9_item.minute + customers_9_item_GO.minute
                                                if minute_sum + customers_9_item.minute + customers_9_item_GO.minute <= minute:
                                                    minute_sum += customers_9_item.minute + customers_9_item_GO.minute
                                                    res_val += [
                                                                customers_9_item_GO.id
                                                            ]
                                                    res_val_i = 0
                                                    for res_val_item in res_val:
                                                        if res_val_i > 0:
                                                            result_exc_list.append(copy.deepcopy(res_val_item))
                                                        res_val_i += 1
                                                    result_list.append(copy.deepcopy(res_val))
                                                    return_while = True
                                                    print("customers_9_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                                                    # print("customers_9_item  minute_sum= {}".format(minute_sum))
                                                    # print("customers_9_item.minute , customers_9_item_GO.minute= {}  ,   {}".format(customers_9_item.minute , customers_9_item_GO.minute))
                                                    break
                                                else:
                                                    if customers_9_item_i == dests_7.count() * (dests_7.count()-1) * (dests_7.count()-2) or order_index == 9 and first_dests.last().id == customers_1_item.id:
                                                        return_while = True
                                                        while_bool = False
                                                        break
                                                    else:
                                                        continue
                                                # print("customers_9_item  minute_sum= {}".format(minute_sum))
                                                # print("customers_9_item  result_exc_list= {}".format(result_exc_list))
                                                # print("customers_9_item  result_list= {}".format(result_list))
                                                # print("customers_9_item.minute , customers_9_item_GO.minute= {}  ,   {}".format(customers_9_item.minute , customers_9_item_GO.minute))

    return result_list


def result1p1_seven(exc_list, minute):
    from content.models import Location,LocationDistance
    # from django.forms.models import model_to_dict
    # from content.new_main import calculate_minute_1times as nm_calculate_minute_1times

    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    result_list = []
    result_exc_list = []

        # .order_by('-minute', '-location1__minute','-location2__minute')
    # dest_list = []
    # for loc_destination_item in loc_destinations:
    #     dest_list.append(obj_to_dict_dest(loc_destination_item))
    loc_destinations = LocationDistance.objects.exclude(
        Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).exclude(
        Q(location1__work_times=3) | Q(location2__work_times=3)).order_by('minute')
    main_location = Location.objects.filter(our_company=True).first()
    customers = Location.objects.exclude(id__in=exc_list).exclude(our_company=True)
    while_bool = True
    before_vals = []
    customers_11_bool = False
    # res_val = []
    for_bool = True
    while_bool = True
    return_while = False
    for order_index in range(7, 0, -1):
        if for_bool is False:
            # print('return_while = {}'.format(return_while))
            break
        print('return for')
        # print(while_bool)
        print("<order_index> = <{}>".format(order_index))
        print("<while_bool> = <{}>".format(while_bool))
        print("<return_while> = <{}>".format(return_while))
        while_bool = True
        return_while = False
        print('return for')
        while while_bool:
            print('head yoxdu return_while = {}'.format(return_while))
            # if while_bool is False:
            #     # print('return_while = {}'.format(return_while))
            #     break
            customers_7_item_i = 0
            customers_6_item_i = 0
            customers_5_item_i = 0
            return_while = False
            res_val = [
                main_location.id,
            ]
            # print("while_bool  res_val= {}".format(res_val))
            first_dests = loc_destinations.exclude(
                Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                Q(location1_id=main_location.id) | Q(location2_id=main_location.id)).order_by('minute')

            if first_dests.count() == 0:
                # # print('var first_dests= {}'.format(first_dests.count()))
                break
            else:
                pass
            print('foot yoxdu first_dests = {}'.format(first_dests.count()))
            for customers_1_item in first_dests:
                if return_while:
                    # print('return_while = {}'.format(return_while))
                    break
                # for_break = False
                # if for_break:
                #     continue
                # before_vals.append(customers_1_item.id)
                if customers_1_item.location1_id == main_location.id:
                    customers_1_item_GO = customers_1_item.location2
                    customers_1_item_ord = 2
                else:
                    customers_1_item_GO = customers_1_item.location1
                    customers_1_item_ord = 1
                # res_val += [customers_1_item_GO.id]
                minute_sum = 0
                # print("customers_1_item.minute , customers_1_item_GO.minute= {}  ,   {}".format(customers_1_item.minute , customers_1_item_GO.minute))
                if order_index > 1 and minute_sum + customers_1_item.minute + customers_1_item_GO.minute <= minute:
                    print("@@@@@@@@@@@ if 1")
                    minute_sum += customers_1_item.minute + customers_1_item_GO.minute
                    res_val += [
                        customers_1_item_GO.id,
                    ]
                    # pass
                elif order_index > 1 and minute_sum + customers_1_item.minute + customers_1_item_GO.minute > minute:
                    print("@@@@@@@@@@@ elif 1")
                    continue
                else:
                    print("@@@@@@@@@@@ else 1")
                    print("@@@@@@@@@@@ {} - {} - {}".format(order_index,
                                                            minute_sum + customers_1_item.minute + customers_1_item_GO.minute,
                                                            minute))
                    # print("order_index else = {}".format(order_index))
                    if minute_sum + customers_1_item.minute + customers_1_item_GO.minute <= minute:
                        # print("@@@@@@@@@@@ if 1")
                        minute_sum += customers_1_item.minute + customers_1_item_GO.minute
                        res_val += [
                            customers_1_item_GO.id,
                        ]
                        # print('+++++++++++++++++++++++++++++++++++++++minute_sum <= minute++++++++++++++++++++++++++++++++++++++++')
                        # print('+++++++++++++++++++++++++++++++++++++++ res_val = {} ++++++++++++++++++++++++++++++++++++++++'.format(res_val))
                        res_val_i = 0
                        for res_val_item in res_val:
                            res_val_i += 1
                            if res_val_i > 0:
                                result_exc_list.append(copy.deepcopy(res_val_item))
                        result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                        return_while = True
                        while_bool = False
                        for_bool = False
                        # print('+++++++++++++++++++++++++++++++++++++++ return_while = {} ++++++++++++++++++++++++++++++++++++++++'.format(return_while))
                        break
                    else:
                        if order_index == 1 and first_dests.last().id == customers_1_item.id:
                            return_while = True
                            while_bool = False
                            break
                        else:
                            continue
                print("customers_1_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                # print("customers_1_item  minute_sum= {}".format(minute_sum))
                dests_2 = loc_destinations.exclude(
                    Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                    Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                    Q(location1_id=customers_1_item_GO.id) | Q(location2_id=customers_1_item_GO.id)).order_by('minute')
                if dests_2.count() == 0:
                    while_bool = False
                    return_while = True
                    print('var dests_2= {}'.format(dests_2.count()))
                    break
                else:
                    print('yoxdu dests_2 = {}'.format(dests_2.count()))
                    pass
                res_val_1 = copy.deepcopy(res_val)
                minute_sum_1 = copy.deepcopy(minute_sum)
                for customers_2_item in dests_2:
                    res_val = copy.deepcopy(res_val_1)
                    minute_sum = copy.deepcopy(minute_sum_1)
                    if return_while:
                        break

                    if customers_2_item.location1_id == customers_1_item_GO.id:
                        customers_2_item_GO = customers_2_item.location2
                    else:
                        customers_2_item_GO = customers_2_item.location1
                    # res_val += [customers_2_item_GO.id]
                    # print("customers_2_item  res_val= {}".format(res_val))
                    # before_vals.append(customers_2_item.id)
                    # minute_sum += customers_2_item.minute + customers_2_item_GO.minute
                    # print("customers_2_item  minute_sum= {}".format(minute_sum))
                    # print("customers_2_item.minute , customers_2_item_GO.minute= {}  ,   {}".format(customers_2_item.minute , customers_2_item_GO.minute))
                    if order_index > 2 and minute_sum + customers_2_item.minute + customers_2_item_GO.minute <= minute:
                        minute_sum += customers_2_item.minute + customers_2_item_GO.minute
                        res_val += [
                            customers_2_item_GO.id,
                        ]
                        # pass
                    elif order_index > 2 and minute_sum + customers_2_item.minute + customers_2_item_GO.minute > minute:
                        continue
                    else:
                        print("order_index else = {}".format(order_index))
                        if minute_sum + customers_2_item.minute + customers_2_item_GO.minute <= minute:
                            minute_sum += customers_2_item.minute + customers_2_item_GO.minute
                            res_val += [
                                customers_2_item_GO.id,
                            ]
                            res_val_i = 0
                            for res_val_item in res_val:
                                if res_val_i > 0:
                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                res_val_i += 1
                            result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                            return_while = True
                            while_bool = False
                            for_bool = False
                            break
                        else:
                            if order_index == 2 and first_dests.last().id == customers_1_item.id:
                                return_while = True
                                while_bool = False
                                break
                            else:
                                continue
                    print("customers_2_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                    dests_3 = loc_destinations.exclude(
                        Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                        Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                        Q(location1_id=customers_2_item_GO.id) | Q(location2_id=customers_2_item_GO.id)).order_by(
                        'minute')
                    if dests_3.count() == 0:
                        while_bool = False
                        return_while = True
                        print('var dests_3= {}'.format(dests_3.count()))
                        break
                    else:
                        print('yoxdu dests_3= {}'.format(dests_3.count()))
                        pass
                    res_val_2 = copy.deepcopy(res_val)
                    minute_sum_2 = copy.deepcopy(minute_sum)

                    for customers_3_item in dests_3:
                        res_val = copy.deepcopy(res_val_2)
                        minute_sum = copy.deepcopy(minute_sum_2)
                        if return_while:
                            break
                        if customers_3_item.location1_id == customers_2_item_GO.id:
                            customers_3_item_GO = customers_3_item.location2
                        else:
                            customers_3_item_GO = customers_3_item.location1
                        # res_val += [customers_3_item_GO.id]
                        print("customers_3_item  res_val= {}".format(res_val))
                        # before_vals.append(customers_3_item.id)
                        if order_index > 3 and minute_sum + customers_3_item.minute + customers_3_item_GO.minute <= minute:
                            minute_sum += customers_3_item.minute + customers_3_item_GO.minute
                            res_val += [
                                customers_3_item_GO.id,
                            ]
                            # pass
                        elif order_index > 3 and minute_sum + customers_3_item.minute + customers_3_item_GO.minute > minute:
                            continue
                        else:
                            print("order_index else = {}".format(order_index))
                            if minute_sum + customers_3_item.minute + customers_3_item_GO.minute <= minute:
                                minute_sum += customers_3_item.minute + customers_3_item_GO.minute
                                res_val += [
                                    customers_3_item_GO.id,
                                ]
                                res_val_i = 0
                                for res_val_item in res_val:
                                    if res_val_i > 0:
                                        result_exc_list.append(copy.deepcopy(res_val_item))
                                    res_val_i += 1
                                result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                return_while = True
                                while_bool = False
                                for_bool = False
                                break
                            else:
                                if order_index == 3 and first_dests.last().id == customers_1_item.id:
                                    return_while = True
                                    while_bool = False
                                    break
                                else:
                                    continue
                        # print("customers_3_item  minute_sum= {}".format(minute_sum))
                        # print("customers_3_item.minute , customers_3_item_GO.minute= {}  ,   {}".format(customers_3_item.minute , customers_3_item_GO.minute))
                        dests_4 = loc_destinations.exclude(
                            Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                            Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                            Q(location1_id=customers_3_item_GO.id) | Q(
                                location2_id=customers_3_item_GO.id)).order_by('minute')
                        if dests_4.count() == 0:
                            while_bool = False
                            return_while = True
                            print('var dests_4= {}'.format(dests_4.count()))
                            break
                        else:
                            pass
                            print('yoxdu dests_4= {}'.format(dests_4.count()))
                        res_val_3 = copy.deepcopy(res_val)
                        minute_sum_3 = copy.deepcopy(minute_sum)
                        for customers_4_item in dests_4:
                            # while_bool = False
                            # return_while = True
                            # break
                            res_val = copy.deepcopy(res_val_3)
                            minute_sum = copy.deepcopy(minute_sum_3)
                            if return_while:
                                break
                            if customers_4_item.location1_id == customers_3_item_GO.id:
                                customers_4_item_GO = customers_4_item.location2
                            else:
                                customers_4_item_GO = customers_4_item.location1
                            # res_val += [customers_4_item_GO.id]
                            # print("customers_4_item  res_val= {}".format(res_val))
                            # # before_vals.append(customers_4_item.id)
                            # # minute_sum += customers_4_item.minute + customers_4_item_GO.minute
                            # print("customers_4_item  minute_sum = {}".format(minute_sum))
                            # print("customers_4_item.minute , customers_4_item_GO.minute= {}  ,   {}".format(customers_4_item.minute , customers_4_item_GO.minute))
                            if order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.minute <= minute:
                                minute_sum += customers_4_item.minute + customers_4_item_GO.minute
                                res_val += [
                                    customers_4_item_GO.id,
                                ]
                                # pass
                            elif order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.minute > minute:
                                print(
                                    "order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.minute > minute")
                                customers_6_item_i += (copy.deepcopy(dests_4.count()) - 1) * (
                                    copy.deepcopy(dests_4.count()) - 2)
                                if customers_6_item_i == dests_4.count() * (dests_4.count() - 1) * (
                                            dests_4.count() - 2) or order_index == 6 and first_dests.last().id == customers_1_item.id:
                                    print(
                                        "customers_6_item_i == dests_4.count() * (dests_4.count() - 1) * (dests_4.count() - 2) or order_index == 6 and first_dests.last().id == customers_1_item.id")
                                    return_while = True
                                    while_bool = False
                                    break
                                continue
                            else:
                                print("4 else")
                                print("order_index else = {}".format(order_index))
                                if minute_sum + customers_4_item.minute + customers_4_item_GO.minute <= minute:
                                    print(
                                        "minute_sum + customers_4_item.minute + customers_4_item_GO.minute <= minute")
                                    minute_sum += customers_4_item.minute + customers_4_item_GO.minute
                                    res_val += [
                                        customers_4_item_GO.id,
                                    ]
                                    res_val_i = 0
                                    for res_val_item in res_val:
                                        if res_val_i > 0:
                                            result_exc_list.append(copy.deepcopy(res_val_item))
                                        res_val_i += 1
                                    result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                    return_while = True
                                    while_bool = False
                                    for_bool = False
                                    break
                                else:
                                    if order_index == 4 and first_dests.last().id == customers_1_item.id:
                                        return_while = True
                                        while_bool = False
                                        break
                                    else:
                                        continue
                            dests_5 = loc_destinations.exclude(
                                Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                                Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                                Q(location1_id=customers_4_item_GO.id) | Q(
                                    location2_id=customers_4_item_GO.id)).order_by('minute')
                            if dests_5.count() == 0:
                                while_bool = False
                                return_while = True
                                break
                            res_val_4 = copy.deepcopy(res_val)
                            minute_sum_4 = copy.deepcopy(minute_sum)
                            # print("customers_4_item  minute_sum = {}".format(minute_sum))
                            # print("customers_4_item  res_val = {}".format(res_val))
                            print("customers_4_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                            for customers_5_item in dests_5:
                                # while_bool = False
                                # return_while = True
                                # break
                                res_val = copy.deepcopy(res_val_4)
                                minute_sum = copy.deepcopy(minute_sum_4)
                                if return_while:
                                    break
                                if customers_5_item.location1_id == customers_4_item_GO.id:
                                    customers_5_item_GO = customers_5_item.location2
                                else:
                                    customers_5_item_GO = customers_5_item.location1
                                # res_val += [
                                #             customers_5_item_GO.id,
                                #         ]
                                # print("customers_5_item  res_val= {}".format(res_val))
                                # before_vals.append(customers_5_item.id)
                                # minute_sum += customers_5_item.minute + customers_5_item_GO.minute
                                if order_index > 5 and minute_sum + customers_5_item.minute + customers_5_item_GO.minute <= minute:
                                    minute_sum += customers_5_item.minute + customers_5_item_GO.minute
                                    res_val += [
                                        customers_5_item_GO.id,
                                    ]
                                    # pass
                                elif order_index > 5 and minute_sum + customers_5_item.minute + customers_5_item_GO.minute > minute:
                                    customers_6_item_i += copy.deepcopy(dests_5.count()) - 1
                                    customers_7_item_i += (copy.deepcopy(dests_5.count()) - 1) * (
                                        copy.deepcopy(dests_5.count()) - 2)
                                    if customers_7_item_i == dests_5.count() * (dests_5.count() - 1) * (
                                                dests_5.count() - 2) or order_index == 7 and first_dests.last().id == customers_1_item.id:
                                        return_while = True
                                        while_bool = False
                                        break
                                    if customers_6_item_i == dests_4.count() * (dests_4.count() - 1) * (
                                                dests_4.count() - 2) or order_index == 6 and first_dests.last().id == customers_1_item.id:
                                        return_while = True
                                        while_bool = False
                                        break
                                    continue
                                else:
                                    print("order_index else = {}".format(order_index))

                                    if minute_sum + customers_5_item.minute + customers_5_item_GO.minute <= minute:
                                        minute_sum += customers_5_item.minute + customers_5_item_GO.minute
                                        res_val += [
                                            customers_5_item_GO.id,
                                        ]
                                        res_val_i = 0
                                        for res_val_item in res_val:
                                            if res_val_i > 0:
                                                result_exc_list.append(copy.deepcopy(res_val_item))
                                            res_val_i += 1
                                        result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                        return_while = True
                                        while_bool = False
                                        for_bool = False
                                        break
                                    else:
                                        if order_index == 5 and first_dests.last().id == customers_1_item.id:
                                            return_while = True
                                            while_bool = False
                                            break
                                        else:
                                            continue
                                # print("customers_5_item update  res_val= {}".format(res_val))
                                # print("customers_5_item  minute_sum= {}".format(minute_sum))
                                # print("customers_5_item.minute , customers_5_item_GO.minute= {}  ,   {}".format(customers_5_item.minute , customers_5_item_GO.minute))
                                dests_6 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(
                                    location2_id__in=result_exc_list)).exclude(
                                    Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                                    Q(location1_id=customers_5_item_GO.id) | Q(
                                        location2_id=customers_5_item_GO.id)).order_by('minute')
                                if dests_6.count() == 0:
                                    while_bool = False
                                    return_while = True
                                    break
                                res_val_5 = copy.deepcopy(res_val)
                                minute_sum_5 = copy.deepcopy(minute_sum)
                                print("customers_5_item  res_val= {}, = minute_sum= {}".format(res_val,
                                                                                               minute_sum))
                                for customers_6_item in dests_6:
                                    customers_6_item_i += 1
                                    res_val = copy.deepcopy(res_val_5)
                                    minute_sum = copy.deepcopy(minute_sum_5)
                                    if return_while:
                                        break
                                    if customers_6_item.location1_id == customers_5_item_GO.id:
                                        customers_6_item_GO = customers_6_item.location2
                                    else:
                                        customers_6_item_GO = customers_6_item.location1
                                    # before_vals.append(customers_6_item.id)

                                    if order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.minute <= minute:
                                        minute_sum += customers_6_item.minute + customers_6_item_GO.minute
                                        res_val += [
                                            customers_6_item_GO.id,
                                        ]
                                        # pass
                                    elif order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.minute > minute:
                                        customers_7_item_i += copy.deepcopy(dests_6.count()) - 1
                                        if customers_7_item_i == dests_5.count() * (dests_5.count() - 1) * (
                                                    dests_5.count() - 2) and order_index == 7 or order_index == 7 and first_dests.last().id == customers_1_item.id:
                                            return_while = True
                                            while_bool = False
                                            break
                                        continue
                                    else:
                                        print("order_index else = {}".format(order_index))
                                        if minute_sum + customers_6_item.minute + customers_6_item_GO.minute <= minute:
                                            minute_sum += customers_6_item.minute + customers_6_item_GO.minute
                                            res_val += [
                                                customers_6_item_GO.id,
                                            ]
                                            res_val_i = 0
                                            for res_val_item in res_val:
                                                if res_val_i > 0:
                                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                                res_val_i += 1
                                            result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                            return_while = True
                                            while_bool = False
                                            for_bool = False
                                            break
                                        else:
                                            if order_index == 6 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            else:
                                                continue
                                    # print("customers_6_item  minute_sum= {}".format(minute_sum))
                                    # print("customers_6_item  res_val= {}".format(res_val))
                                    # print("customers_6_item.minute , customers_6_item_GO.minute= {}  ,   {}".format(customers_6_item.minute , customers_6_item_GO.minute))
                                    print("customers_6_item  res_val= {}, = minute_sum= {}".format(res_val,
                                                                                                   minute_sum))
                                    dests_7 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(
                                        location2_id__in=result_exc_list)).exclude(
                                        Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                                        Q(location1_id=customers_6_item_GO.id) | Q(
                                            location2_id=customers_6_item_GO.id))
                                    if dests_7.count() == 0:
                                        while_bool = False
                                        return_while = True
                                        break
                                    res_val_6 = copy.deepcopy(res_val)
                                    minute_sum_6 = copy.deepcopy(minute_sum)
                                    for customers_7_item in dests_7:
                                        customers_7_item_i += 1
                                        res_val = copy.deepcopy(res_val_6)
                                        minute_sum = copy.deepcopy(minute_sum_6)
                                        if return_while:
                                            break
                                        if customers_7_item.location1_id == customers_6_item_GO.id:
                                            customers_7_item_GO = customers_7_item.location2
                                        else:
                                            customers_7_item_GO = customers_7_item.location1
                                        customers_7_bool = True
                                        # before_vals.append(customers_7_item.id)
                                        # print("customers_7_item  res_val= {}".format(res_val))
                                        # calculate_minute_val =  calculate_minute(res_val,minute_all=minute,dest_list=dest_list)
                                        # return calculate_minute_val
                                        # minute_sum = customers_1_item.minute + customers_2_item_GO.minute + customers_3_item.minute + customers_3_item_GO.minute + customers_2_item.minute + customers_2_item_GO.minute + customers_3_item.minute + customers_3_item_GO.minute + customers_4_item.minute + customers_4_item_GO.minute + customers_5_item.minute + customers_5_item_GO.minute + customers_6_item.minute + customers_6_item_GO.minute + customers_7_item.minute + customers_7_item_GO.minute
                                        if minute_sum + customers_7_item.minute + customers_7_item_GO.minute <= minute:
                                            minute_sum += customers_7_item.minute + customers_7_item_GO.minute
                                            res_val += [
                                                customers_7_item_GO.id
                                            ]
                                            res_val_i = 0
                                            for res_val_item in res_val:
                                                if res_val_i > 0:
                                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                                res_val_i += 1
                                            result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                            return_while = True
                                            while_bool = False
                                            for_bool = False
                                            print("customers_7_item  res_val= {}, = minute_sum= {}".format(res_val,
                                                                                                           minute_sum))
                                            # print("customers_7_item  minute_sum= {}".format(minute_sum))
                                            # print("customers_7_item.minute , customers_7_item_GO.minute= {}  ,   {}".format(customers_7_item.minute , customers_7_item_GO.minute))
                                            break
                                        else:
                                            if customers_7_item_i == dests_5.count() * (dests_5.count() - 1) * (
                                                        dests_5.count() - 2) or order_index == 7 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            else:
                                                continue
                                                # print("customers_7_item  minute_sum= {}".format(minute_sum))
                                                # print("customers_7_item  result_exc_list= {}".format(result_exc_list))
                                                # print("customers_7_item  result_list= {}".format(result_list))
                                                # print("customers_7_item.minute , customers_7_item_GO.minute= {}  ,   {}".format(customers_7_item.minute , customers_7_item_GO.minute))

    return result_list


def sub_result1p1(week_day,custom_start_id,exc_list, minute):
    from content.models import Location,LocationDistance
    # from django.forms.models import model_to_dict
    # from work.new_main import calculate_minute_1times as nm_calculate_minute_1times

    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    result_list = []
    result_exc_list = []

        # .order_by('-minute', '-location1__minute','-location2__minute')
    # dest_list = []
    # for loc_destination_item in loc_destinations:
    #     dest_list.append(obj_to_dict_dest(loc_destination_item))
    loc_destinations = LocationDistance.objects.exclude(
        Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).exclude(
        Q(location1__work_times=3) | Q(location2__work_times=3)).order_by('minute   ')
    if custom_start_id == 0:
        main_customer = Location.objects.filter(our_company=True).first()
    else:
        main_customer = Location.objects.filter(id=custom_start_id).first()
    # customers = Location.objects.exclude(id__in=exc_list).exclude(our_company=True)
    while_bool = True
    for_bool = True
    before_vals = []
    customers_11_bool = False
    # res_val = []
    while_bool = True
    return_while = False
    for order_index in range(9, 0, -1):
        if for_bool is False:
            # print('return_while = {}'.format(return_while))
            break
        print('return for')
        # print(while_bool)
        print("<order_index> = <{}>".format(order_index))
        print("<while_bool> = <{}>".format(while_bool))
        print("<return_while> = <{}>".format(return_while))
        while_bool = True
        return_while = False
        print('return for')
        while while_bool:
            print('head yoxdu return_while = {}'.format(return_while))
            # if while_bool is False:
            #     # print('return_while = {}'.format(return_while))
            #     break
            customers_9_item_i = 0
            customers_8_item_i = 0
            customers_7_item_i = 0
            return_while = False
            res_val = [
                       main_customer.id,
                    ]
            # print("while_bool  res_val= {}".format(res_val))
            first_dests = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=main_customer.id) | Q(location2_id=main_customer.id)).order_by('minute')

            if first_dests.count() == 0:
                # # print('var first_dests= {}'.format(first_dests.count()))
                break
            else:
                pass
            print('foot yoxdu first_dests = {}'.format(first_dests.count()))
            for customers_1_item in first_dests:
                if return_while:
                    # print('return_while = {}'.format(return_while))
                    break
                # for_break = False
                # if for_break:
                #     continue
                # before_vals.append(customers_1_item.id)
                if customers_1_item.location1_id == main_customer.id:
                    customers_1_item_GO = customers_1_item.location2
                    customers_1_item_ord = 2
                else:
                    customers_1_item_GO = customers_1_item.location1
                    customers_1_item_ord = 1
                # res_val += [customers_1_item_GO.id]
                minute_sum = 0
                # print("customers_1_item.minute , customers_1_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_1_item.minute , customers_1_item_GO.get_customer_day_minute(week_day)))
                if order_index > 1 and minute_sum + customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(week_day) <= minute:
                    print("@@@@@@@@@@@ if 1")
                    minute_sum += customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(week_day)
                    res_val += [
                        customers_1_item_GO.id,
                    ]
                    # pass
                elif order_index > 1 and minute_sum + customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(week_day) > minute:
                    print("@@@@@@@@@@@ elif 1")
                    continue
                else:
                    print("@@@@@@@@@@@ else 1")
                    print("@@@@@@@@@@@ {} - {} - {}".format(order_index , minute_sum + customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(week_day) , minute))
                    # print("order_index else = {}".format(order_index))
                    if minute_sum + customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(week_day) <= minute:
                        # print("@@@@@@@@@@@ if 1")
                        minute_sum += customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(week_day)
                        res_val += [
                            customers_1_item_GO.id,
                        ]
                        # print('+++++++++++++++++++++++++++++++++++++++minute_sum <= minute++++++++++++++++++++++++++++++++++++++++')
                        # print('+++++++++++++++++++++++++++++++++++++++ res_val = {} ++++++++++++++++++++++++++++++++++++++++'.format(res_val))
                        res_val_i = 0
                        for res_val_item in res_val:
                            res_val_i += 1
                            if res_val_i > 0:
                                result_exc_list.append(copy.deepcopy(res_val_item))
                        result_list.append(copy.deepcopy(res_val + [[minute_sum]]))

                        return_while = True
                        while_bool = False
                        for_bool = False
                        # print('+++++++++++++++++++++++++++++++++++++++ return_while = {} ++++++++++++++++++++++++++++++++++++++++'.format(return_while))
                        break
                    else:
                        if order_index == 1 and first_dests.last().id == customers_1_item.id:
                            return_while = True
                            while_bool = False
                            break
                        else:
                            continue
                print("customers_1_item  res_val= {}, = minute_sum= {}".format(res_val,minute_sum))
                # print("customers_1_item  minute_sum= {}".format(minute_sum))
                dests_2 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_1_item_GO.id) | Q(location2_id=customers_1_item_GO.id)).order_by('minute')
                if dests_2.count() == 0:
                    while_bool = False
                    return_while = True
                    print('var dests_2= {}'.format(dests_2.count()))
                    break
                else:
                    print('yoxdu dests_2 = {}'.format(dests_2.count()))
                    pass
                res_val_1 = copy.deepcopy(res_val)
                minute_sum_1 = copy.deepcopy(minute_sum)
                for customers_2_item in dests_2:
                    res_val = copy.deepcopy(res_val_1)
                    minute_sum = copy.deepcopy(minute_sum_1)
                    if return_while:
                        break

                    if customers_2_item.location1_id == customers_1_item_GO.id:
                        customers_2_item_GO = customers_2_item.location2
                    else:
                        customers_2_item_GO = customers_2_item.location1
                    # res_val += [customers_2_item_GO.id]
                    # print("customers_2_item  res_val= {}".format(res_val))
                    # before_vals.append(customers_2_item.id)
                    # minute_sum += customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(week_day)
                    # print("customers_2_item  minute_sum= {}".format(minute_sum))
                    # print("customers_2_item.minute , customers_2_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_2_item.minute , customers_2_item_GO.get_customer_day_minute(week_day)))
                    if order_index > 2 and minute_sum + customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(week_day) <= minute:
                        minute_sum += customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(week_day)
                        res_val += [
                            customers_2_item_GO.id,
                        ]
                        # pass
                    elif order_index > 2 and minute_sum + customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(week_day) > minute:
                        continue
                    else:
                        print("order_index else = {}".format(order_index))
                        if minute_sum + customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(week_day) <= minute:
                            minute_sum += customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(week_day)
                            res_val += [
                                customers_2_item_GO.id,
                            ]
                            res_val_i = 0
                            for res_val_item in res_val:
                                if res_val_i > 0:
                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                res_val_i += 1
                            result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                            return_while = True
                            while_bool = False
                            for_bool = False
                            break
                        else:
                            if order_index == 2 and first_dests.last().id == customers_1_item.id:
                                return_while = True
                                while_bool = False
                                break
                            else:
                                continue
                    print("customers_2_item  res_val= {}, = minute_sum= {}".format(res_val,minute_sum))
                    dests_3 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_2_item_GO.id) | Q(location2_id=customers_2_item_GO.id)).order_by('minute')
                    if dests_3.count() == 0:
                        while_bool = False
                        return_while = True
                        print('var dests_3= {}'.format(dests_3.count()))
                        break
                    else:
                        print('yoxdu dests_3= {}'.format(dests_3.count()))
                        pass
                    res_val_2 = copy.deepcopy(res_val)
                    minute_sum_2 = copy.deepcopy(minute_sum)
                    for customers_3_item in dests_3:
                        res_val = copy.deepcopy(res_val_2)
                        minute_sum = copy.deepcopy(minute_sum_2)
                        if return_while:
                            break
                        # before_vals.append(customers_3_item.id)
                        if customers_3_item.location1_id == customers_2_item_GO.id:
                            customers_3_item_GO = customers_3_item.location2
                        else:
                            customers_3_item_GO = customers_3_item.location1
                        # res_val += [customers_3_item_GO.id]
                        # # print("customers_3_item  res_val= {}".format(res_val))
                        # minute_sum += customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(week_day)
                        if order_index > 3 and minute_sum + customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(week_day) <= minute:
                            minute_sum += customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(week_day)
                            res_val += [
                                customers_3_item_GO.id,
                            ]
                            # pass
                        elif order_index > 3 and minute_sum + customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(week_day) > minute:
                            continue
                        else:
                            # print("order_index else = {}".format(order_index))
                            if minute_sum + customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(week_day) <= minute:
                                minute_sum += customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(week_day)
                                res_val += [
                                    customers_3_item_GO.id,
                                ]
                                res_val_i = 0
                                for res_val_item in res_val:
                                    if res_val_i > 0:
                                        result_exc_list.append(copy.deepcopy(res_val_item))
                                    res_val_i += 1
                                result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                return_while = True
                                while_bool = False
                                for_bool = False
                                break
                            else:
                                if order_index == 3 and first_dests.last().id == customers_1_item.id:
                                    return_while = True
                                    while_bool = False
                                    break
                                else:
                                    continue
                        # print("customers_3_item  minute_sum= {}".format(minute_sum))
                        # print("customers_3_item.minute , customers_3_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_3_item.minute , customers_3_item_GO.get_customer_day_minute(week_day)))
                        dests_4 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_3_item_GO.id) | Q(location2_id=customers_3_item_GO.id)).order_by('minute')
                        if dests_4.count() == 0:
                            while_bool = False
                            return_while = True
                            print('var dests_4= {}'.format(dests_4.count()))
                            break
                        else:
                            print('yoxdu dests_4= {}'.format(dests_4.count()))
                            pass
                        res_val_3 = copy.deepcopy(res_val)
                        minute_sum_3 = copy.deepcopy(minute_sum)
                        print("customers_3_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                        for customers_4_item in dests_4:
                            res_val = copy.deepcopy(res_val_3)
                            minute_sum = copy.deepcopy(minute_sum_3)
                            if return_while:
                                break
                            # before_vals.append(customers_4_item.id)
                            if customers_4_item.location1_id == customers_3_item_GO.id:
                                customers_4_item_GO = customers_4_item.location2
                            else:
                                customers_4_item_GO = customers_4_item.location1
                            # res_val += [customers_4_item_GO.id]
                            # # print("customers_4_item  res_val= {}".format(res_val))
                            # minute_sum += customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(week_day)
                            if order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(week_day) <= minute:
                                minute_sum += customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(week_day)
                                res_val += [
                                    customers_4_item_GO.id,
                                ]
                                # pass
                            elif order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(week_day) > minute:
                                continue
                            else:
                                # print("order_index else = {}".format(order_index))
                                if minute_sum + customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(week_day) <= minute:
                                    minute_sum += customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(week_day)
                                    res_val += [
                                        customers_4_item_GO.id,
                                    ]
                                    res_val_i = 0
                                    for res_val_item in res_val:
                                        if res_val_i > 0:
                                            result_exc_list.append(copy.deepcopy(res_val_item))
                                        res_val_i += 1
                                    result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                    return_while = True
                                    while_bool = False
                                    for_bool = False
                                    break
                                else:
                                    if order_index == 4 and first_dests.last().id == customers_1_item.id:
                                        return_while = True
                                        while_bool = False
                                        break
                                    else:
                                        continue
                            # print("customers_4_item  minute_sum= {}".format(minute_sum))
                            # print("customers_4_item.minute , customers_4_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_4_item.minute , customers_4_item_GO.get_customer_day_minute(week_day)))
                            print("customers_4_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                            dests_5 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_4_item_GO.id) | Q(location2_id=customers_4_item_GO.id)).order_by('minute')
                            if dests_5.count() == 0:
                                while_bool = False
                                return_while = True
                                print('var dests_5= {}'.format(dests_5.count()))
                                break
                            else:
                                pass
                                print('yoxdu dests_5= {}'.format(dests_5.count()))
                            res_val_4 = copy.deepcopy(res_val)
                            minute_sum_4 = copy.deepcopy(minute_sum)
                            for customers_5_item in dests_5:
                                res_val = copy.deepcopy(res_val_4)
                                minute_sum = copy.deepcopy(minute_sum_4)
                                if return_while:
                                    break
                                if customers_5_item.location1_id == customers_4_item_GO.id:
                                    customers_5_item_GO = customers_5_item.location2
                                else:
                                    customers_5_item_GO = customers_5_item.location1
                                # res_val += [customers_5_item_GO.id]
                                print("customers_5_item  res_val= {}".format(res_val))
                                # before_vals.append(customers_5_item.id)
                                if order_index > 5 and minute_sum + customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(week_day) <= minute:
                                    minute_sum += customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(week_day)
                                    res_val += [
                                        customers_5_item_GO.id,
                                    ]
                                    # pass
                                elif order_index > 5 and minute_sum + customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(week_day) > minute:
                                    continue
                                else:
                                    print("order_index else = {}".format(order_index))
                                    if minute_sum + customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(week_day) <= minute:
                                        minute_sum += customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(week_day)
                                        res_val += [
                                            customers_5_item_GO.id,
                                        ]
                                        res_val_i = 0
                                        for res_val_item in res_val:
                                            if res_val_i > 0:
                                                result_exc_list.append(copy.deepcopy(res_val_item))
                                            res_val_i += 1
                                        result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                        return_while = True
                                        while_bool = False
                                        for_bool = False
                                        break
                                    else:
                                        if order_index == 5 and first_dests.last().id == customers_1_item.id:
                                            return_while = True
                                            while_bool = False
                                            break
                                        else:
                                            continue
                                # print("customers_5_item  minute_sum= {}".format(minute_sum))
                                # print("customers_5_item.minute , customers_5_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_5_item.minute , customers_5_item_GO.get_customer_day_minute(week_day)))
                                dests_6 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_5_item_GO.id) | Q(location2_id=customers_5_item_GO.id)).order_by('minute')
                                if dests_6.count() == 0:
                                    while_bool = False
                                    return_while = True
                                    print('var dests_6= {}'.format(dests_6.count()))
                                    break
                                else:
                                    pass
                                    print('yoxdu dests_6= {}'.format(dests_6.count()))
                                res_val_5 = copy.deepcopy(res_val)
                                minute_sum_5 = copy.deepcopy(minute_sum)
                                for customers_6_item in dests_6:
                                    # while_bool = False
                                    # return_while = True
                                    # break
                                    res_val = copy.deepcopy(res_val_5)
                                    minute_sum = copy.deepcopy(minute_sum_5)
                                    if return_while:
                                        break
                                    if customers_6_item.location1_id == customers_5_item_GO.id:
                                        customers_6_item_GO = customers_6_item.location2
                                    else:
                                        customers_6_item_GO = customers_6_item.location1
                                    # res_val += [customers_6_item_GO.id]
                                    # print("customers_6_item  res_val= {}".format(res_val))
                                    # # before_vals.append(customers_6_item.id)
                                    # # minute_sum += customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(week_day)
                                    # print("customers_6_item  minute_sum = {}".format(minute_sum))
                                    # print("customers_6_item.minute , customers_6_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_6_item.minute , customers_6_item_GO.get_customer_day_minute(week_day)))
                                    if order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(week_day) <= minute:
                                        minute_sum += customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(week_day)
                                        res_val += [
                                            customers_6_item_GO.id,
                                        ]
                                        # pass
                                    elif order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(week_day) > minute:
                                        print("order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(week_day) > minute")
                                        customers_8_item_i += (copy.deepcopy(dests_6.count()) - 1) * (
                                        copy.deepcopy(dests_6.count()) - 2)
                                        if customers_8_item_i == dests_6.count() * (dests_6.count() - 1) * (dests_6.count() - 2) or order_index == 8 and first_dests.last().id == customers_1_item.id:
                                            print("customers_8_item_i == dests_6.count() * (dests_6.count() - 1) * (dests_6.count() - 2) or order_index == 8 and first_dests.last().id == customers_1_item.id")
                                            return_while = True
                                            while_bool = False
                                            break
                                        continue
                                    else:
                                        print("6 else")
                                        print("order_index else = {}".format(order_index))
                                        if minute_sum + customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(week_day) <= minute:
                                            print("minute_sum + customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(week_day) <= minute")
                                            minute_sum += customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(week_day)
                                            res_val += [
                                                customers_6_item_GO.id,
                                            ]
                                            res_val_i = 0
                                            for res_val_item in res_val:
                                                if res_val_i > 0:
                                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                                res_val_i += 1
                                            result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                            return_while = True
                                            while_bool = False
                                            for_bool = False
                                            break
                                        else:
                                            if order_index == 6 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            else:
                                                continue
                                    dests_7 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_6_item_GO.id) | Q(location2_id=customers_6_item_GO.id)).order_by('minute')
                                    if dests_7.count() == 0:
                                        while_bool = False
                                        return_while = True
                                        break
                                    res_val_6 = copy.deepcopy(res_val)
                                    minute_sum_6 = copy.deepcopy(minute_sum)
                                    # print("customers_6_item  minute_sum = {}".format(minute_sum))
                                    # print("customers_6_item  res_val = {}".format(res_val))
                                    print("customers_6_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                                    for customers_7_item in dests_7:
                                        # while_bool = False
                                        # return_while = True
                                        # break
                                        res_val = copy.deepcopy(res_val_6)
                                        minute_sum = copy.deepcopy(minute_sum_6)
                                        if return_while:
                                            break
                                        if customers_7_item.location1_id == customers_6_item_GO.id:
                                            customers_7_item_GO = customers_7_item.location2
                                        else:
                                            customers_7_item_GO = customers_7_item.location1
                                        # res_val += [
                                        #             customers_7_item_GO.id,
                                        #         ]
                                        # print("customers_7_item  res_val= {}".format(res_val))
                                        # before_vals.append(customers_7_item.id)
                                        # minute_sum += customers_7_item.minute + customers_7_item_GO.get_customer_day_minute(week_day)
                                        if order_index > 7 and minute_sum + customers_7_item.minute + customers_7_item_GO.get_customer_day_minute(week_day) <= minute:
                                            minute_sum += customers_7_item.minute + customers_7_item_GO.get_customer_day_minute(week_day)
                                            res_val += [
                                                customers_7_item_GO.id,
                                            ]
                                            # pass
                                        elif order_index > 7 and minute_sum + customers_7_item.minute + customers_7_item_GO.get_customer_day_minute(week_day) > minute:
                                            customers_8_item_i += copy.deepcopy(dests_7.count()) - 1
                                            customers_9_item_i += (copy.deepcopy(dests_7.count())-1)*(copy.deepcopy(dests_7.count())-2)
                                            if customers_9_item_i == dests_7.count() * (dests_7.count() - 1) * (
                                                dests_7.count() - 2) or order_index == 9 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            if customers_8_item_i == dests_6.count() * (dests_6.count() - 1) * (
                                                dests_6.count() - 2) or order_index == 8 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            continue
                                        else:
                                            print("order_index else = {}".format(order_index))

                                            if minute_sum + customers_7_item.minute + customers_7_item_GO.get_customer_day_minute(week_day) <= minute:
                                                minute_sum += customers_7_item.minute + customers_7_item_GO.get_customer_day_minute(week_day)
                                                res_val += [
                                                    customers_7_item_GO.id,
                                                ]
                                                res_val_i = 0
                                                for res_val_item in res_val:
                                                    if res_val_i > 0:
                                                        result_exc_list.append(copy.deepcopy(res_val_item))
                                                    res_val_i += 1
                                                result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                                return_while = True
                                                while_bool = False
                                                for_bool = False
                                                break
                                            else:
                                                if order_index == 7 and first_dests.last().id == customers_1_item.id:
                                                    return_while = True
                                                    while_bool = False
                                                    break
                                                else:
                                                    continue
                                        # print("customers_7_item update  res_val= {}".format(res_val))
                                        # print("customers_7_item  minute_sum= {}".format(minute_sum))
                                        # print("customers_7_item.minute , customers_7_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_7_item.minute , customers_7_item_GO.get_customer_day_minute(week_day)))
                                        dests_8 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_7_item_GO.id) | Q(location2_id=customers_7_item_GO.id)).order_by('minute')
                                        if dests_8.count() == 0:
                                            while_bool = False
                                            return_while = True
                                            break
                                        res_val_7 = copy.deepcopy(res_val)
                                        minute_sum_7 = copy.deepcopy(minute_sum)
                                        print("customers_7_item  res_val= {}, = minute_sum= {}".format(res_val,
                                                                                                       minute_sum))
                                        for customers_8_item in dests_8:
                                            customers_8_item_i += 1
                                            res_val = copy.deepcopy(res_val_7)
                                            minute_sum = copy.deepcopy(minute_sum_7)
                                            if return_while:
                                                break
                                            if customers_8_item.location1_id == customers_7_item_GO.id:
                                                customers_8_item_GO = customers_8_item.location2
                                            else:
                                                customers_8_item_GO = customers_8_item.location1
                                            # before_vals.append(customers_8_item.id)

                                            if order_index > 8 and minute_sum + customers_8_item.minute + customers_8_item_GO.get_customer_day_minute(week_day) <= minute:
                                                minute_sum += customers_8_item.minute + customers_8_item_GO.get_customer_day_minute(week_day)
                                                res_val += [
                                                            customers_8_item_GO.id,
                                                        ]
                                            elif order_index > 8 and minute_sum + customers_8_item.minute + customers_8_item_GO.get_customer_day_minute(week_day) > minute:
                                                customers_9_item_i += copy.deepcopy(dests_8.count())-1
                                                if customers_9_item_i == dests_7.count() * (dests_7.count() - 1) * (
                                                    dests_7.count() - 2) and order_index == 9 or order_index == 9 and first_dests.last().id == customers_1_item.id:
                                                    return_while = True
                                                    while_bool = False
                                                    break
                                                continue
                                            else:
                                                print("order_index else = {}".format(order_index))
                                                if minute_sum + customers_8_item.minute + customers_8_item_GO.get_customer_day_minute(week_day) <= minute:
                                                    minute_sum += customers_8_item.minute + customers_8_item_GO.get_customer_day_minute(week_day)
                                                    res_val += [
                                                                customers_8_item_GO.id,
                                                            ]
                                                    res_val_i = 0
                                                    for res_val_item in res_val:
                                                        if res_val_i > 0:
                                                            result_exc_list.append(copy.deepcopy(res_val_item))
                                                        res_val_i += 1
                                                    result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                                    return_while = True
                                                    while_bool = False
                                                    for_bool = False
                                                    break
                                                else:
                                                    if order_index == 8 and first_dests.last().id == customers_1_item.id:
                                                        return_while = True
                                                        while_bool = False
                                                        break
                                                    else:
                                                        continue
                                            # print("customers_8_item  minute_sum= {}".format(minute_sum))
                                            # print("customers_8_item  res_val= {}".format(res_val))
                                            # print("customers_8_item.minute , customers_8_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_8_item.minute , customers_8_item_GO.get_customer_day_minute(week_day)))
                                            print("customers_8_item  res_val= {}, = minute_sum= {}".format(res_val,minute_sum))
                                            dests_9 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(Q(location1_id=customers_8_item_GO.id) | Q(location2_id=customers_8_item_GO.id))
                                            if dests_9.count() == 0:
                                                while_bool = False
                                                return_while = True
                                                break
                                            res_val_8 = copy.deepcopy(res_val)
                                            minute_sum_8 = copy.deepcopy(minute_sum)
                                            for customers_9_item in dests_9:
                                                customers_9_item_i += 1
                                                res_val = copy.deepcopy(res_val_8)
                                                minute_sum = copy.deepcopy(minute_sum_8)
                                                if return_while:
                                                    break
                                                if customers_9_item.location1_id == customers_8_item_GO.id:
                                                    customers_9_item_GO = customers_9_item.location2
                                                else:
                                                    customers_9_item_GO = customers_9_item.location1
                                                customers_9_bool = True
                                                if minute_sum + customers_9_item.minute + customers_9_item_GO.get_customer_day_minute(week_day) <= minute:
                                                    minute_sum += customers_9_item.minute + customers_9_item_GO.get_customer_day_minute(week_day)
                                                    res_val += [
                                                                customers_9_item_GO.id
                                                            ]
                                                    res_val_i = 0
                                                    for res_val_item in res_val:
                                                        if res_val_i > 0:
                                                            result_exc_list.append(copy.deepcopy(res_val_item))
                                                        res_val_i += 1
                                                    result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                                    return_while = True
                                                    while_bool = False
                                                    for_bool = False
                                                    print("customers_9_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                                                    # print("customers_9_item  minute_sum= {}".format(minute_sum))
                                                    # print("customers_9_item.minute , customers_9_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_9_item.minute , customers_9_item_GO.get_customer_day_minute(week_day)))
                                                    break
                                                else:
                                                    if customers_9_item_i == dests_7.count() * (dests_7.count()-1) * (dests_7.count()-2) or order_index == 9 and first_dests.last().id == customers_1_item.id:
                                                        return_while = True
                                                        while_bool = False
                                                        break
                                                    else:
                                                        continue
                                                # print("customers_9_item  minute_sum= {}".format(minute_sum))
                                                # print("customers_9_item  result_exc_list= {}".format(result_exc_list))
                                                # print("customers_9_item  result_list= {}".format(result_list))
                                                # print("customers_9_item.minute , customers_9_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_9_item.minute , customers_9_item_GO.get_customer_day_minute(week_day)))

    return result_list


def sub_result1p1_seven(week_day,custom_start_id,exc_list, minute):
    from content.models import Location,LocationDistance
    # from django.forms.models import model_to_dict
    # from work.new_main import calculate_minute_1times as nm_calculate_minute_1times

    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    result_list = []
    result_exc_list = []

        # .order_by('-minute', '-location1__minute','-location2__minute')
    # dest_list = []
    # for loc_destination_item in loc_destinations:
    #     dest_list.append(obj_to_dict_dest(loc_destination_item))
    loc_destinations = LocationDistance.objects.exclude(
        Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).exclude(
        Q(location1__work_times=3) | Q(location2__work_times=3)).order_by('minute   ')
    if custom_start_id == 0:
        main_customer = Location.objects.filter(our_company=True).first()
    else:
        main_customer = Location.objects.filter(id=custom_start_id).first()
    # customers = Location.objects.exclude(id__in=exc_list).exclude(our_company=True)
    while_bool = True
    for_bool = True
    before_vals = []
    customers_11_bool = False
    # res_val = []
    while_bool = True
    return_while = False
    for order_index in range(7, 0, -1):
        if for_bool is False:
            # print('return_while = {}'.format(return_while))
            break
        print('return for')
        # print(while_bool)
        print("<order_index> = <{}>".format(order_index))
        print("<while_bool> = <{}>".format(while_bool))
        print("<return_while> = <{}>".format(return_while))
        while_bool = True
        return_while = False
        print('return for')
        while while_bool:
            print('head yoxdu return_while = {}'.format(return_while))
            # if while_bool is False:
            #     # print('return_while = {}'.format(return_while))
            #     break
            customers_7_item_i = 0
            customers_6_item_i = 0
            customers_5_item_i = 0
            return_while = False
            res_val = [
                main_customer.id,
            ]
            # print("while_bool  res_val= {}".format(res_val))
            first_dests = loc_destinations.exclude(
                Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                Q(location1_id=main_customer.id) | Q(location2_id=main_customer.id)).order_by('minute')

            if first_dests.count() == 0:
                # # print('var first_dests= {}'.format(first_dests.count()))
                break
            else:
                pass
            print('foot yoxdu first_dests = {}'.format(first_dests.count()))
            for customers_1_item in first_dests:
                if return_while:
                    # print('return_while = {}'.format(return_while))
                    break
                # for_break = False
                # if for_break:
                #     continue
                # before_vals.append(customers_1_item.id)
                if customers_1_item.location1_id == main_customer.id:
                    customers_1_item_GO = customers_1_item.location2
                    customers_1_item_ord = 2
                else:
                    customers_1_item_GO = customers_1_item.location1
                    customers_1_item_ord = 1
                # res_val += [customers_1_item_GO.id]
                minute_sum = 0
                # print("customers_1_item.minute , customers_1_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_1_item.minute , customers_1_item_GO.get_customer_day_minute(week_day)))
                if order_index > 1 and minute_sum + customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(
                        week_day) <= minute:
                    print("@@@@@@@@@@@ if 1")
                    minute_sum += customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(week_day)
                    res_val += [
                        customers_1_item_GO.id,
                    ]
                    # pass
                elif order_index > 1 and minute_sum + customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(
                        week_day) > minute:
                    print("@@@@@@@@@@@ elif 1")
                    continue
                else:
                    print("@@@@@@@@@@@ else 1")
                    print("@@@@@@@@@@@ {} - {} - {}".format(order_index,
                                                            minute_sum + customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(
                                                                week_day), minute))
                    # print("order_index else = {}".format(order_index))
                    if minute_sum + customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(
                            week_day) <= minute:
                        # print("@@@@@@@@@@@ if 1")
                        minute_sum += customers_1_item.minute + customers_1_item_GO.get_customer_day_minute(week_day)
                        res_val += [
                            customers_1_item_GO.id,
                        ]
                        # print('+++++++++++++++++++++++++++++++++++++++minute_sum <= minute++++++++++++++++++++++++++++++++++++++++')
                        # print('+++++++++++++++++++++++++++++++++++++++ res_val = {} ++++++++++++++++++++++++++++++++++++++++'.format(res_val))
                        res_val_i = 0
                        for res_val_item in res_val:
                            res_val_i += 1
                            if res_val_i > 0:
                                result_exc_list.append(copy.deepcopy(res_val_item))
                        result_list.append(copy.deepcopy(res_val + [[minute_sum]]))

                        return_while = True
                        while_bool = False
                        for_bool = False
                        # print('+++++++++++++++++++++++++++++++++++++++ return_while = {} ++++++++++++++++++++++++++++++++++++++++'.format(return_while))
                        break
                    else:
                        if order_index == 1 and first_dests.last().id == customers_1_item.id:
                            return_while = True
                            while_bool = False
                            break
                        else:
                            continue
                print("customers_1_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                # print("customers_1_item  minute_sum= {}".format(minute_sum))
                dests_2 = loc_destinations.exclude(
                    Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                    Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                    Q(location1_id=customers_1_item_GO.id) | Q(location2_id=customers_1_item_GO.id)).order_by('minute')
                if dests_2.count() == 0:
                    while_bool = False
                    return_while = True
                    print('var dests_2= {}'.format(dests_2.count()))
                    break
                else:
                    print('yoxdu dests_2 = {}'.format(dests_2.count()))
                    pass
                res_val_1 = copy.deepcopy(res_val)
                minute_sum_1 = copy.deepcopy(minute_sum)
                for customers_2_item in dests_2:
                    res_val = copy.deepcopy(res_val_1)
                    minute_sum = copy.deepcopy(minute_sum_1)
                    if return_while:
                        break

                    if customers_2_item.location1_id == customers_1_item_GO.id:
                        customers_2_item_GO = customers_2_item.location2
                    else:
                        customers_2_item_GO = customers_2_item.location1
                    # res_val += [customers_2_item_GO.id]
                    # print("customers_2_item  res_val= {}".format(res_val))
                    # before_vals.append(customers_2_item.id)
                    # minute_sum += customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(week_day)
                    # print("customers_2_item  minute_sum= {}".format(minute_sum))
                    # print("customers_2_item.minute , customers_2_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_2_item.minute , customers_2_item_GO.get_customer_day_minute(week_day)))
                    if order_index > 2 and minute_sum + customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(
                            week_day) <= minute:
                        minute_sum += customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(week_day)
                        res_val += [
                            customers_2_item_GO.id,
                        ]
                        # pass
                    elif order_index > 2 and minute_sum + customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(
                            week_day) > minute:
                        continue
                    else:
                        print("order_index else = {}".format(order_index))
                        if minute_sum + customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(
                                week_day) <= minute:
                            minute_sum += customers_2_item.minute + customers_2_item_GO.get_customer_day_minute(
                                week_day)
                            res_val += [
                                customers_2_item_GO.id,
                            ]
                            res_val_i = 0
                            for res_val_item in res_val:
                                if res_val_i > 0:
                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                res_val_i += 1
                            result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                            return_while = True
                            while_bool = False
                            for_bool = False
                            break
                        else:
                            if order_index == 2 and first_dests.last().id == customers_1_item.id:
                                return_while = True
                                while_bool = False
                                break
                            else:
                                continue
                    print("customers_2_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                    dests_3 = loc_destinations.exclude(
                        Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                        Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                        Q(location1_id=customers_2_item_GO.id) | Q(location2_id=customers_2_item_GO.id)).order_by(
                        'minute')
                    if dests_3.count() == 0:
                        while_bool = False
                        return_while = True
                        print('var dests_3= {}'.format(dests_3.count()))
                        break
                    else:
                        print('yoxdu dests_3= {}'.format(dests_3.count()))
                        pass
                    res_val_2 = copy.deepcopy(res_val)
                    minute_sum_2 = copy.deepcopy(minute_sum)

                    for customers_3_item in dests_3:
                        res_val = copy.deepcopy(res_val_2)
                        minute_sum = copy.deepcopy(minute_sum_2)
                        if return_while:
                            break
                        if customers_3_item.location1_id == customers_2_item_GO.id:
                            customers_3_item_GO = customers_3_item.location2
                        else:
                            customers_3_item_GO = customers_3_item.location1
                        # res_val += [customers_3_item_GO.id]
                        print("customers_3_item  res_val= {}".format(res_val))
                        # before_vals.append(customers_3_item.id)
                        if order_index > 3 and minute_sum + customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(
                                week_day) <= minute:
                            minute_sum += customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(
                                week_day)
                            res_val += [
                                customers_3_item_GO.id,
                            ]
                            # pass
                        elif order_index > 3 and minute_sum + customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(
                                week_day) > minute:
                            continue
                        else:
                            print("order_index else = {}".format(order_index))
                            if minute_sum + customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(
                                    week_day) <= minute:
                                minute_sum += customers_3_item.minute + customers_3_item_GO.get_customer_day_minute(
                                    week_day)
                                res_val += [
                                    customers_3_item_GO.id,
                                ]
                                res_val_i = 0
                                for res_val_item in res_val:
                                    if res_val_i > 0:
                                        result_exc_list.append(copy.deepcopy(res_val_item))
                                    res_val_i += 1
                                result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                return_while = True
                                while_bool = False
                                for_bool = False
                                break
                            else:
                                if order_index == 3 and first_dests.last().id == customers_1_item.id:
                                    return_while = True
                                    while_bool = False
                                    break
                                else:
                                    continue
                        # print("customers_3_item  minute_sum= {}".format(minute_sum))
                        # print("customers_3_item.minute , customers_3_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_3_item.minute , customers_3_item_GO.get_customer_day_minute(week_day)))
                        dests_4 = loc_destinations.exclude(
                            Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                            Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                            Q(location1_id=customers_3_item_GO.id) | Q(
                                location2_id=customers_3_item_GO.id)).order_by('minute')
                        if dests_4.count() == 0:
                            while_bool = False
                            return_while = True
                            print('var dests_4= {}'.format(dests_4.count()))
                            break
                        else:
                            pass
                            print('yoxdu dests_4= {}'.format(dests_4.count()))
                        res_val_3 = copy.deepcopy(res_val)
                        minute_sum_3 = copy.deepcopy(minute_sum)
                        for customers_4_item in dests_4:
                            # while_bool = False
                            # return_while = True
                            # break
                            res_val = copy.deepcopy(res_val_3)
                            minute_sum = copy.deepcopy(minute_sum_3)
                            if return_while:
                                break
                            if customers_4_item.location1_id == customers_3_item_GO.id:
                                customers_4_item_GO = customers_4_item.location2
                            else:
                                customers_4_item_GO = customers_4_item.location1
                            # res_val += [customers_4_item_GO.id]
                            # print("customers_4_item  res_val= {}".format(res_val))
                            # # before_vals.append(customers_4_item.id)
                            # # minute_sum += customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(week_day)
                            # print("customers_4_item  minute_sum = {}".format(minute_sum))
                            # print("customers_4_item.minute , customers_4_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_4_item.minute , customers_4_item_GO.get_customer_day_minute(week_day)))
                            if order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(
                                    week_day) <= minute:
                                minute_sum += customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(
                                    week_day)
                                res_val += [
                                    customers_4_item_GO.id,
                                ]
                                # pass
                            elif order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(
                                    week_day) > minute:
                                print(
                                    "order_index > 4 and minute_sum + customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(week_day) > minute")
                                customers_6_item_i += (copy.deepcopy(dests_4.count()) - 1) * (
                                    copy.deepcopy(dests_4.count()) - 2)
                                if customers_6_item_i == dests_4.count() * (dests_4.count() - 1) * (
                                            dests_4.count() - 2) or order_index == 6 and first_dests.last().id == customers_1_item.id:
                                    print(
                                        "customers_6_item_i == dests_4.count() * (dests_4.count() - 1) * (dests_4.count() - 2) or order_index == 6 and first_dests.last().id == customers_1_item.id")
                                    return_while = True
                                    while_bool = False
                                    break
                                continue
                            else:
                                print("4 else")
                                print("order_index else = {}".format(order_index))
                                if minute_sum + customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(
                                        week_day) <= minute:
                                    print(
                                        "minute_sum + customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(week_day) <= minute")
                                    minute_sum += customers_4_item.minute + customers_4_item_GO.get_customer_day_minute(
                                        week_day)
                                    res_val += [
                                        customers_4_item_GO.id,
                                    ]
                                    res_val_i = 0
                                    for res_val_item in res_val:
                                        if res_val_i > 0:
                                            result_exc_list.append(copy.deepcopy(res_val_item))
                                        res_val_i += 1
                                    result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                    return_while = True
                                    while_bool = False
                                    for_bool = False
                                    break
                                else:
                                    if order_index == 4 and first_dests.last().id == customers_1_item.id:
                                        return_while = True
                                        while_bool = False
                                        break
                                    else:
                                        continue
                            dests_5 = loc_destinations.exclude(
                                Q(location1_id__in=result_exc_list) | Q(location2_id__in=result_exc_list)).exclude(
                                Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                                Q(location1_id=customers_4_item_GO.id) | Q(
                                    location2_id=customers_4_item_GO.id)).order_by('minute')
                            if dests_5.count() == 0:
                                while_bool = False
                                return_while = True
                                break
                            res_val_4 = copy.deepcopy(res_val)
                            minute_sum_4 = copy.deepcopy(minute_sum)
                            # print("customers_4_item  minute_sum = {}".format(minute_sum))
                            # print("customers_4_item  res_val = {}".format(res_val))
                            print("customers_4_item  res_val= {}, = minute_sum= {}".format(res_val, minute_sum))
                            for customers_5_item in dests_5:
                                # while_bool = False
                                # return_while = True
                                # break
                                res_val = copy.deepcopy(res_val_4)
                                minute_sum = copy.deepcopy(minute_sum_4)
                                if return_while:
                                    break
                                if customers_5_item.location1_id == customers_4_item_GO.id:
                                    customers_5_item_GO = customers_5_item.location2
                                else:
                                    customers_5_item_GO = customers_5_item.location1
                                # res_val += [
                                #             customers_5_item_GO.id,
                                #         ]
                                # print("customers_5_item  res_val= {}".format(res_val))
                                # before_vals.append(customers_5_item.id)
                                # minute_sum += customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(week_day)
                                if order_index > 5 and minute_sum + customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(
                                        week_day) <= minute:
                                    minute_sum += customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(
                                        week_day)
                                    res_val += [
                                        customers_5_item_GO.id,
                                    ]
                                    # pass
                                elif order_index > 5 and minute_sum + customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(
                                        week_day) > minute:
                                    customers_6_item_i += copy.deepcopy(dests_5.count()) - 1
                                    customers_7_item_i += (copy.deepcopy(dests_5.count()) - 1) * (
                                        copy.deepcopy(dests_5.count()) - 2)
                                    if customers_7_item_i == dests_5.count() * (dests_5.count() - 1) * (
                                                dests_5.count() - 2) or order_index == 7 and first_dests.last().id == customers_1_item.id:
                                        return_while = True
                                        while_bool = False
                                        break
                                    if customers_6_item_i == dests_4.count() * (dests_4.count() - 1) * (
                                                dests_4.count() - 2) or order_index == 6 and first_dests.last().id == customers_1_item.id:
                                        return_while = True
                                        while_bool = False
                                        break
                                    continue
                                else:
                                    print("order_index else = {}".format(order_index))

                                    if minute_sum + customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(
                                            week_day) <= minute:
                                        minute_sum += customers_5_item.minute + customers_5_item_GO.get_customer_day_minute(
                                            week_day)
                                        res_val += [
                                            customers_5_item_GO.id,
                                        ]
                                        res_val_i = 0
                                        for res_val_item in res_val:
                                            if res_val_i > 0:
                                                result_exc_list.append(copy.deepcopy(res_val_item))
                                            res_val_i += 1
                                        result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                        return_while = True
                                        while_bool = False
                                        for_bool = False
                                        break
                                    else:
                                        if order_index == 5 and first_dests.last().id == customers_1_item.id:
                                            return_while = True
                                            while_bool = False
                                            break
                                        else:
                                            continue
                                # print("customers_5_item update  res_val= {}".format(res_val))
                                # print("customers_5_item  minute_sum= {}".format(minute_sum))
                                # print("customers_5_item.minute , customers_5_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_5_item.minute , customers_5_item_GO.get_customer_day_minute(week_day)))
                                dests_6 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(
                                    location2_id__in=result_exc_list)).exclude(
                                    Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                                    Q(location1_id=customers_5_item_GO.id) | Q(
                                        location2_id=customers_5_item_GO.id)).order_by('minute')
                                if dests_6.count() == 0:
                                    while_bool = False
                                    return_while = True
                                    break
                                res_val_5 = copy.deepcopy(res_val)
                                minute_sum_5 = copy.deepcopy(minute_sum)
                                print("customers_5_item  res_val= {}, = minute_sum= {}".format(res_val,
                                                                                               minute_sum))
                                for customers_6_item in dests_6:
                                    customers_6_item_i += 1
                                    res_val = copy.deepcopy(res_val_5)
                                    minute_sum = copy.deepcopy(minute_sum_5)
                                    if return_while:
                                        break
                                    if customers_6_item.location1_id == customers_5_item_GO.id:
                                        customers_6_item_GO = customers_6_item.location2
                                    else:
                                        customers_6_item_GO = customers_6_item.location1
                                    # before_vals.append(customers_6_item.id)

                                    if order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(
                                            week_day) <= minute:
                                        minute_sum += customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(
                                            week_day)
                                        res_val += [
                                            customers_6_item_GO.id,
                                        ]
                                    elif order_index > 6 and minute_sum + customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(
                                            week_day) > minute:
                                        customers_7_item_i += copy.deepcopy(dests_6.count()) - 1
                                        if customers_7_item_i == dests_5.count() * (dests_5.count() - 1) * (
                                                    dests_5.count() - 2) and order_index == 7 or order_index == 7 and first_dests.last().id == customers_1_item.id:
                                            return_while = True
                                            while_bool = False
                                            break
                                        continue
                                    else:
                                        print("order_index else = {}".format(order_index))
                                        if minute_sum + customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(
                                                week_day) <= minute:
                                            minute_sum += customers_6_item.minute + customers_6_item_GO.get_customer_day_minute(
                                                week_day)
                                            res_val += [
                                                customers_6_item_GO.id,
                                            ]
                                            res_val_i = 0
                                            for res_val_item in res_val:
                                                if res_val_i > 0:
                                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                                res_val_i += 1
                                            result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                            return_while = True
                                            while_bool = False
                                            for_bool = False
                                            break
                                        else:
                                            if order_index == 6 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            else:
                                                continue
                                    # print("customers_6_item  minute_sum= {}".format(minute_sum))
                                    # print("customers_6_item  res_val= {}".format(res_val))
                                    # print("customers_6_item.minute , customers_6_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_6_item.minute , customers_6_item_GO.get_customer_day_minute(week_day)))
                                    print("customers_6_item  res_val= {}, = minute_sum= {}".format(res_val,
                                                                                                   minute_sum))
                                    dests_7 = loc_destinations.exclude(Q(location1_id__in=result_exc_list) | Q(
                                        location2_id__in=result_exc_list)).exclude(
                                        Q(location1_id__in=res_val[:-1]) | Q(location2_id__in=res_val[:-1])).filter(
                                        Q(location1_id=customers_6_item_GO.id) | Q(
                                            location2_id=customers_6_item_GO.id))
                                    if dests_7.count() == 0:
                                        while_bool = False
                                        return_while = True
                                        break
                                    res_val_6 = copy.deepcopy(res_val)
                                    minute_sum_6 = copy.deepcopy(minute_sum)
                                    for customers_7_item in dests_7:
                                        customers_7_item_i += 1
                                        res_val = copy.deepcopy(res_val_6)
                                        minute_sum = copy.deepcopy(minute_sum_6)
                                        if return_while:
                                            break
                                        if customers_7_item.location1_id == customers_6_item_GO.id:
                                            customers_7_item_GO = customers_7_item.location2
                                        else:
                                            customers_7_item_GO = customers_7_item.location1
                                        customers_7_bool = True
                                        if minute_sum + customers_7_item.minute + customers_7_item_GO.get_customer_day_minute(
                                                week_day) <= minute:
                                            minute_sum += customers_7_item.minute + customers_7_item_GO.get_customer_day_minute(
                                                week_day)
                                            res_val += [
                                                customers_7_item_GO.id
                                            ]
                                            res_val_i = 0
                                            for res_val_item in res_val:
                                                if res_val_i > 0:
                                                    result_exc_list.append(copy.deepcopy(res_val_item))
                                                res_val_i += 1
                                            result_list.append(copy.deepcopy(res_val + [[minute_sum]]))
                                            return_while = True
                                            while_bool = False
                                            for_bool = False
                                            print("customers_7_item  res_val= {}, = minute_sum= {}".format(res_val,
                                                                                                           minute_sum))
                                            # print("customers_7_item  minute_sum= {}".format(minute_sum))
                                            # print("customers_7_item.minute , customers_7_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_7_item.minute , customers_7_item_GO.get_customer_day_minute(week_day)))
                                            break
                                        else:
                                            if customers_7_item_i == dests_5.count() * (dests_5.count() - 1) * (
                                                        dests_5.count() - 2) or order_index == 7 and first_dests.last().id == customers_1_item.id:
                                                return_while = True
                                                while_bool = False
                                                break
                                            else:
                                                continue
                                                # print("customers_7_item  minute_sum= {}".format(minute_sum))
                                                # print("customers_7_item  result_exc_list= {}".format(result_exc_list))
                                                # print("customers_7_item  result_list= {}".format(result_list))
                                                # print("customers_7_item.minute , customers_7_item_GO.get_customer_day_minute(week_day)= {}  ,   {}".format(customers_7_item.minute , customers_7_item_GO.get_customer_day_minute(week_day)))

    return result_list

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
