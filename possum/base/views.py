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

from possum.base.models import Accompagnement, Sauce, Etat, \
    Categorie, Couleur, Cuisson, Facture, Log, LogType, Paiement, \
    PaiementType, Produit, ProduitVendu, Suivi, Table, Zone

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout

def accueil(request):
    """Liste des declarations pour un utilisateur"""
#    today = datetime.date.today()
    data = {}
#    data['user'] = request.user
#    declaration = Declaration.objects.filter(user=request.user).filter(greve__validation__isnull=False)
#    data['current'] = declaration.filter(greve__date_fin__gt=today).order_by('-greve__date_greve')
#    data['others'] = declaration.filter(greve__date_fin__lte=today).order_by('-greve__date_greve')
#   data['revision'] = get_svn_revision(".")

    return render_to_response('base/accueil.html', data)

def factures(request):
    data = {}
    data['factures'] = Facture.objects.all()
    return render_to_response('base/factures.html', data)

def facture(request, id_facture):
    data = {}
    data['facture'] = get_object_or_404(Facture, pk=id_facture)
    return render_to_response('base/facture.html', data)

def my_logout(request):
    logout(request)
    return HttpResponseRedirect('/declare/accueil')
