"""timeopt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.utils import translation
from django.views import generic
from django.views.static import serve
from content.views import *
from django.views import static
from django.conf import settings
from general import set_lang as core_views


urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^administration/', admin.site.urls,name="admin"),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
        url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT }, name='media')
]
translation.activate(settings.LANGUAGE_CODE)

urlpatterns += i18n_patterns(
    url(r'^test/$', index, name="index"),
    url(r'^set-language/$',core_views.set_language,  name='set_language'),
    url(r'^', include("timeopt.core.urls", namespace="core")),
    # url(r'^', include("general.urls", namespace="general")),
    # url(r'^', include("tour.urls", namespace="tour")),
    url(r'^', include("userprofile.urls", namespace="userprofile")),
    # url(r'^account/', include("base_user.urls", namespace="account")),
)

urlpatterns += staticfiles_urlpatterns()




@login_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)


if settings.DEBUG is False:   #if DEBUG is True it will be served automatically
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT }, name='static'),
        url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT }, name='media')
    ]
urlpatterns += staticfiles_urlpatterns()