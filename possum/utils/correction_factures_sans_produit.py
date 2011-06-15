#!/usr/bin/env python
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
import sys, os
sys.path.append('/home/pos')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from possum.base.models import Accompagnement, Sauce, Etat, \
    Categorie, Couleur, Cuisson, Facture, Log, LogType, Paiement, \
    PaiementType, Produit, ProduitVendu, Suivi, Table, Zone

# il faut une categorie
c = Categorie.objects.get(id=1)

for f in Facture.objects.exclude(restant_a_payer=0, produits__isnull=False):
    filter = Produit.objects.filter(prix=f.get_montant())
    count = filter.count()
    if count > 0:
        p = filter[0]
        print p.nom
    else:
        nom = "recuperation ancienne base (%0.2f)" % f.get_montant()
        print nom
        p = Produit(nom=nom, nom_facture=nom, prix=f.get_montant(), actif=False, categorie=c)
        p.save()
    vendu = ProduitVendu(produit=p, facture=f)
    vendu.save()
    f.produits.add(vendu)

