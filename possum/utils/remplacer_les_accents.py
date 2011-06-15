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

def sans_accent(nom):
#    print "avant: ", nom
    nom = nom.replace(u"é", u"e")
    nom = nom.replace(u"è", u"e")
    nom = nom.replace(u"à", u"a")
#    nom.replace(u"\xe9", u"e")
#    nom.replace(u"\xe8", u"e")
#    print "apres: ", nom
    return nom

for p in Produit.objects.iterator():
    p.nom = sans_accent(p.nom)
    p.save()

for p in PaiementType.objects.iterator():
    p.nom = sans_accent(p.nom)
    p.save()

for p in Categorie.objects.iterator():
    p.nom = sans_accent(p.nom)
    p.save()

