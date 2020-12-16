import json

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, get_user_model

from django.contrib.auth.views import logout
# Create your views here.
from django.urls import reverse
from django.utils import timezone
from django.utils.datetime_safe import datetime

from userprofile.forms import *
from django.utils.translation import ugettext as _

from userprofile.models import Profile
from content.models import *
from content.tasks import main_result_prepare_plan, main_result_prepare_plan_new, add_location_from_excel_list,main_result_prepare_plan_new_plan
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from flynsarmy_paginator.paginator import FlynsarmyPaginator
from django.template.loader import render_to_string

GUser = get_user_model()

def base(req=None):
    company_information = CompanyInformation.objects.filter(active=True).order_by('-date').first()
    settings_obj = Settings.objects.filter().order_by('-date').first()
    data = {
        'now':datetime.now(),
        'base_company_information':company_information,
        'base_settings_obj':settings_obj,
    }
    return data

def base_auth(req=None):
    user = req.user
    profile = get_object_or_404(Profile, user=user)
    company_information = CompanyInformation.objects.filter(active=True).order_by('-date').first()
    settings_obj = Settings.objects.filter().order_by('-date').first()
    data = {
        'now':datetime.now(),
        'base_profile':profile,
        'base_plan_log':PlanLog.objects.filter(complated=False,rejcected=False),
        'base_company_information':company_information,
        'base_settings_obj':settings_obj,
    }
    return data



