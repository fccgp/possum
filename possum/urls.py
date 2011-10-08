from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
)

urlpatterns += patterns('possum.base.views',
    (r'^$', 'accueil'),
    (r'^accueil$', 'accueil'),
    (r'^factures$', 'factures'),
    (r'^facture/(?P<id_facture>\d+)/$', 'facture'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/pos/possum/static/'}),
    )
