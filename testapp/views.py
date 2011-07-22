from django.http import HttpResponse

def index(request):
    return HttpResponse('OK')

def return_post_data(request):
    print request.POST
    return HttpResponse(request.POST['data'])
