from django.conf.urls import url

from timeopt.core.views import GenerateRandomUserView, home

urlpatterns = [
    url(r'^generate/users/form/$', GenerateRandomUserView.as_view(), name="generate-users"),
    # url(r'^generate/users-home/$', home, name="users_list"),
    url(r'^generate/users-home/$', home, name="users_list"),
]