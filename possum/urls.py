from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^benchmark/', include('benchmark.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^base/', include('possum.base.urls')),
#       (r'^voting/', include('trunk.voting.urls')),

    # Uncomment the next line to enable the admin:
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
