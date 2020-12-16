from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns

from .views import *


urlpatterns = [
	url(r'^log-out/$', log_out, name='log-out'),
	url(r'^sign-in/$', sign_in, name='sign_in'),
	url(r'^d/change-password/$', change_password, name='change-password'),
	url(r'^$', dashboard, name='dashboard'),
	url(r'^d/plan-prepare/$', plan_prepare, name='plan-prepare'),
	url(r'^d/plan-prepare/ajax/(?P<op_slug>[\w-]+)/$', plan_prepare_ajax, name='plan-prepare-ajax'),
	url(r'^d/employee-show-plan/ajax/$', employee_plan_show_ajax, name='employee-plan-ajax'),
	url(r'^d/admin-customer-from-excel/$', customer_upload_from_excel, name='admin-customer-upload-from-excel'),
	url(r'^d/admin-employee-show-plan/ajax/(?P<e_id>[0-9]+)/$', admin_employee_plan_show_ajax, name='admin-employee-plan-ajax'),
	url(r'^d/admin-employee-plan-form-generate/ajax/$', admin_employee_plan_form_generate_ajax, name='admin-employee-plan-form-generate-ajax'),
	url(r'^d/admin-employee-plan-form-customer-ajax/ajax/(?P<e_p_id>[0-9]+)/(?P<l_id>[0-9]+)/$', admin_employee_plan_form_location_ajax, name='admin-employee-plan-form-location-ajax'),
	url(r'^d/admin-employee-plan-form-change-location-position-ajax/ajax/(?P<cur_loc_ord_id>[0-9]+)/$', admin_employee_plan_form_change_location_position_ajax, name='admin-change-customer-position-ajax'),
	url(r'^d/admin-employee-show-map-plan/ajax/$', admin_employee_plan_show_map_ajax, name='admin-employee-plan-map-ajax'),
	url(r'^d/admin-all-employees-plans/$', admin_all_employees_plans, name='admin-all-employees-plans'),
	url(r'^d/admin-all-customers/$', admin_all_customers, name='admin-all-customers'),
	url(r'^d/admin-all-employees-plans/employee/(?P<e_id>[0-9]+)/$', admin_employee_plans, name='admin-employee-plans'),
	url(r'^d/all-plans/$', all_plans, name='all-plans'),
	url(r'^d/my-plans/$', my_plans, name='my-plans'),
	# url(r'^forgot-password/$', forgot_password, name='forgot_password'),

    # url(r'^contact/$', 'home.views.contact',name='contact'),

]
