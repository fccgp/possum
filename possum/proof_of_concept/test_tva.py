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

from datetime import datetime
from decimal import Decimal

montant_alcool = Decimal("0")
montant_normal = Decimal("0")
for facture in Facture().get_factures_du_jour(datetime(2011,1,27)).iterator():
    montant_alcool += facture.montant_alcool
    montant_normal += facture.montant_normal

#tva_normal = montant_normal - (montant_normal / Decimal("1.055"))
#tva_alcool = montant_alcool - (montant_alcool / Decimal("1.196"))
tva_normal = montant_normal * (Decimal("0.055") / Decimal("1.055"))
tva_alcool = montant_alcool * (Decimal("0.196") / Decimal("1.196"))

print "Montant normal: % 6.2f => TVA: % 6.2f" % (montant_normal, tva_normal)
print "Montant alcool: % 6.2f => TVA: % 6.2f" % (montant_alcool, tva_alcool)
print "-------------------------------------"
for ligne in Facture().rapport_jour(datetime(2011,1,27)):
    print ligne
print "-------------------------------------"
for ligne in Facture().rapport_mois(datetime(2011,1,27)):
    print ligne
