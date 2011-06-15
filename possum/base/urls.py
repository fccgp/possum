from django.conf.urls.defaults import *

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('possum.base.views',
    # Example:
    # (r'^trunk/', include('trunk.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
	(r'^$', 'accueil'),
	(r'^accueil$', 'accueil'),
	(r'^factures$', 'factures'),
#	(r'^greve/nouvelle$', 'new'),
	(r'^facture/(?P<id_facture>\d+)/$', 'facture'),
#	(r'^greve/(?P<greve_id>\d+)/valide$', 'valide'),
#	(r'^declaration$', 'declarations'),
#	(r'^declaration/$', 'declarations'),
#	(r'^declaration/(?P<declaration_id>\d+)/$', 'declaration'),
#	(r'^login$', 'my_login'),
#	(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'declare/login.html'}),
	(r'^logout$', 'my_logout'),
)
