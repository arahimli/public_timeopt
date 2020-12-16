from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.datetime_safe import datetime
from django.views.generic.edit import FormView
from django.shortcuts import redirect, render

from .forms import GenerateRandomUserForm
from .tasks import create_random_user_accounts


def base(req=None):
    lang = req.LANGUAGE_CODE
    data = {
        'now':datetime.now(),
    }
    return data


class GenerateRandomUserView(FormView):
    template_name = 'generate_random_users.html'
    form_class = GenerateRandomUserForm

    def form_valid(self, form):
        total = form.cleaned_data.get('total')
        print(total)
        create_random_user_accounts.delay(int(total))
        messages.success(self.request, 'We are generating your random users! Wait a moment and refresh this page.')
        return redirect('core:users_list')

def home(request):
    context = base(req=request)
    form = GenerateRandomUserForm()
    users = User.objects.all()

    context['form'] = form
    context['users'] = users
    return render(request, 'users.html', context=context)