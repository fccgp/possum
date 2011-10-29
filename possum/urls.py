from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('possum.base.views',
    (r'^$', 'accueil'),
#    (r'^accueil$', 'accueil'),

#    (r'^carte/$', 'carte'),    
    (r'^carte/categories/$', 'categories'),
    (r'^carte/categories/new/$', 'categories_new'),
    (r'^carte/categories/(?P<cat_id>\d+)/less/$', 'categories_less_priority'),
    (r'^carte/categories/(?P<cat_id>\d+)/more/$', 'categories_more_priority'),
    (r'^carte/categories/(?P<cat_id>\d+)/less-10/$', 'categories_less_priority', {'nb': 10}),
    (r'^carte/categories/(?P<cat_id>\d+)/more-10/$', 'categories_more_priority', {'nb': 10}),
    (r'^carte/categories/(?P<cat_id>\d+)/surtaxable/$', 'categories_surtaxable'),
    (r'^carte/categories/(?P<cat_id>\d+)/change/$', 'categories_change'),
    (r'^carte/categories/(?P<cat_id>\d+)/alcool/$', 'categories_alcool'),
    (r'^carte/categories/(?P<cat_id>\d+)/delete/$', 'categories_delete'),
    (r'^carte/categories/(?P<cat_id>\d+)/disable_surtaxe/$', 'categories_disable_surtaxe'),
    
    (r'^carte/products/$', 'categories'),
    (r'^carte/products/cat/(?P<cat_id>\d+)/$', 'products'),
    (r'^carte/products/(?P<product_id>\d+)/change/$', 'products_change'),
    (r'^carte/products/cat/(?P<cat_id>\d+)/new/$', 'products_new'),

    (r'^pos/$', 'pos'),
    (r'^bills/$', 'factures'),
    (r'^jukebox/$', 'jukebox'),
    (r'^stats/$', 'stats'),

    (r'^profile/$', 'profile'),

    (r'^users/$', 'users'),
    (r'^users/new/$', 'users_new'),
    (r'^users/(?P<user_id>\d+)/passwd/$', 'users_passwd'),
    (r'^users/(?P<user_id>\d+)/active/$', 'users_active'),
    (r'^users/(?P<user_id>\d+)/change/$', 'users_change'),
    (r'^users/(?P<user_id>\d+)/perm/(?P<codename>p\d+)/$', 'users_change_perm'),

    (r'^facture/(?P<id_facture>\d+)/$', 'facture'),
)

urlpatterns += patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
