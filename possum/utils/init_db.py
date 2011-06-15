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

Couleur(id=1,red=255,green=159,blue=0).save()
Couleur(id=2,red=102,green=204,blue=153).save()
Couleur(id=3,red=255,green=200,blue=50).save()
Couleur(id=4,red=166,green=159,blue=189).save()
Couleur(id=5,red=184,green=218,blue=42).save()
Couleur(id=6,red=201,green=161,blue=0).save()
Couleur(id=7,red=69,green=224,blue=108).save()
Couleur(id=8,red=255,green=249,blue=160).save()
Couleur(id=9,red=255,green=249,blue=78).save()
Couleur(id=10,red=148,green=166,blue=255).save()
Couleur(id=11,red=255,green=225,blue=33).save()
Couleur(id=12,red=68,green=179,blue=220).save()
Couleur(id=13,red=234,green=101,blue=149).save()
Couleur(id=14,red=255,green=90,blue=109).save()
Couleur(id=15,red=234,green=151,blue=181).save()
Couleur(id=16,red=255,green=135,blue=149).save()
Couleur(id=17,red=29,green=255,blue=165).save()
Couleur(id=18,red=255,green=53,blue=96).save()
Couleur(id=19,red=136,green=240,blue=39).save()
Couleur(id=20,red=63,green=164,blue=172).save()

LogType(id=1,nom='Saint Saens Facturation System: ready',description='').save()
LogType(id=2,nom='Saint Saens Facturation System: shutting down',description='').save()
LogType(id=3,nom='Database initialized',description='').save()
LogType(id=4,nom='Rapport generated',description='').save()
LogType(id=5,nom='Warning',description='').save()
LogType(id=6,nom='Critical',description='').save()
LogType(id=7,nom='Nouveau Montant',description='').save()
LogType(id=8,nom='Version',description='').save()
LogType(id=9,nom='nb_couverts',description='Nombre de couverts').save()
LogType(id=10,nom='nb_factures',description='Nombre de factures').save()
LogType(id=11,nom='nb_bar',description='Nombre de factures pour le bar').save()
LogType(id=12,nom='ca_resto',description='CA restauration').save()
LogType(id=13,nom='ca_bar',description='CA bar').save()
LogType(id=14,nom='montant_alcool',description='Montant Alcool').save()
LogType(id=15,nom='maj_stats',description='61858').save()
LogType(id=16,nom='montant_normal',description='Montant Normal').save()
LogType(id=17,nom='tm_resto',description='TM restauration').save()
LogType(id=18,nom='ca',description='CA TTC').save()
LogType(id=19,nom='tm_bar',description='TM bar').save()
LogType(id=20,nom='tva_alcool',description='TVA Alcool').save()
LogType(id=21,nom='tva_normal',description='TVA Normal').save()
