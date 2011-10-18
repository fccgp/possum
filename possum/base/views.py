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
from django.template import RequestContext
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.core.context_processors import PermWrapper

def get_user(request):
    data = {}
    data['perms'] = PermWrapper(request.user)
    data['user'] = request.user
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

    return render_to_response('base/accueil.html', data)

@login_required
def carte(request):
    data = get_user(request)
    data['menu_carte'] = True
    return render_to_response('base/carte.html', data)

@login_required
def categories(request):
    data = get_user(request)
    data['menu_carte'] = True
    return render_to_response('base/categories.html', data)

@login_required
def pos(request):
    data = get_user(request)
    data['menu_pos'] = True
    return render_to_response('base/pos.html', data)

@login_required
def jukebox(request):
    data = get_user(request)
    data['menu_jukebox'] = True
    return render_to_response('base/jukebox.html', data)

@login_required
def stats(request):
    data = get_user(request)
    data['menu_stats'] = True
    return render_to_response('base/stats.html', data)

@login_required
def users(request):
    data = get_user(request)
    data['menu_users'] = True
    return render_to_response('base/users.html', data)

@login_required
def factures(request):
    data = get_user(request)
    data['menu_bills'] = True
#    data['factures'] = Facture.objects.all()
    return render_to_response('base/factures.html', data)

@login_required
def facture(request, id_facture):
    data = get_user(request)
    data['facture'] = get_object_or_404(Facture, pk=id_facture)
    return render_to_response('base/facture.html', data)

#	return render_to_response('login.html', data, 
#			context_instance=RequestContext(request))

