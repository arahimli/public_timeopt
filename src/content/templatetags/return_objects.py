from django import template
from content.models import Employee,PlanEmployeeWork,EmployeeWorkDay

register = template.Library()


@register.assignment_tag
def plan_employee_works(employee,week,day):
    employee_obj = Employee.objects.filter(id=employee).first()
    plan_employee_work = PlanEmployeeWork.objects.filter(employee=employee_obj, week=week, day=day)
    return plan_employee_work


@register.assignment_tag
def get_random_testimonial():
    return Testimonials.objects.order_by('?')[0]