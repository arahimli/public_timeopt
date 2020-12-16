import json

from django.core import serializers
from django.db.models import Q
from timeopt import settings
from django.http import HttpResponseRedirect, Http404, HttpResponse

# from content.models import Location,LocationDistance
from django.db.models.fields.related import ManyToManyField
from django.db.models.fields.related import ForeignKey

# from django_pandas.io import read_frame

def chunkify(lst,n):
  return [lst[i::n] for i in range(0,n)]

def main_work_list(exc_list,minute):
    from content.models import LocationDistance
    from django.forms.models import model_to_dict
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).order_by('minute')
    # dest_list = []
    # df = read_frame(loc_destinations)
    # for loc_destination_item in loc_destinations:
    #     dest_list.append(obj_to_dict_dest(loc_destination_item))
    dest_list = LocationDistance.objects.exclude(Q(location1_id__in=[]) | Q(location2_id__in=[])).values('location1','location1__minute','location2','location2__minute','minute')
    # week_dtf = pd.DataFrame.from_records(loc_destinations)


    all_list = result(exc_list=exc_list,minute=minute,dest_list=dest_list)
    get_max_len_list_with_minute_val = get_max_len_list_with_minute(list=all_list,minute=minute,dest_list=dest_list)
    print("get_max_len_list_with_minute_val = {}".format(get_max_len_list_with_minute_val))
    return get_max_len_list_with_minute_val



def get_max_len_list_with_minute(list,minute,dest_list):
    return_list = list[0]
    min_minute = calculate_minute(list[0],minute,dest_list)
    get_list_max_len_val = get_list_max_len(list)
    for list_item in list:
        minute = calculate_minute(list_item,minute,dest_list)
        if get_list_max_len_val <= len(list_item):
            if minute<min_minute:
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



def result(exc_list,minute,dest_list):
    from content.models import Location
    from django.forms.models import model_to_dict
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')

    # print(dest_list)
    # return dest_list

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
        # result_list_max_len = get_list_max_len(result_list)
        # result_list = get_max_len_list(result_list)
        for result_item in result_list:
            # print('result_item[:-1] = {}'.format(result_item[:-1]))
            # print('result_item[:-2] = {}'.format(result_item[:-2]))
            calculate_minute_val = calculate_minute(result_item, minute, dest_list)
            # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            # print("calculate_minute_val = {}".format(calculate_minute_val))
            # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            if calculate_minute_val>0:
                opt_destination_fun =  opt_destination(result_item[-1], result_item[:-1], calculate_minute_val,dest_list)
                try:
                    my_locs = opt_destination_fun[1]
                    # print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
                    # print(opt_destination_fun)
                    # print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")

                    if len(my_locs)>=0:
                        for x in list(my_locs):
                            result_t = result_item+[x[0]]
                            result_list_def.append(result_t)
                except:
                    pass
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



def calculate_minute(loc_list,minute_all,dest_list_q):
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list))
    i=0
    minute=0
    for loc_list_item in loc_list:
        # print('dhsjdshdjshdj')
        if i > 0:
            j=0
            # print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii={}".format(1))
            print(len(dest_list_q))
            dest_list_q_l = dest_list_q.filter(Q(location1_id=loc_list[i],location2_id=loc_list[i-1]) | Q(location1_id=loc_list[i-1],location2_id=loc_list[i])).first()
            # print(dest_list_q_l)
            # dest_list = read_frame(dest_list_q).sort_values(['minute'], ascending=[False])
            # for dest_list_item in dest_list:
                # if j<=0:
                    # print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj={}".format(j))
                # print("dest_list_item['location1'] = {} --  loc_list[i-1] = {} --  dest_list_item['location2'] = {} --  loc_list[i] = {} --  ".format(dest_list_item['location1'],loc_list[i-1],dest_list_item['location2'],loc_list[i]))
                # if (dest_list_item['location1']  == loc_list[i] and dest_list_item['location2'] == loc_list[i-1]) or (dest_list_item['location1']  == loc_list[i-1] and dest_list_item['location2'] == loc_list[i]):
                    # loc_destination = LocationDistance.objects.filter(Q(location1_id=loc_list[i],location2_id=loc_list[i-1]) | Q(location1_id=loc_list[i-1],location2_id=loc_list[i])).first()
            main_location = None
            if loc_list[i] == dest_list_q_l.location1:
                main_location = dest_list_q_l.location1
            else:
                main_location = dest_list_q_l.location2
            minute += dest_list_q_l.minute + main_location.minute
                    # print("hahahahahahahhahahahahahahahahahahahahahhahahahahahahahahaahahhahaahhahaahahahahhahahahahahaahahh")
                    # print(minute)
                    # print("hahahahahahahhahahahahahahahahahahahahahhahahahahahahahahaahahhahaahhahaahahahahhahahahahahaahahh")
                # j+=1
        i+=1
    minute_all-=minute
    # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    # print("calculate_minute_val = {}".format(minute_all))
    # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return minute_all



