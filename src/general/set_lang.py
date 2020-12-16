from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import check_for_language

from django.utils import translation
# def set_language(request):
def set_language(request):
    lang_code = request.GET.get('language', None)
    # translation.activate(lang_code)
    next = request.GET.get('next', None)
    if next:
        next = next.split('/', 2)
        next = '/' + next[len(next)-1]
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    # level_count = next.split('/').__len__() - 3
    # field = 'slug_' + lang_code
    # print (next)

    # return HttpResponse(next )
    if request.method == 'GET':
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
                next = '/'+lang_code+next
                translation.activate(lang_code)
    response = HttpResponseRedirect(next)
    return response