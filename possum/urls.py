from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # Example:
    # (r'^benchmark/', include('benchmark.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^base/', include('possum.base.urls')),

    # Uncomment the next line to enable the admin:
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/pos/possum/static/'}),
    )
