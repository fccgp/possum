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
from datetime import datetime, timedelta

sys.path.append('/home/pos')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

#from trunk.base.models import Accompagnement, Sauce, Etat, Categorie, Couleur, Cuisson, Facture, Log, LogType, Paiement, PaiementType, Produit, ProduitVendu, Suivi, Table, Zone
from possum.base.models import Facture

debut = datetime.now()
output = "/tmp/maj_nb_couverts.py"
fd = open(output, "w")
fd.write("#!/usr/bin/env python\n")
fd.write("import sys, os\n")
fd.write("sys.path.append('/home/pos')\n")
fd.write("os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'\n")
fd.write("from possum.base.models import Facture\n")
# on considere que les factures dont le nombre de couverts n'est pas a 0
# contiennent le bon nombre de couverts
count = 0
for f in Facture.objects.filter(couverts=0).iterator():
    guest = f.guest_couverts()
    if guest != 0:
        count += 1
        #print "[%06d] guest: %d" % (f.id, guest)
        fd.write("f = Facture.objects.get(id=%d)\n" % f.id)
        fd.write("f.couverts = %d\n" % guest)
        fd.write("f.save()\n")
fd.close()
print "pour appliquer les changements, voir le fichier: %s" % output
print "%d factures concernees" % count
print datetime.now() - debut
