from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(WorkDay)
admin.site.register(PlanEmployeeWork)

class LocationOrderAdmin(admin.ModelAdmin):
    list_display = ("get_employee","get_week","get_day","location","order_index","get_minute",)
    list_filter = ("order_index",)
    # list_filter =
    # search_fields = ("get_employee","get_week","get_day","get_minute",)
    def get_employee(self, obj):
        return "{} {}".format(obj.plan_employee_work.employee.first_name,obj.plan_employee_work.employee.last_name)
    def get_week(self, obj):
        return obj.plan_employee_work.week
    def get_day(self, obj):
        return obj.plan_employee_work.day.day
    def get_minute(self, obj):
        return obj.plan_employee_work.minute
admin.site.register(LocationOrder,LocationOrderAdmin)

class EmployeeWorkDayInlineAdmin(admin.TabularInline):
    model = EmployeeWorkDay
    extra = 0
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
             return 0
        return self.extra


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name","last_name","status",)
    list_filter = ("first_name","last_name","status",)
    search_fields = ("first_name","last_name",)
    inlines = (EmployeeWorkDayInlineAdmin,)
admin.site.register(Employee,EmployeeAdmin)


class SettingsAdmin(admin.ModelAdmin):
    list_display = ("title","main_plan","sub_plan","date",)
    list_filter = ("title","main_plan","sub_plan",)
    list_editable = ("main_plan","sub_plan",)
    search_fields = ("title",)
admin.site.register(Settings,SettingsAdmin)

class LocationAdmin(admin.ModelAdmin):
    list_display = ("name","work_times","address","status","minute","date",)
    list_filter = ("address","minute","work_times","name",)
    search_fields = ("name","address","minute",)
admin.site.register(Location,LocationAdmin)

class LocationDistanceAdmin(admin.ModelAdmin):
    list_display = ("location1","location2","main_company","minute","distance",)
    search_fields = ["location1__name","location2__name"]
    list_filter = ["location2__name","location1__name",]
admin.site.register(LocationDistance,LocationDistanceAdmin)

class DistanceErrorLogAdmin(admin.ModelAdmin):
    def date_fun(self, obj):
        return obj.date.strftime("%d %b %Y")
    def date_seconds(self, obj):
        return obj.date.strftime("%d %b %Y %H:%M:%S")
    list_display = ("location1","location2","date_fun","date_seconds",)
    search_fields = ["location1__name","location2__name"]
    list_filter = ["location2__name","location1__name",]
admin.site.register(DistanceErrorLog,DistanceErrorLogAdmin)





class PlanLogAdmin(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.date.strftime("%d %b %Y %H:%M:%S")

    # time_seconds.admin_order_field = 'date'
    list_display = ("time_seconds","complated","rejcected",)
admin.site.register(PlanLog,PlanLogAdmin)




class ExcelDocumentAdmin(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.date.strftime("%d %b %Y %H:%M:%S")

    # time_seconds.admin_order_field = 'date'
    list_display = ("time_seconds",)
admin.site.register(ExcelDocument,ExcelDocumentAdmin)
