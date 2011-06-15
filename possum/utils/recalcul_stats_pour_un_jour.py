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

from datetime import datetime, timedelta

date = datetime(2011,1,27)
date_min = date.replace(hour=5)
date_max = date_min + timedelta(days=1)

# RAZ les stats
for stats in StatsJourGeneral.objects.filter(date=date).iterator():
    stats.valeur = "0"
    stats.save()
for stats in StatsJourCategorie.objects.filter(date=date).iterator():
    stats.valeur = "0"
    stats.nb = 0
    stats.save()
for stats in StatsJourProduit.objects.filter(date=date).iterator():
    stats.valeur = "0"
    stats.nb = 0
    stats.save()
for stats in StatsJourPaiement.objects.filter(date=date).iterator():
    stats.valeur = "0"
    stats.nb = 0
    stats.save()

for facture in Facture.objects.filter(date_creation__gt=date_min,
                                      date_creation__lt=date_max)\
                                      .iterator():
    facture.maj_stats()
#Facture().rapport_jour(date)