def opt_destination(current_loc_id,exc_list, minute,dest_list):
    from content.models import Location
    from content.models import LocationDistance
    inc_list = []
    exc_list = list(exc_list)
    minute_last = minute
    # print("------------------------------------------------------------------------------------------------------------")
    # print(exc_list)
    # print("------------------------------------------------------------------------------------------------------------")
    # dest_list_all = []
    # for dest_list_item in dest_list:
    #     if not (dest_list_item['location2']  in exc_list or dest_list_item['location2'] in exc_list) and (dest_list_item['location2']  == current_loc_id or dest_list_item['location2'] == current_loc_id):
    #         pass
    # dest_list = dict((key,value) for key, value in a.items() if key == 1)
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    # loc_destinations = LocationDistance.objects.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id)).order_by('minute')
    # print(loc_destinations.count())
    # print(minute)

    result_val = []
    # return len(loc_destinations)
    if minute > 0:
        # print(inc_list)
        # print(exc_list)
        # loc_destinations = loc_destinations.filter(location1=current_loc_id)
        # for loc_destination in loc_destinations:
        i=0
        j=0
        dest_list = dest_list.exclude(Q(location1_id__in=exc_list) | Q(location2_id__in=exc_list)).filter(Q(location1_id=current_loc_id) | Q(location2_id=current_loc_id))
        for dest_list_item in dest_list:
            # print("dest_list_item['location1'] = {} -------  dest_list_item['location2'] = {}  -- ----------------- exc_list = {}".format(dest_list_item['location1'],dest_list_item['location2'],exc_list))
            if not (dest_list_item['location1'] in exc_list or dest_list_item['location2'] in exc_list):
                if dest_list_item['location1']  == current_loc_id or dest_list_item['location1'] == current_loc_id:
                    main_location = None
                    go_location = None
                    # print(current_loc_id)
                    # print(loc_destination.location1_id)
                    # print(loc_destination.location2_id)
                    if current_loc_id == dest_list_item['location1']:
                        main_location = dest_list_item['location1_obj']
                        go_location = dest_list_item['location2_obj']
                    elif current_loc_id == dest_list_item['location2']:
                        main_location = dest_list_item['location2_obj']
                        go_location = dest_list_item['location1_obj']
                    # else:
                    #     break
                    minute = minute_last - (dest_list_item['minute'] + go_location['minute'])
                    # print(minute)
                    if minute>0:
                        inc_list.append([go_location['pk'],minute])
                        j+=1
                    else:
                        pass
            i+=1
        # result_val.append([current_loc_id, inc_list])
        result_val.append(current_loc_id)
        result_val.append(inc_list)
        # exc_list.append(current_loc_id)
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        # print("i={}   ---   j={}".format(i,j))
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    return result_val
    # return result_val


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

def week_dtf_(week_dtf):
    return week_dtf



def distance_2_point(location1_lat,location1_lon,location2_lat,location2_lon):
    import googlemaps
    from datetime import datetime
    # gmaps = googlemaps.Client(key=settings.GEOPOSITION_GOOGLE_MAPS_API_KEY)
    gmaps = googlemaps.Client(key='AIzaSyCZzOkIyEloBqx-8MSfZZxMp3rVKCtfc3k')

    # Geocoding and address
    geocode_distance = gmaps.distance_matrix((location1_lat,location1_lon),(location2_lat,location2_lon),mode="driving")
    geocode_distance_es = geocode_distance['rows'][0]['elements'][0]
    return [int(round(geocode_distance_es['duration']['value']/60)),geocode_distance_es['distance']['value']]