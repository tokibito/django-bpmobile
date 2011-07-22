from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^testapp/$', 'testapp.views.index',name='testapp_index'),
    url(r'^testapp/return_post_data$', 'testapp.views.return_post_data',name='testapp_return_post_data'),
)
