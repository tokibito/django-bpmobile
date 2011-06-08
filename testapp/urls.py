from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^testapp/$', 'testapp.views.index',name='testapp_index'),
)
