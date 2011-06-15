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
"""Mise à jour des statistiques de la base.
"""

import sys, os
sys.path.append('/home/pos')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'
from django.conf import settings
import logging, logging.handlers

if settings.DEBUG:
    logging.basicConfig(
        level = logging.DEBUG,
        format = '[%(asctime)s %(filename)s:%(lineno)d %(funcName)s] '\
                '%(levelname)-8s %(message)s (%(relativeCreated)dms)',
        datefmt = '%Y-%m-%d %H:%M:%S'
    )
else:
    logging.basicConfig(
        level = logging.WARNING,
        format = '[%(asctime)s %(filename)s:%(lineno)d %(funcName)s] '\
                '%(levelname)-8s %(message)s (%(relativeCreated)dms)',
        datefmt = '%Y-%m-%d %H:%M:%S')
    LOG = logging.getLogger('')
    LOG.addHandler(logging.handlers.SMTPHandler("localhost", \
                   "possum@localhost", ["root@localhost"], "[POSSUM] "))

from possum.base.models import Facture

#for facture in Facture.objects.iterator():
    #facture.saved_in_stats = False
    #facture.save()

#Facture().maj_stats_avec_nouvelles_factures()

selection = Facture.objects.filter(saved_in_stats=False)

logging.info("parcours des factures")
if settings.DEBUG:
    import progressbar
    pbar = progressbar.ProgressBar(maxval=selection.count()).start()

count = 1
for facture in selection.iterator():
    if settings.DEBUG:
        pbar.update(count)
    facture.maj_stats()
    count += 1

if settings.DEBUG:
    pbar.finish()
