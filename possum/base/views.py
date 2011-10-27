# -*- coding: utf-8 -*-
#
#    Copyright 2009, 2010, 2011 Sébastien Bonnegent
#
#    This file is part of POSSUM.
#
#    POSSUM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    POSSUM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with POSSUM.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
from possum.base.models import Accompagnement, Sauce, Etat, \
    Categorie, Couleur, Cuisson, Facture, Log, LogType, Paiement, \
    PaiementType, Produit, ProduitVendu, Suivi, Table, Zone
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
#from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.core.context_processors import PermWrapper
from django.contrib.auth.models import User, UserManager, Permission
from django.conf import settings
from django.contrib import messages

def get_user(request):
    data = {}
    data['perms'] = PermWrapper(request.user)
    data['user'] = request.user
#    data.update(csrf(request))
    return data

@login_required
def accueil(request):
#    today = datetime.date.today()
    data = get_user(request)
#    data['user'] = request.user
#    declaration = Declaration.objects.filter(user=request.user).filter(greve__validation__isnull=False)
#    data['current'] = declaration.filter(greve__date_fin__gt=today).order_by('-greve__date_greve')
#    data['others'] = declaration.filter(greve__date_fin__lte=today).order_by('-greve__date_greve')
#   data['revision'] = get_svn_revision(".")

    return render_to_response('base/accueil.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def carte(request):
    """This is not used.
    """
    data = get_user(request)
    data['menu_carte'] = True
    return render_to_response('base/carte.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def products(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    data['menu_carte'] = True
    data['products'] = Produit.objects.filter(categorie=cat)
    return render_to_response('base/products.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories(request):
    data = get_user(request)
    data['menu_carte'] = True
    data['categories'] = Categorie.objects.order_by('priorite', 'nom')
    return render_to_response('base/categories.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_less_priority(request, cat_id, nb=1):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    cat.priorite -= nb
    cat.save()
    logging.info("[%s] cat [%s] priority - %d" % (data['user'].username, cat.nom, nb))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_more_priority(request, cat_id, nb=1):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    cat.priorite += nb
    cat.save()
    logging.info("[%s] cat [%s] priority + %d" % (data['user'].username, cat.nom, nb))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_surtaxable(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.surtaxable
    cat.surtaxable = new
    cat.save()
    logging.info("[%s] cat [%s] surtaxable: %s" % (data['user'].username, cat.nom, cat.surtaxable))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_alcool(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.alcool
    cat.alcool = new
    cat.save()
    logging.info("[%s] cat [%s] alcool: %s" % (data['user'].username, cat.nom, cat.alcool))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_disable_surtaxe(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.disable_surtaxe
    cat.disable_surtaxe = new
    cat.save()
    logging.info("[%s] cat [%s] disable_surtaxe: %s" % (data['user'].username, cat.nom, cat.disable_surtaxe))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p5')
def pos(request):
    data = get_user(request)
    data['menu_pos'] = True
    return render_to_response('base/pos.html',
                                data,
                                context_instance=RequestContext(request))

@login_required
def jukebox(request):
    data = get_user(request)
    data['menu_jukebox'] = True
    return render_to_response('base/jukebox.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def stats(request):
    data = get_user(request)
    data['menu_stats'] = True
    return render_to_response('base/stats.html',
                                data,
                                context_instance=RequestContext(request))

@login_required
def profile(request):
    data = get_user(request)
    data['menu_profile'] = True
    old = request.POST.get('old', '').strip()
    new1 = request.POST.get('new1', '').strip()
    new2 = request.POST.get('new2', '').strip()
    if old:
        error = False
        if data['user'].check_password(old):
            if new1 and new1 == new2:
                data['user'].set_password(new1)
                data['user'].save()
                data['success'] = "Le mot de passe a été changé."
                logging.info('[%s] password changed' % data['user'].username)
            else:
                data['error'] = "Le nouveau mot de passe n'est pas valide."
                logging.warning('[%s] new password is not correct' % data['user'].username)
        else:
            data['error'] = "Le mot de passe fourni n'est pas bon."
            logging.warning('[%s] check password failed' % data['user'].username)
    return render_to_response('base/profile.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p1')
def users(request):
    data = get_user(request)
    data['menu_users'] = True
    data['perms_list'] = settings.PERMS
    data['users'] = User.objects.all()
    for user in data['users']:
         user.permissions = [p.codename for p in user.user_permissions.all()]
    return render_to_response('base/users.html', 
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p1')
def users_new(request):
    data = get_user(request)
    # data is here to create a new user ?
    login = request.POST.get('login', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    mail = request.POST.get('mail', '').strip()
    if login:
        user = User()
        user.username = login
        user.first_name = first_name
        user.last_name = last_name
        user.email = mail
        try:
            user.save()
            logging.info("[%s] new user [%s]" % (data['user'].username, login))
            #users(request)
        except:
            #data['error'] = "Le nouvel utilisateur n'a pu être créé."
            logging.warning("[%s] new user failed: [%s] [%s] [%s] [%s]" % (data['user'].username, login, first_name, last_name, mail))
            messages.add_message(request, messages.ERROR, "Le nouveau compte n'a pu être créé.")
    return HttpResponseRedirect('/users/')

@permission_required('base.p1')
def users_change(request, user_id):
    data = get_user(request)
    login = request.POST.get('login', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    mail = request.POST.get('mail', '').strip()
    user = get_object_or_404(User, pk=user_id)
    if login != user.username:
        logging.info("[%s] new login: [%s] > [%s]" % (data['user'].username, user.username, login))
        user.username = login
    if first_name != user.first_name:
        logging.info("[%s] new first name for [%s]: [%s] > [%s]" % (data['user'].username, user.username, user.first_name, first_name))
        user.first_name = first_name
    if last_name != user.last_name:
        logging.info("[%s] new last name for [%s]: [%s] > [%s]" % (data['user'].username, user.username, user.last_name, last_name))
        user.last_name = last_name
    if mail != user.email:
        logging.info("[%s] new mail for [%s]: [%s] > [%s]" % (data['user'].username, user.username, user.email, mail))
        user.email = mail

    try:
        user.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        logging.warning("[%s] save failed for [%s]" % (data['user'].username, user.username))
    return HttpResponseRedirect('/users/')

@permission_required('base.p1')
def users_active(request, user_id):
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    new = not user.is_active
    p1 = Permission.objects.get(codename="p1")
    if not new and p1.user_set.count() == 1 and p1 in user.user_permissions.all():
        messages.add_message(request, messages.ERROR, "Il doit rester au moins un compte actif avec la permission P1.")
        logging.warning("[%s] we must have at least one active user with P1 permission.")
    else:
        user.is_active = new
        user.save()
        logging.info("[%s] user [%s] active: %s" % (data['user'].username, user.username, user.is_active))
    return HttpResponseRedirect('/users/')

@permission_required('base.p1')
def users_passwd(request, user_id):
    """Set a new random password for a user.
    """
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    passwd = UserManager().make_random_password(length=10)
    user.set_password(passwd)
    user.save()
    messages.add_message(request, messages.SUCCESS, "Le nouveau mot de passe l'utilisateur %s est : %s" % (user.username, passwd))
    logging.info("[%s] user [%s] new password" % (data['user'].username, user.username))
    return HttpResponseRedirect('/users/')

@permission_required('base.p1')
def users_change_perm(request, user_id, codename):
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    # little test because because user can do ugly things :)
    # now we are sure that it is a good permission    
    if codename in settings.PERMS:
        perm = Permission.objects.get(codename=codename)
        if perm in user.user_permissions.all():
            if codename == 'p1' and perm.user_set.count() == 1:
                # we must have at least one person with this permission
                logging.info("[%s] user [%s] perm [%s]: at least should have one person" % (data['user'].username, user.username, codename))
                messages.add_message(request, messages.ERROR, "Il doit rester au moins 1 compte avec la permission P1.")
            else:
                user.user_permissions.remove(perm)
                logging.info("[%s] user [%s] remove perm: %s" % (data['user'].username, user.username, codename))
        else:
            user.user_permissions.add(perm)
            logging.info("[%s] user [%s] add perm: %s" % (data['user'].username, user.username, codename))
    else:
        logging.warning("[%s] wrong perm info : [%s]" % (data['user'].username, codename))
    return HttpResponseRedirect('/users/')

@permission_required('base.p3')
def factures(request):
    data = get_user(request)
    data['menu_bills'] = True
#    data['factures'] = Facture.objects.all()
    return render_to_response('base/factures.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p3')
def facture(request, id_facture):
    data = get_user(request)
    data['facture'] = get_object_or_404(Facture, pk=id_facture)
    return render_to_response('base/facture.html',
                                data,
                                context_instance=RequestContext(request))

#	return render_to_response('login.html', data, 
#			context_instance=RequestContext(request))

