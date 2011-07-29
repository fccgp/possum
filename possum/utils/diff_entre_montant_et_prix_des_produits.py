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

from possum.base.models import Facture, StatsJourPaiement, \
                StatsJourGeneral, StatsJourProduit, StatsJourCategorie
from decimal import Decimal

count = 0
for f in Facture.objects.filter(id__gt=40000).iterator():
    if not f.est_surtaxe():
        total = Decimal('0')
        for p in f.produits.all():
            total += p.prix
        if total != f.get_montant():
            print "---------------------------------------------------------------"
            print "[%s] %.2f (facture) != %.2f (calcul)" % (f, f.get_montant(), total)
            for p in f.paiements.all():
                print p
            for p in f.produits.all():
                print "[%d] %s" % (p.id, p.produit.nom)
            count += 1

print count