@login_required(login_url='userprofile:sign_in')
def dashboard(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    # tourpackeges = None
    now = timezone.now()
    context = base_auth(req=request)
    employees = Employee.objects.all()
    customers = Location.objects.filter(our_company=False)
    if profile.type == 'admin-person':
        pass
    elif profile.type == 'employee-person':
        pass
    else:
        raise Http404
    # return HttpResponse(customers[:20].count())
    context['employee_count'] = employees.count()
    context['customer_count'] = customers.count()
    context['last_customers'] = customers.all()[:20]
    context['last_employees'] = employees.all()[:20]
    # context['tours'] = Tour.objects.filter(active=True)
    return render(request, 'userprofile/dashboard.html', context=context)




@login_required(login_url='userprofile:sign_in')
def customer_upload_from_excel(request):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    context['message_code'] = 0
    if profile.type == 'admin-person':
        pass
    else:
        raise Http404
    if request.method == 'POST':
        form = ExcelDocumentForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            clean_data = form.cleaned_data
            excelfile = clean_data.get('excelfile')
            extension = os.path.splitext(excelfile.name)[1]
            if not (extension in IMPORT_FILE_TYPES):
                context['message_code'] = 2
                context['message'] = _("Please choose Excel File")
                return render(request, 'userprofile/admin/add-customer-excel.html', context=context)
                # raise forms.ValidationError(
                #     _("This file is not a valid Excel file. Please make sure your input file is an Excel file )"))
            # pass
            excel_document_new = ExcelDocument(excelfile=excelfile)
            excel_document_new.save()
            # return HttpResponse(excelfile)
            context['message_code'] = 1
            # print("excel_document_new.excelfile.url={}".format(excel_document_new.excelfile.url))
            # print("excel_document_new.excelfile={}".format(excel_document_new.excelfile))
            add_location_from_excel_list.delay(excel_document_new.excelfile.url)
            context['message'] = _("Uploaded successfuly")

        else:
            context['message_code'] = 2
            context['message'] = _("Please choose Excel File")
            # return HttpResponse(form.errors)
            # newdoc = ExcelDocumentForm(excelfile = request.FILES['excelfile'])
            # newdoc.save()

            # return HttpResponseRedirect(reverse('credit.views.list'))
    else:
        form = ExcelDocumentForm()
    context['form'] = form
    return render(request, 'userprofile/admin/add-customer-excel.html', context=context)





@login_required(login_url='userprofile:sign_in')
def all_plans(request):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person':
        pass
    else:
        raise Http404
    return render(request, 'userprofile/admin/all_plans.html', context=context)

@login_required(login_url='userprofile:sign_in')
def my_plans(request):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    context['employee'] = get_object_or_404(Employee,profile=profile)
    context['week_list'] = [1,2,3]

    if profile.type == 'employee-person':
        pass
    else:
        raise Http404
    return render(request, 'userprofile/employee/plans.html', context=context)


@login_required(login_url='userprofile:sign_in')
def plan_prepare(request):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person':
        pass
    else:
        raise Http404
    return render(request, 'userprofile/admin/plan_prepare.html', context=context)


@login_required(login_url='userprofile:sign_in')
def admin_all_employees_plans(request):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person':
        employee_list = Employee.objects.all()
        # company_product_or_service_list = CompanyProductOrService.objects.filter(deleted=False)
        # .filter(start_date__gte=now).filter(end_date__lte=now)[:18]
        # contact_list = Contacts.objects.all()
        paginator = FlynsarmyPaginator(employee_list, 30, adjacent_pages=3)  # Show 25 contacts per page

        page = request.GET.get('page')  # page check is tam eded
        try:
            employees = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            employees = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            employees = paginator.page(paginator.num_pages)
        context['employees'] =  employees
        context['page'] =  page
    else:
        raise Http404
    return render(request, 'userprofile/admin/all_employees.html', context=context)


@login_required(login_url='userprofile:sign_in')
def admin_employee_plans(request,e_id):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    if profile.type == 'admin-person':
        context['employee'] = get_object_or_404(Employee,id=e_id)
        context['week_list'] = [1,2,3]
    else:
        raise Http404
    return render(request, 'userprofile/admin/employee_plans.html', context=context)




@login_required(login_url='userprofile:sign_in')
def admin_all_customers(request):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person':
        customer_list = Location.objects.all()
        # company_product_or_service_list = CompanyProductOrService.objects.filter(deleted=False)
        # .filter(start_date__gte=now).filter(end_date__lte=now)[:18]
        # contact_list = Contacts.objects.all()
        paginator = FlynsarmyPaginator(customer_list, 30, adjacent_pages=3)  # Show 25 contacts per page

        page = request.GET.get('page')  # page check is tam eded
        try:
            customers = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            customers = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            customers = paginator.page(paginator.num_pages)
        context['customers'] = customers
        context['page'] =  page
    else:
        raise Http404
    return render(request, 'userprofile/admin/all_customers.html', context=context)





@login_required(login_url='userprofile:sign_in')
def plan_prepare_ajax(request, op_slug, sub_main_result_prepare_plan_new_plan=None):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person':
        if request.method == 'GET' and request.is_ajax():
            message_code = 0
            message = ""
            plan_obj = PlanLog.objects
            settings_obj = Settings.objects
            if plan_obj.filter(complated=False,rejcected=False):
                message = _("Please wait preparing plans........")
            else:
                if op_slug == 'main':
                    if settings_obj.filter(main_plan=True):
                        message_code = 1
                        main_result_prepare_plan_new_plan.delay()
                        message = _("Started plan preparing. Please wait........")
                    else:
                        message = _("Main plan is disable ........")
                if op_slug == 'sub-main':
                    if settings_obj.filter(sub_plan=True):
                        message_code = 1
                        sub_main_result_prepare_plan_new_plan.delay()
                        message = _("Started plan preparing. Please wait........")
                        settings_obj_f = settings_obj.first()
                        settings_obj_f.sub_plan = False
                        print("sub_plan = {}".format(settings_obj_f.sub_plan))
                        settings_obj_f.save()
                    else:
                        message = _("SubMain plan is disable ........")
            data = {'message_code': message_code, 'message': message}
            # data = {'message_code': message_code, 'message': message}
            return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")
        else:
            raise Http404
    else:
        raise Http404




@login_required(login_url='userprofile:sign_in')
def employee_plan_show_ajax(request):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    employee = get_object_or_404(Employee, profile=profile)
    if profile.type == 'employee-person':
        if request.method == 'GET' and request.is_ajax():
            message_code = 0
            _html = ""
            week_list = [1, 2, 3, 4]
            employee_work_day_i = 0
            for employee_work_day in employee.get_employee_work_days():
                employee_work_day_i += 1
                week_list_i = 0
                _html = '{0}{1}'.format(_html, '<div class="row ">')
                for week_item in week_list:
                    _button = ""
                    week_list_i += 1
                    employee_get_plans_w_d_location_list = []
                    # print("employee_get_plans_w_d_location_list={}".format(employee_get_plans_w_d_location_list))
                    _html = '{0}{1}'.format(_html,
                                            render_to_string('userprofile/include/_week_part.html',
                                                             {
                                                                 'week_item': week_item,
                                                                 'employee_work_day': employee_work_day,
                                                             }))
                    employee_get_plans_w_d = employee_work_day.get_plans_w_d(week_item, employee_work_day.day.id)
                    loc_oreders = LocationOrder.objects.filter(plan_employee_work=employee_get_plans_w_d).order_by(
                        'order_index')
                    employee_get_plans_w_d_location_i = 0
                    for employee_get_plans_w_d_location in loc_oreders:
                        employee_get_plans_w_d_location_list.append(employee_get_plans_w_d_location.location_id)
                        employee_get_plans_w_d_location_i += 1
                        _html = '{0}{1}'.format(_html,
                                                render_to_string('userprofile/include/_employee_plans.html',
                                                                 {
                                                                     'employee_work_day_i': employee_work_day_i,
                                                                     'profile_type': profile.type,
                                                                     'week_list_i': week_list_i,
                                                                     'employee_get_plans_w_d_location_i': employee_get_plans_w_d_location_i,
                                                                     'employee_get_plans_w_d': employee_get_plans_w_d,
                                                                     'employee_get_plans_w_d_get_location': employee_get_plans_w_d_location,
                                                                 }))
                    if employee_get_plans_w_d_location_i > 0:
                        _button = '{0}'.format(render_to_string('userprofile/include/_employee_plans_button.html',
                                                                {
                                                                    'employee_get_plans_w_d_location_list': employee_get_plans_w_d_location_list,
                                                                    # 'employee_get_plans_w_d_location_i': employee_get_plans_w_d_location_i,
                                                                }))
                    # _html = '{0}{1}{2}'.format(_html, _button, '</ul></div>')
                    employee_get_plans_w_d_location_list = []
                    _html = '{0}{1}{2}'.format( _html,_button, '</ul></div>')
                message_code = 1
                _html = '{0}{1}'.format(_html, '</div>')
            data = {'message_code': message_code, '_html': _html}
            # data = {'message_code': message_code, '_html': _html}
            return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")
        else:
            raise Http404
    else:
        raise Http404



@login_required(login_url='userprofile:sign_in')
def admin_employee_plan_show_ajax(request,e_id):
    context = base_auth(req=request)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person':
        employee = get_object_or_404(Employee, id=e_id)
        if request.method == 'GET' and request.is_ajax():
            message_code = 0
            _html = ""
            week_list = [1, 2, 3, 4]
            employee_work_day_i = 0
            for employee_work_day in employee.get_employee_work_days():
                # employee_get_plans_w_d_location_list = []
                employee_work_day_i+=1
                week_list_i = 0
                _html = '{0}{1}'.format(_html,'<div class="row ">')
                for week_item in week_list:
                    _button = ""
                    week_list_i += 1
                    employee_get_plans_w_d_location_list = []
                    # print("employee_get_plans_w_d_location_list={}".format(employee_get_plans_w_d_location_list))
                    _html = '{0}{1}'.format(_html,
                                              render_to_string('userprofile/include/_week_part.html',
                                                                        {
                                                                            'week_item': week_item,
                                                                            'employee_work_day': employee_work_day,
                                                                        }))
                    employee_get_plans_w_d = employee_work_day.get_plans_w_d(week_item,employee_work_day.day.id)
                    loc_oreders = LocationOrder.objects.filter(plan_employee_work=employee_get_plans_w_d).order_by('order_index')
                    employee_get_plans_w_d_location_i = 0
                    for employee_get_plans_w_d_location in loc_oreders:
                        employee_get_plans_w_d_location_list.append(employee_get_plans_w_d_location.location_id)
                        employee_get_plans_w_d_location_i +=1
                        _html = '{0}{1}'.format(_html,
                                                  render_to_string('userprofile/include/_employee_plans.html',
                                                                            {
                                                                                'employee_work_day_i': employee_work_day_i,
                                                                                'profile_type': profile.type,
                                                                                'week_list_i': week_list_i,
                                                                                'employee_get_plans_w_d_location_i': employee_get_plans_w_d_location_i,
                                                                                'employee_get_plans_w_d': employee_get_plans_w_d,
                                                                                'employee_get_plans_w_d_get_location': employee_get_plans_w_d_location,
                                                                            }))
                    if employee_get_plans_w_d_location_i > 0:
                        _button = '{0}'.format(render_to_string('userprofile/include/_employee_plans_button.html',
                                                                        {
                                                                            'employee_get_plans_w_d_location_list': employee_get_plans_w_d_location_list,
                                                                            # 'employee_get_plans_w_d_location_i': employee_get_plans_w_d_location_i,
                                                                        }))
                    # _html = '{0}{1}'.format( _html, '</ul></div>')
                    employee_get_plans_w_d_location_list = []
                    _html = '{0}{1}{2}'.format( _html,_button, '</ul></div>')
                message_code = 1
                _html = '{0}{1}'.format(_html, '</div>')
            data = {'message_code': message_code, '_html': _html}
            # data = {'message_code': message_code, '_html': _html}
            return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")
        else:
            raise Http404
    else:
        raise Http404







@login_required(login_url='userprofile:sign_in')
def admin_employee_plan_show_map_ajax(request):
    # context = base_auth(req=request)
    user = request.user
    # print("salam")
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person' or profile.type == 'employee-person' :
        # print("admin")
        if request.method == 'GET' and request.is_ajax():
            # print("get ajax")
            message_code = 0
            _html = ""
            message_code = 1
            main_location = Location.objects.filter(our_company=True).first()
            location_list = request.GET.getlist('location_list')
            map_data = []
            locations = Location.objects.filter(id__in=location_list)
            location_list_i = 0
            for location_list_item in location_list:
                location_list_i +=1
                locations_item = locations.filter(id=location_list_item).first()
                map_data.append([locations_item.address])
            # # print("locations_item.address={}".format(locations_item.address))
            map_data.insert(0,[main_location.address])
            # print("locations={}".format(locations.count()))
            # print("map_data={}".format(map_data))

            _html = '{0}'.format(render_to_string('userprofile/include/_direction_map.html',
                                                    {
                                                        'map_data': map_data,
                                                        # 'employee_get_plans_w_d_location_i': employee_get_plans_w_d_location_i,
                                                    }))
            data = {'message_code': message_code, '_html': _html}
            # data = {'message_code': message_code, '_html': _html}
            return JsonResponse(data)







@login_required(login_url='userprofile:sign_in')
def admin_employee_plan_form_generate_ajax(request):
    # context = base_auth(req=request)
    user = request.user
    # print("salam")
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person':
        # print("admin")
        if request.method == 'GET' and request.is_ajax():
            # print("get ajax")
            message_code = 0
            _html = ""
            _html_employees_select = "<option value="">{}</option>".format(_("Select Employee"))
            _html_employees_work_day_select = "<option value="">{}</option>".format(_("Select Work Day"))
            message_code = 1
            employee_plan_id = request.GET.get('employee_plan_id')
            l_id = request.GET.get('l_id')
            map_data = []
            employee_plan = PlanEmployeeWork.objects.filter(id=employee_plan_id).first()
            if employee_plan:
                location = employee_plan.get_location(l_id)
                employees = Employee.objects.filter(status=True)
                work_days = WorkDay.objects.all().order_by('day')
                for employee_item in employees:
                    _html_employees_select = '{0}{1}'.format(_html_employees_select,'<option value="{}">{} {}</option>'.format(employee_item.id,employee_item.first_name,employee_item.last_name))
                for work_days_item in work_days:
                    _html_employees_work_day_select = '{0}{1}'.format(_html_employees_work_day_select,'<option value="{}">{}</option>'.format(work_days_item.id,work_days_item.get_day_name()))
                # print("locations={}".format(locations.count()))
                # print("map_data={}".format(map_data))

            data = {'message_code': message_code, '_html_employees_select': _html_employees_select, '_html_employees_work_day_select': _html_employees_work_day_select}
            # data = {'message_code': message_code, '_html': _html}
            return JsonResponse(data)
            # return Jso(json.dumps(data, ensure_ascii=False), content_type="application/json")






@login_required(login_url='userprofile:sign_in')
def admin_employee_plan_form_location_ajax(request,e_p_id,l_id):
    # context = base_auth(req=request)
    user = request.user
    # print("salam")
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person':
        # print("admin")
        if request.method == 'GET' and request.is_ajax():
            # print("get ajax")
            message_code = 0
            _html = ""
            _html_customers_select_first = '<option value="">{}</option>'.format(_("Select Customer"))
            _html_customers_select = '<option value="">{}</option>'.format(_("Select Customer"))
            try:
                message_code = 1
                employees_select_id = request.GET.get('employees_select_id')
                employees_work_day_id = request.GET.get('employees_work_day_id')
                map_data = []
                c_employee_plan = PlanEmployeeWork.objects.filter(id=e_p_id).first()
                c_location = Location.objects.filter(id=l_id).first()
                if c_employee_plan and c_location:
                    ch_employee_plan = PlanEmployeeWork.objects.filter(employee_id=employees_select_id,week=c_employee_plan.week,day_id=employees_work_day_id).first()
                    if ch_employee_plan:
                        location_orders = ch_employee_plan.get_locations()
                        # employees = Employee.objects.filter(status=True)
                        # work_days = WorkDay.objects.all().order_by('day')
                        for location_orders_item in location_orders:
                            _html_customers_select = '{0}{1}'.format(_html_customers_select,'<option value="{}">{}</option>'.format(location_orders_item.id,location_orders_item.location.name))
            except:
                message_code = 1
                # pass
            if _html_customers_select == _html_customers_select_first:
                _html_customers_select = ''
            data = {'message_code': message_code, '_html_customers_select': _html_customers_select}
            # data = {'message_code': message_code, '_html': _html}
            return JsonResponse(data)



@login_required(login_url='userprofile:sign_in')
def admin_employee_plan_form_change_location_position_ajax(request,cur_loc_ord_id):
    # context = base_auth(req=request)
    user = request.user
    # print("salam")
    profile = get_object_or_404(Profile, user=user)
    if profile.type == 'admin-person':
        # print("admin")
        if request.method == 'GET' and request.is_ajax():
            # print("get ajax")
            message_code = 0
            _html = ""
            # _html_customers_select = '<option value="">{}</option>'.format(_("Select Customer"))
            try:
                message_code = 1
                employees_select_id = request.GET.get('employees_select_id')
                employees_work_day_id = request.GET.get('employees_work_day_id')
                chng_loc_ord_id = request.GET.get('chng_loc_ord_id')
                map_data = []
                chng_loc_ord_obj = LocationOrder.objects.filter(id=chng_loc_ord_id).first()
                cur_loc_ord_obj = LocationOrder.objects.filter(id=cur_loc_ord_id).first()
                # print('cur_loc_ord_obj.location_id = {} ,chng_loc_ord_obj.location_id  = {}'.format(cur_loc_ord_obj.location_id ,chng_loc_ord_obj.location_id ))
                cur_loc_ord_obj_loc_id =  cur_loc_ord_obj.location_id
                chng_loc_ord_obj_id =  chng_loc_ord_obj.location_id
                cur_loc_ord_obj.location_id ,chng_loc_ord_obj.location_id = chng_loc_ord_obj_id , cur_loc_ord_obj_loc_id
                # print('cur_loc_ord_obj.location_id = {} ,chng_loc_ord_obj.location_id  = {}'.format(cur_loc_ord_obj.location_id ,chng_loc_ord_obj.location_id ))
                cur_loc_ord_obj.save()
                chng_loc_ord_obj.save()
            except:
                message_code = 0
                # pass
            data = {'message_code': message_code, '_html_customers_select': _html}
            # data = {'message_code': message_code, '_html': _html}
            return JsonResponse(data)
            # return Jso(json.dumps(data, ensure_ascii=False), content_type="application/json")



@login_required(login_url='userprofile:sign_in')
def log_out(request):
    if request.user.is_authenticated():
        logout(request)
    next_url = request.GET.get('next_url')
    if next_url:
        pass
    else:
        next_url = reverse('userprofile:sign_in')
    return HttpResponseRedirect(next_url)

def sign_in(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('userprofile:dashboard'))
    login_form = LoginForm(request.POST or None, request.FILES or None)
    next_url = request.GET.get('next_url')
    context = base(req=request)
    context['login_form'] = login_form
    context['next_url'] = next_url
    # return HttpResponse(next_url)
    if request.method == 'POST':
        if login_form.is_valid():
            clean_data = login_form.cleaned_data
            username = clean_data.get('username_or_email')
            password = clean_data.get('password')
            remember_me = clean_data.get('remember_me')

            # if remember_me:
            #     remember_me = True
            # else:
            #     remember_me = False

            if '@' in username:
                try:
                    user_email = GUser.objects.get(email=username)
                    user = auth.authenticate(username=user_email.username,
                                             password=password)
                except:
                    user = auth.authenticate(username=username,
                                             password=password)
            else:
                user = auth.authenticate(username=username,
                                         password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    # return HttpResponse(next_url)
                    if next_url =='None' or not next_url:
                        next_url = reverse('userprofile:dashboard')
                    else:
                        pass
                    # return HttpResponse(next_url)
                    return HttpResponseRedirect(next_url)
                else:
                    message_login = _("Please wait for confirm account")
            else:
                if '@' in username:
                    message_login = _("Email or password incorrect")
                else:
                    message_login = _("username or password incorrect")

            context['message_login'] = message_login

            # else:

    return render(request, 'userprofile/general/sign-in.html', context=context)


@login_required(login_url='userprofile:sign_in')
def change_password(request):
    user = request.user
    user_profile = get_object_or_404(Profile, user=user)
    next_url = request.GET.get('next_url')
    form = ChangePasswordForm(request.POST or None)
    context = base_auth(req=request)
    context['form'] = form
    context['next_url'] = next_url
    if request.method == 'POST':
        if form.is_valid():
            clean_data = form.cleaned_data
            old_password = clean_data.get('old_password')
            new_password = clean_data.get('new_password')
            core = authenticate(username=user.username, password=old_password)
            if core:
            # if not logo:
            #     form.add_error('logo', _('this_field_is_required'))
            #     return render(request, 'profile/create_or_edit_product_service.html', context=context)
                user.set_password(new_password)
                if user_profile.type == 'employee-person':
                    employee_obj = get_object_or_404(Employee,profile=user_profile)
                    employee_obj.password = new_password
                    employee_obj.save()
                elif user_profile.type == 'admin-person':
                    pass
                else:
                    raise Http404
                user.save()
            else:
                form.add_error('old_password', _('Password is incorrect'))
                context['error_message'] = _('Password Successfully Changed ')
                return render(request, 'userprofile/general/change-password.html', context=context)
            context['message'] = _('Password Successfully Changed ')
            # else:

    return render(request, 'userprofile/general/change-password.html', context=context)



