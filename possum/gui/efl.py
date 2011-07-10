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

"""POSSUM GUI using EFL"""

import os, sys
from elementary import cursors
import elementary
import ecore
import evas
import locale
import io
from datetime import datetime, timedelta
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

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
    #handler = logging.handlers.SMTPHandler("localhost", \
    #                "possum@localhost", ["root@localhost"], "[POSSUM] ")
    LOG = logging.getLogger('')
    LOG.addHandler(logging.handlers.SMTPHandler("localhost", \
                   "possum@localhost", ["root@localhost"], "[POSSUM] "))

from possum.base.models import Accompagnement, Sauce, Etat, \
    Categorie, Couleur, Cuisson, Facture, Log, LogType, Paiement, \
    PaiementType, Produit, ProduitVendu, Suivi, Table, Zone, \
    StatsJourGeneral

# on temporise pour etre sur que la base postgres est demarree
from time import sleep
from psycopg2 import OperationalError
DB_NOT_READY = True
while DB_NOT_READY:
    try:
        Zone.objects.count()
        DB_NOT_READY = False
    except OperationalError:
        logging.debug("database not ready, we wait ...")
        sleep(2)

Log(type=LogType.objects.get(id=1)).save()

try:
    from decimal import Decimal
except ImportError:
    logging.critical("Librairie decimal introuvable")
    sys.exit()

try:
    import mpd
except ImportError:
    logging.warning("Librairie MPD introuvable")

# liste des frames de produits par id de categorie
# pour pouvoir les afficher
# fr_produits[3].show()
FRAMES_PRODUITS = {}
# la categorie courante
FRAMES_PRODUITS["actif"] = None
# valeur du nombre dans la calculatrice
NOMBRES_VALEUR = Decimal("0.00")
NOMBRES_COEF = Decimal("0.00")
# boite correspondant a l'ecran de la partie calculatrice
COMPTEUR_CAL = {}
COMPTEUR_TOTAL = {}
COMPTEUR_RESTE = {}
CPT_CAL = 0
CPT_TOTAL = 1
CPT_RESTE = 2
# date pour les rapports
RAPPORT_DATE = None
RAPPORT_JOUR_BT = None
# la progressBar
PB = None
# le label de la partie musique
PB_LABEL = None
# dict qui contient toutes les notifications pour le choix des sous produits
NOTIFY_VENDU = {}
# si besoin, contient le produit en cours d'ajout (cas des menus)
VENDU_COURANT = None
# le spinner avec le nombre de couverts
F_COUVERTS = None
# le hover pour le choix de l'etat
F_ETAT = None
# le hover pour le choix de la table
F_TABLE = None
# affichage de la tva
F_TVA = None
# element selectionne dans la liste des produits d'une facture
F_LISTE_PRODUIT_COURANT = None
# List representant les produits dans une facture
F_LISTE_PRODUITS = None
# liste contenant les paiements
F_LISTE_PAIEMENTS = None
# element selectionne dans la liste des paiements d'une facture
F_LISTE_PAIEMENT_COURANT = None
# nombre de facture soldee / non soldee
F_SOLDEE = Facture().nb_soldee_jour(datetime.today())
# les factures en cours
F_LISTE = Facture().non_soldees()
F_NON_SOLDEE = len(F_LISTE)
# valeur des tickets restos
try:
    VALEUR_TR = Paiement.objects.filter(type__nom="Tic. Resto." \
                                            ).latest().valeur_unitaire
except:
    VALEUR_TR = Decimal("5")
try:
    VALEUR_ANCV = Paiement.objects.filter(type__nom="ANCV" \
                                            ).latest().valeur_unitaire
except:
    VALEUR_ANCV = Decimal("7")
# le numero de la facture courante
F_INDEX = 0
if not F_NON_SOLDEE:
    # on cree une facture vide
    facture = Facture()
    facture.save()
    F_NON_SOLDEE += 1
    F_LISTE.append(facture)
# on construit d'avance le panneau de choix de table
#t_choix_frame = None
#c_choix_frame = None
# le montant des paiements
F_PAYER = None
# le montant de la facture
F_TOTAL = None
# les valeurs de TR et ANCV
BT_ANCV = None
BT_TR = None
#notify_admin_access = None
#admin_current = ""
#notify_admin_pass = None
HISTO_PRODUITS = None
HISTO_PAIEMENTS = None
# pour les Genlist
# comment est afficher l'item dans la liste
def gl_label_get(obj, part, item_data):
    return "%s" % (item_data.show(),)

def gl_label_get_sub(obj, part, item_data):
    return "%s" % (item_data.showSubProducts(),)

def gl_label_get_str(obj, part, item_data):
    return item_data

def gl_icon_get(obj, part, data):
    ic = elementary.Icon(obj)
    return ic

def gl_state_get(obj, part, item_data):
    return False

#def gl_sel(gli, gl, *args, **kwargs):
#    print gli.i
#    print "selection item %s on genlist %s" % (gli, gl)

ITC_PRODUIT = elementary.GenlistItemClass(item_style="default",
                               label_get_func=gl_label_get,
                               icon_get_func=gl_icon_get,
                               state_get_func=gl_state_get)
ITC_SOUS_PRODUIT = elementary.GenlistItemClass(item_style="default",
                               label_get_func=gl_label_get_sub,
                               icon_get_func=gl_icon_get,
                               state_get_func=gl_state_get)
ITC_STR = elementary.GenlistItemClass(item_style="default",
                               label_get_func=gl_label_get_str,
                               icon_get_func=gl_icon_get,
                               state_get_func=gl_state_get)

try:
    MPD_CLIENT = mpd.MPDClient()
except:
    logging.warning("MPDCLIENT a echoue !")
    MPD_CLIENT = None
    logging.warning("Librairie python-mpd installee ?")

def destroy(obj):
    Facture().maj_stats_avec_nouvelles_factures()
    Log(type=LogType.objects.get(id=2)).save()
    elementary.exit()
    logging.info("POSSUM terminate.")
    logging.shutdown()

elementary.init()
win = elementary.Window("possum", elementary.ELM_WIN_BASIC)
win.resize(1024, 768)
win.title_set("P.O.S.S.U.M")
win.callback_destroy_add(destroy)

CURSOR = cursors.ELM_CURSOR_TCROSS

if not settings.DEBUG:
    win.fullscreen = True

def admin_panel_exit(bt):
    global notify_admin_panel
    notify_admin_panel.hide()

def admin_access_ok(bt, username, password, notify, entry):
    global notify_admin_panel, RAPPORT_DATE, \
           RAPPORT_JOUR_BT, RAPPORT_MOIS_BT, RAPPORT_ANNEE_BT
    notify.hide()
    if Facture().authenticate(username.label_get(), password.entry_get()):
        # on enleve de l'affichage les factures soldees
        f_menage()
        f_show()
        # mot de passe ok
        today = datetime.today()
        # s'il est entre 0h et 5h, on suppose que l'on voudra les
        # rapports de la veille
        if today.hour < 5:
            RAPPORT_DATE = today - timedelta(days=1)
        else:
            RAPPORT_DATE = today
        logging.debug(RAPPORT_DATE)
        RAPPORT_JOUR_BT.label_set("%d" % RAPPORT_DATE.day)
        RAPPORT_MOIS_BT.label_set(RAPPORT_DATE.strftime("%B"))
        RAPPORT_ANNEE_BT.label_set("%d" % RAPPORT_DATE.year)
        notify_admin_panel.show()
        maj_stats()
    else:
        logging.warning("mot de passe invalide pour %s" \
                        % username.label_get())
    entry.entry_set("")

def calcul_des_stats(notify):
    logging.debug("signal recu")
    Facture().maj_stats_avec_nouvelles_factures()
    notify.hide()

def maj_stats():
    """ on mets un panneau d'attente, le temps que les stats soient
    calculee"""
    global win
    notify_stats = elementary.Notify(win)
    notify_stats.repeat_events_set(False)
    notify_stats.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    bx = elementary.Box(win)
    bx.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    notify_stats.content_set(bx)
    bx.show()

    # la progressbar ne bouge pas pendant les calculs, elle n'a donc
    # aucun interet
    #pbar = elementary.Progressbar(win)
    #pbar.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    #pbar.size_hint_align_set(evas.EVAS_HINT_FILL, 0.5)
    #pbar.pulse_set(True)
    #pbar.pulse(True)
    #bx.pack_end(pbar)
    #pbar.show()

    lb = elementary.Label(win)
    lb.label_set("<br>Mise à jour des statistiques, "
                 "merci de patienter quelques instants.<br><br>")
    bx.pack_end(lb)
    lb.show()

    notify_stats.show()
    ecore.timer_add(0.5, calcul_des_stats, notify_stats)

def admin_access_add(bt, caractere, entry):
    tmp = entry.entry_get()
    tmp += caractere
    entry.entry_set(tmp)

def admin_access_del(bt, entry):
    tmp = entry.entry_get()
    tmp = tmp[:-1]
    entry.entry_set(tmp)

def admin_access_cancel(bt, notify, entry):
    logging.warning("tentative d'acces au panneau d'admin")
    notify.hide()
    entry.entry_set("")

def admin_access_user_change(bt, item):
    bt.label_set(item.label_get())

def create_admin_access():
    """Creation d'avance du panneau de choix de table"""
#    global win, notify_admin_pass
    global win

    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    fr = elementary.Frame(win)
    fr.label_set("Accès au mode Admin")
    fr.show()

    notify.content_set(fr)

    tb = elementary.Table(win)
    tb.show()
    fr.content_set(tb)

    # nombres de case de largeur
    largeur = 16

    # on selectionne par defaut le dernier utilisateur qui s'est
    # connecte et liste des comptes actifs et par ordre alphabetique
    users = elementary.Hoversel(win)
    users.hover_parent_set(win)
    users.label_set(Facture().get_last_connected())
    users.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    users.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    for username in Facture().get_users():
        users.item_add(username, callback=admin_access_user_change)
    users.show()
    tb.pack(users, 0, 0, 4, 1)

    notify_admin_pass = elementary.ScrolledEntry(win)
    notify_admin_pass.password_set(True)
    notify_admin_pass.single_line_set(True)
    notify_admin_pass.entry_set("")
    notify_admin_pass.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    notify_admin_pass.size_hint_align_set(evas.EVAS_HINT_FILL, 0.5)
    notify_admin_pass.disabled_set(True)
    tb.pack(notify_admin_pass, 4, 0, largeur-4, 1)
    notify_admin_pass.show()

    x = 2
    y = 1
    for i in '1234567890':
        bt = elementary.Button(win)
        bt.label_set(i)
        bt.callback_clicked_add(admin_access_add, i, notify_admin_pass)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        x += 1

    bt = elementary.Button(win)
    bt.label_set("Suppr")
    bt.callback_clicked_add(admin_access_del, notify_admin_pass)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, x, y, 2, 1)
    y += 1
    x = 0

    for i in """!"#$%&'()*+,-./:""":
        bt = elementary.Button(win)
        bt.label_set(i)
        bt.callback_clicked_add(admin_access_add, i, notify_admin_pass)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        x += 1
    y += 1
    x = 0

    for i in """;<=>?@[\]^_`{|}~""":
        bt = elementary.Button(win)
        bt.label_set(i)
        bt.callback_clicked_add(admin_access_add, i, notify_admin_pass)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        x += 1
    y += 1
    x = 1

    for i in 'ABCDEFGHIJKLMN':
        bt = elementary.Button(win)
        bt.label_set(i)
        bt.callback_clicked_add(admin_access_add, i, notify_admin_pass)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        x += 1
    y += 1
    x = 2

    for i in 'OPQRSTUVWXYZ':
        bt = elementary.Button(win)
        bt.label_set(i)
        bt.callback_clicked_add(admin_access_add, i, notify_admin_pass)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        x += 1
    y += 1
    x = 1

    for i in 'abcdefghijklmn':
        bt = elementary.Button(win)
        bt.label_set(i)
        bt.callback_clicked_add(admin_access_add, i, notify_admin_pass)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        x += 1
    y += 1
    x = 2

    for i in 'opqrstuvwxyz':
        bt = elementary.Button(win)
        bt.label_set(i)
        bt.callback_clicked_add(admin_access_add, i, notify_admin_pass)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        x += 1
    y += 1
    x = 0

    sp = elementary.Separator(win)
    sp.horizontal_set(True)
    sp.show()
    tb.pack(sp, 0, y, largeur, 1)
    y += 1

    bt = elementary.Button(win)
    bt.label_set("Valider")
    bt.callback_clicked_add(admin_access_ok,
                            username=users,
                            password=notify_admin_pass,
                            notify=notify,
                            entry=notify_admin_pass)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, largeur-6, y, 4, 1)

    bt = elementary.Button(win)
    bt.label_set("Annuler")
    bt.callback_clicked_add(admin_access_cancel,
                            notify=notify,
                            entry=notify_admin_pass)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 2, y, 4, 1)

    notify.hide()
    return notify

def choix_jour_clicked(bt, day, notify, bt_clicked):
    global RAPPORT_DATE
    tmp = RAPPORT_DATE.replace(day=day)
    RAPPORT_DATE = tmp
    logging.debug(RAPPORT_DATE)
    notify.hide()
    bt_clicked.label_set("%d" % day)

def choix_mois_clicked(bt, mois, notify, bt_clicked):
    global RAPPORT_DATE, RAPPORT_JOUR_BT
    try:
        tmp = RAPPORT_DATE.replace(month=mois)
    except ValueError:
        tmp = RAPPORT_DATE.replace(month=mois, day=1)
        RAPPORT_JOUR_BT.label_set("1")
    RAPPORT_DATE = tmp
    logging.debug(RAPPORT_DATE)
    notify.hide()
    bt_clicked.label_set(RAPPORT_DATE.strftime("%B"))

def choix_annee_clicked(bt, year, notify, bt_clicked):
    global RAPPORT_DATE, RAPPORT_JOUR_BT
    try:
        tmp = RAPPORT_DATE.replace(year=year)
    except ValueError:
        tmp = RAPPORT_DATE.replace(year=year, day=1)
        RAPPORT_JOUR_BT.label_set("1")
    RAPPORT_DATE = tmp
    logging.debug(RAPPORT_DATE)
    notify.hide()
    bt_clicked.label_set("%d" % year)

def choix_jour(bt_clicked):
    global win
    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    fr = elementary.Frame(win)
    fr.label_set("Choix du jour")
    fr.show()

    notify.content_set(fr)

    tb = elementary.Table(win)
    tb.show()
    fr.content_set(tb)

    if RAPPORT_DATE.month == 12:
        nb_jours = 31
    else:
        # on prend le 1er jour du mois suivant auquel on enleve 1 jour
        mois_suivant = RAPPORT_DATE.replace(month=RAPPORT_DATE.month+1,
                                            day=1) - timedelta(days=1)
        nb_jours = mois_suivant.day
    x = 0
    y = 0
    for i in xrange(1, nb_jours + 1):
        bt = elementary.Button(win)
        bt.label_set("           %d           " % i)
        bt.callback_clicked_add(choix_jour_clicked, i, notify, bt_clicked)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        if y < 8:
            y += 1
        else:
            y = 0
            x += 1
    notify.show()

def choix_mois(bt_clicked):
    global win
    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    fr = elementary.Frame(win)
    fr.label_set("Choix du mois")
    fr.show()

    notify.content_set(fr)

    tb = elementary.Table(win)
    tb.homogenous_set(True)
    tb.show()
    fr.content_set(tb)

    # on se positionne le 1er du mois, car si on est le 31,
    # on ne pourra pas générer tous les mois de l'année
    date = datetime.today().replace(day=1)
    x = 0
    y = 0
    logging.debug(date)
    for i in xrange(1, 13):
        tmp = date.replace(month=i)
        bt = elementary.Button(win)
        bt.label_set(tmp.strftime("           %B           "))
        bt.callback_clicked_add(choix_mois_clicked, i, notify, bt_clicked)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        if y < 3:
            y += 1
        else:
            y = 0
            x += 1
    notify.show()

def choix_annee(bt_clicked):
    """Choix de l'annee pour les rapports
    """
    global win
    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    fr = elementary.Frame(win)
    fr.label_set("Choix de l'année")
    fr.show()

    notify.content_set(fr)

    tb = elementary.Table(win)
    tb.show()
    fr.content_set(tb)

    year_min = Facture.objects.get(id=1).date_creation.year
    year_max = datetime.today().year

    x = 0
    y = 0
    for year in xrange(year_min, year_max + 1):
        bt = elementary.Button(win)
        bt.label_set("           %d           " % year)
        bt.callback_clicked_add(choix_annee_clicked, year, notify, bt_clicked)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.show()
        tb.pack(bt, x, y, 1, 1)
        if y < 3:
            y += 1
        else:
            y = 0
            x += 1
    notify.show()

def create_admin_panel():
    """Creation d'avance du panneau de choix de table"""
    global win, notify_admin_panel, \
           RAPPORT_DATE, \
           RAPPORT_JOUR_BT, RAPPORT_MOIS_BT, RAPPORT_ANNEE_BT

    notify_admin_panel = elementary.Notify(win)
    notify_admin_panel.repeat_events_set(False)
    notify_admin_panel.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    fr = elementary.Frame(win)
    fr.label_set("Administration")
    fr.show()

    notify_admin_panel.content_set(fr)

    tb = elementary.Table(win)
    #tb.homogenous_set(True)
    tb.show()
    fr.content_set(tb)

    l = elementary.Label(win)
    l.label_set("Date:")
    l.show()
    tb.pack(l, 0, 0, 1, 1)

    bt = elementary.Button(win)
    bt.label_set("--")
    bt.callback_clicked_add(choix_jour)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    RAPPORT_JOUR_BT = bt
    tb.pack(bt, 1, 0, 1, 1)

    bt = elementary.Button(win)
    bt.label_set("------")
    bt.callback_clicked_add(choix_mois)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    RAPPORT_MOIS_BT = bt
    tb.pack(bt, 2, 0, 1, 1)

    bt = elementary.Button(win)
    bt.label_set("----")
    bt.callback_clicked_add(choix_annee)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    RAPPORT_ANNEE_BT = bt
    tb.pack(bt, 3, 0, 1, 1)

    sp = elementary.Separator(win)
    sp.horizontal_set(True)
    sp.show()
    tb.pack(sp, 0, 1, 4, 1)

    bt = elementary.Button(win)
    bt.label_set("Rapport du jour sélectionné")
    bt.callback_clicked_add(afficher_rapport_jour)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 0, 2, 2, 1)

    bt = elementary.Button(win)
    bt.label_set("Rapport du mois sélectionné")
    bt.callback_clicked_add(afficher_rapport_mois)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 0, 3, 2, 1)

    bt = elementary.Button(win)
    bt.label_set("Historique du jour sélectionné")
    bt.callback_clicked_add(historique)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 2, 2, 2, 1)

    bt = elementary.Button(win)
    bt.label_set("Liste des produits")
    bt.callback_clicked_add(liste_des_produits)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 2, 3, 2, 1)

    sp = elementary.Separator(win)
    sp.horizontal_set(True)
    sp.show()
    tb.pack(sp, 0, 4, 4, 1)

    bt = elementary.Button(win)
    bt.label_set("Retour au mode normal")
    bt.callback_clicked_add(admin_panel_exit)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 0, 5, 4, 1)

    notify_admin_panel.hide()

def histo_exit(bt, notify):
    """On sort du panneau historique"""
    notify.hide()

def histo_facture(bt, item, f):
    global HISTO_PRODUITS, HISTO_PAIEMENTS
    HISTO_PRODUITS.clear()
    for vendu in f.produits.order_by(\
                        'produit__categorie__priorite').iterator():
        HISTO_PRODUITS.item_append(ITC_PRODUIT, vendu)
        for sous_produit in vendu.contient.order_by(\
                        'produit__categorie__priorite').iterator():
            HISTO_PRODUITS.item_append(ITC_SOUS_PRODUIT, sous_produit)
    HISTO_PAIEMENTS.clear()
    for paiement in f.paiements.iterator():
        HISTO_PAIEMENTS.item_append(ITC_PRODUIT, paiement)

def notify_imprimable(titre, texte):
    """Affiche un texte qui peut directement être envoyé
    à l'imprimante.

    - texte: est sous la forme d'une liste ['ligne1', 'ligne2', ...]
    """
    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    fr = elementary.Frame(win)
    fr.label_set(titre)
    fr.show()

    notify.content_set(fr)

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND,
                            evas.EVAS_HINT_EXPAND)
    tb.homogenous_set(True)
    tb.size_hint_align_set(evas.EVAS_HINT_FILL,
                           evas.EVAS_HINT_FILL)
    tb.show()
    fr.content_set(tb)

    liste = elementary.Genlist(win)
    liste.size_hint_weight_set(evas.EVAS_HINT_EXPAND, \
                                          evas.EVAS_HINT_EXPAND)
    liste.size_hint_align_set(evas.EVAS_HINT_FILL, \
                                         evas.EVAS_HINT_FILL)

    for line in texte:
        # on affiche le nombre d'element
        liste.item_append(ITC_STR, line)

    liste.show()
    tb.pack(liste,0,0,15,15)

    bt = elementary.Button(win)
    bt.label_set("Imprimer")
    bt.callback_clicked_add(imprimer_texte, texte)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 11, 15, 2, 1)

    bt = elementary.Button(win)
    bt.label_set("Retour")
    bt.callback_clicked_add(histo_exit, notify)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 2, 15, 2, 1)

    notify.show()

def liste_des_produits(bt):
    """Permet d'afficher la liste des produits en vente
    """
    liste = []
    for categorie in Categorie.objects.order_by('priorite').iterator():
        # on affiche le nombre d'element
        liste.append(categorie.show())
        for produit in Produit.objects.filter(categorie=categorie,
                                              actif=True):
            liste.append(produit.show())

    notify_imprimable("Liste des produits", liste)

def historique(bt):
    """Creation du panneau historique"""
    global win, RAPPORT_DATE, HISTO_PRODUITS, HISTO_PAIEMENTS

    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    fr = elementary.Frame(win)
    fr.label_set("Historique")
    fr.show()

    notify.content_set(fr)

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, \
                               evas.EVAS_HINT_EXPAND)
    tb.homogenous_set(True)
#    tb.size_hint_align_set(evas.EVAS_HINT_FILL, \
#                              evas.EVAS_HINT_FILL)
    tb.show()
    fr.content_set(tb)

    # la liste des factures
    liste = elementary.Genlist(win)
    liste_factures = Facture().get_factures_du_jour(RAPPORT_DATE)
    if len(liste_factures):
        first = liste_factures[0]
    else:
        logging.debug("aucune facture")
        first = None
        liste.item_append(ITC_STR, "Aucune")
    # liste des produits
    fr_produits = elementary.Frame(win)
    fr_produits.label_set("Produits")
    fr_produits.size_hint_weight_set(evas.EVAS_HINT_EXPAND,
                             evas.EVAS_HINT_EXPAND)
    fr_produits.size_hint_align_set(evas.EVAS_HINT_FILL,
                            evas.EVAS_HINT_FILL)
    fr_produits.show()
#    tb.pack(fr_produits, 2, 0, 3, 10)
    tb.pack(fr_produits, 2, 0, 3, 6)
    liste_produits = elementary.Genlist(win)
    liste_produits.size_hint_weight_set(evas.EVAS_HINT_EXPAND, \
                                evas.EVAS_HINT_EXPAND)
    liste_produits.size_hint_align_set(evas.EVAS_HINT_FILL, \
                               evas.EVAS_HINT_FILL)
    #tb.pack(liste_produits, 2, 0, 2, 6)
    HISTO_PRODUITS = liste_produits
    liste_produits.show()
    fr_produits.content_set(liste_produits)
    if first:
        for vendu in first.produits.order_by(\
                            'produit__categorie__priorite').iterator():
            #liste_produits.item_append(vendu.show())
            liste_produits.item_append(ITC_PRODUIT, vendu)
            for sous_produit in vendu.contient.order_by(\
                            'produit__categorie__priorite').iterator():
                #liste_produits.item_append(sous_produit.showSubProducts())
                liste_produits.item_append(ITC_SOUS_PRODUIT, sous_produit)
    else:
        liste_produits.item_append(ITC_STR, "Aucun")
    # liste des paiements
    fr_paiements = elementary.Frame(win)
    fr_paiements.label_set("Paiements")
    fr_paiements.size_hint_weight_set(evas.EVAS_HINT_EXPAND,
                             evas.EVAS_HINT_EXPAND)
    fr_paiements.size_hint_align_set(evas.EVAS_HINT_FILL,
                            evas.EVAS_HINT_FILL)
    fr_paiements.show()
#    tb.pack(fr_paiements, 5, 4, 2, 6)
    tb.pack(fr_paiements, 2, 6, 3, 4)
    liste_paiements = elementary.Genlist(win)
    liste_paiements.size_hint_weight_set(evas.EVAS_HINT_EXPAND, \
                                          evas.EVAS_HINT_EXPAND)
    liste_paiements.size_hint_align_set(evas.EVAS_HINT_FILL, \
                                         evas.EVAS_HINT_FILL)
    #tb.pack(liste_paiements, 4, 4, 2, 2)
    HISTO_PAIEMENTS = liste_paiements
    liste_paiements.show()
    if first:
        for paiement in first.paiements.iterator():
            #liste_paiements.item_append(paiement.show())
            liste_paiements.item_append(ITC_PRODUIT, paiement)
    else:
        liste_paiements.item_append(ITC_STR, "Aucun")
    fr_paiements.content_set(liste_paiements)
    # liste des factures
    fr_factures = elementary.Frame(win)
    fr_factures.size_hint_weight_set(evas.EVAS_HINT_EXPAND,
                             evas.EVAS_HINT_EXPAND)
    fr_factures.size_hint_align_set(evas.EVAS_HINT_FILL,
                            evas.EVAS_HINT_FILL)
    fr_factures.label_set("Factures")
    fr_factures.show()

    for f in liste_factures.iterator():
        liste.item_append(ITC_PRODUIT, \
                          f, \
                          func=histo_facture)
    liste.size_hint_weight_set(evas.EVAS_HINT_EXPAND, \
                               evas.EVAS_HINT_EXPAND)
    liste.size_hint_align_set(evas.EVAS_HINT_FILL, \
                              evas.EVAS_HINT_FILL)
    liste.show()
    fr_factures.content_set(liste)
    tb.pack(fr_factures, 0, 0, 2, 10)

    bt = elementary.Button(win)
    bt.label_set("Retour")
    bt.callback_clicked_add(histo_exit, notify)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
#    tb.pack(bt, 0, 10, 10, 1)
    tb.pack(bt, 2, 10, 2, 1)

    rapport = Facture().rapport_jour(RAPPORT_DATE)
    bt = elementary.Button(win)
    bt.label_set("Imprimer")
    bt.callback_clicked_add(imprimer_texte, rapport)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 6, 10, 2, 1)

    fr_stats = elementary.Frame(win)
    fr_stats.label_set("Informations")
    fr_stats.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fr_stats.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fr_stats.show()
#    tb.pack(fr_stats, 5, 0, 2, 4)
    tb.pack(fr_stats, 5, 0, 5, 10)

    # les stats de l'annee derniere
    last = RAPPORT_DATE.replace(year=RAPPORT_DATE.year-1) + timedelta(days=1)

    en = elementary.Label(win)
    stats = StatsJourGeneral()
    
    en.label_set("<b>%s</><br>" 
                 "-----------------------------------------------------"
                 "-------------------------------------------------<br>"
                 "CA TTC: <b>%.2f</b>"
                 "    (moy. %.2f / max. %.2f)<br>"
                 "Nb factures: <b>%d</b>"
                 "    (moy. %.2f / max. %d)<br>"
                 "<br>"
                 "CA Resto: <b>%.2f</b>"
                 "    (moy. %.2f / max. %.2f)<br>"
                 "Nb couverts: <b>%d</b>"
                 "    (moy. %.2f / max. %d)<br>"
                 "TM Resto: <b>%.2f</b>"
                 "    (moy. %.2f / max. %.2f<br>"
                 "<br>"
                 "CA Bar: <b>%.2f</b>"
                 "    (moy. %.2f / max. %.2f)<br>"
                 "TM Bar: <b>%.2f</b>"
                 "    (moy. %.2f / max. %.2f)<br>"
                 "<br>"
                 "<br>"
                 "<b>%s</><br>"
                 "-----------------------------------------------------"
                 "-------------------------------------------------<br>"
                 "CA TTC: %.2f<br>"
                 "Nb factures: %d<br>"
                 "<br>"
                 "CA Resto: %.2f<br>"
                 "Nb couverts: %d<br>"
                 "TM Resto: %.2f<br>"
                 "<br>"
                 "CA Bar: %.2f<br>"
                 "TM Bar: %.2f<br>"
                 % (RAPPORT_DATE.strftime("  %A %d %B %Y  "),
                    stats.get_data("ca", RAPPORT_DATE),
                    stats.get_avg("ca"),
                    stats.get_max("ca"),
                    stats.get_data("nb_factures", RAPPORT_DATE),
                    stats.get_avg("nb_factures"),
                    stats.get_max("nb_factures"),
                    stats.get_data("ca_resto", RAPPORT_DATE),
                    stats.get_avg("ca_resto"),
                    stats.get_max("ca_resto"),
                    stats.get_data("nb_couverts", RAPPORT_DATE),
                    stats.get_avg("nb_couverts"),
                    stats.get_max("nb_couverts"),
                    stats.get_data("tm_resto", RAPPORT_DATE),
                    stats.get_avg("tm_resto"),
                    stats.get_max("tm_resto"),
                    stats.get_data("ca_bar", RAPPORT_DATE),
                    stats.get_avg("ca_bar"),
                    stats.get_max("ca_bar"),
                    stats.get_data("tm_bar", RAPPORT_DATE),
                    stats.get_avg("tm_bar"),
                    stats.get_max("tm_bar"),
                    last.strftime("  %A %d %B %Y  "),
                    stats.get_data("ca", last),
                    stats.get_data("nb_factures", last),
                    stats.get_data("ca_resto", last),
                    stats.get_data("nb_couverts", last),
                    stats.get_data("tm_resto", last),
                    stats.get_data("ca_bar", last), 
                    stats.get_data("tm_bar", last),
                )
    )
    en.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    en.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    en.show()
    fr_stats.content_set(en)

    notify.show()

def create_t_choix_frame():
    """Creation d'avance du panneau de choix de table"""

    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_TOP_LEFT)

    main = elementary.Table(win)
#    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    main.show()
    notify.content_set(main)

    x = 0
    for zone in Zone.objects.order_by("-nom").iterator():
        fr = elementary.Frame(win)
        fr.label_set(zone.nom)
        fr.show()
        main.pack(fr, x, 0, 1, 3)

        tb = elementary.Table(win)
        tb.show()
        fr.content_set(tb)

        ite = Table.objects.filter(zone=zone).iterator()
        count = Table.objects.filter(zone=zone).count()
        nb_ligne = 8
        nb_colonne = count / nb_ligne
        if (count % nb_ligne) != 0:
            nb_colonne += 1
        for i in xrange(nb_colonne):
            for j in xrange(nb_ligne):
                bt = elementary.Button(win)
                try:
                    t = ite.next()
                    bt.label_set("           %s           " % t.nom)
                    bt.callback_clicked_add(t_clicked, t, notify)
                except StopIteration:
                    bt.label_set(" ")
                bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
                bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
                bt.show()
                tb.pack(bt, i, j, 1, 1)
        x += 1
    notify.hide()
    return notify

def create_c_choix_frame():
    """Creation d'avance du panneau du nombre de couverts"""

    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_TOP_LEFT)

    fr = elementary.Frame(win)
#    fr.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
#    fr.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fr.label_set("Sélection du nombre de couverts")
    fr.show()

    notify.content_set(fr)
    tb = elementary.Table(win)
    #tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    tb.homogenous_set(True)
    tb.show()
    fr.content_set(tb)

    for i in xrange(5):
        for j in xrange(10):
            bt = elementary.Button(win)
            nb = str(i*10 + j)
            bt.label_set("            %s            "  % nb)
            bt.callback_clicked_add(f_couverts_change, nb, notify)
            bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
            bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
            bt.show()
            tb.pack(bt, i, j, 1, 1)

    notify.hide()
    return notify

def create_notify_vendu():
    """Creation d'avance des panneaux de choix des sous produits"""
    global win, NOTIFY_VENDU

    NOTIFY_VENDU = {}
    for produit in Produit.objects.filter(actif=True).exclude( \
                                categories_ok__isnull=True).iterator():
        NOTIFY_VENDU[produit.id] = {}
        for categorie in produit.categories_ok.iterator():
            # on cree un panneau pour chaque categorie
            notify = elementary.Notify(win)
            notify.repeat_events_set(False)
            notify.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

            fr = elementary.Frame(win)
            fr.label_set("%s : choix de %s" % (produit.nom, categorie.nom))
            fr.show()
            notify.content_set(fr)

            # la box horizontale
            box = elementary.Box(win)
            box.size_hint_weight_set(evas.EVAS_HINT_EXPAND,
                                     evas.EVAS_HINT_EXPAND)
            box.horizontal_set(True)
            box.show()
            fr.content_set(box)

            # liste des produits authorises
            for sub in produit.produits_ok.filter(actif=True, \
                                        categorie=categorie).iterator():
                bt = elementary.Button(win)
                bt.label_set(sub.nom)
                bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
                bt.size_hint_align_set(evas.EVAS_HINT_FILL,
                                       evas.EVAS_HINT_FILL)
                bt.callback_clicked_add(p_sub_clicked, notify, sub)
                if os.path.isfile("images/couleurs/%s.png" \
                                  % categorie.couleur.id):
                    ic = elementary.Icon(win)
                    ic.file_set("images/couleurs/%s.png" \
                                % categorie.couleur.id)
                    ic.scale_set(0, 0)
                    ic.show()
                    bt.icon_set(ic)
                bt.show()
                box.pack_end(bt)
            NOTIFY_VENDU[produit.id][categorie.id] = notify

    notify.hide()

def f_show():
    """Affiche la facture courante"""
    global F_SOLDEE, F_NON_SOLDEE, F_INDEX, F_LISTE, f_label, f_stats, \
        F_COUVERTS, F_ETAT, F_TABLE, F_LISTE_PRODUIT_COURANT, \
        F_LISTE_PRODUITS, F_PAYER, F_TOTAL, F_TVA, CPT_TOTAL, \
        CPT_RESTE, F_LISTE_PAIEMENTS
    if len(F_LISTE):
        f = F_LISTE[F_INDEX]
        f_label.label_set("%s" % f.show())
        if f.couverts == 1:
            F_COUVERTS.label_set("1 couvert")
        elif not f.couverts:
            F_COUVERTS.label_set("0 couvert")
        else:
            F_COUVERTS.label_set("%d couverts" % f.couverts)
        if f.table:
            F_TABLE.label_set(f.table.nom)
        else:
            F_TABLE.label_set("T--")
        F_TVA.label_set("TVA 5.5%%: % 5.2f € || TVA 19.6%%: % 5.2f €" \
                        % (f.getTvaAlcool(), f.getTvaNormal()))
        # MAJ de la liste des produits
        F_LISTE_PRODUIT_COURANT = None

        F_LISTE_PRODUITS.clear()
        for vendu in f.produits.order_by(\
                            'produit__categorie__priorite').iterator():
            F_LISTE_PRODUITS.item_append(ITC_PRODUIT,
                                         vendu,
                                         func=f_produit_select)
            for sous_produit in vendu.contient.order_by(\
                            'produit__categorie__priorite').iterator():
                F_LISTE_PRODUITS.item_append(ITC_SOUS_PRODUIT, sous_produit)
        # MAJ du total
        show_compteur(CPT_TOTAL, f.get_montant())
        # MAJ de la liste des paiements
        F_LISTE_PAIEMENT_COURANT = None
        F_LISTE_PAIEMENTS.clear()
        for paiement in f.paiements.iterator():
            F_LISTE_PAIEMENTS.item_append(ITC_PRODUIT, paiement,
                                          func=f_paiement_select)
        # MAJ du montant non paye
        show_compteur(CPT_RESTE, f.restant_a_payer)
    else:
        f_label.label_set("Aucune facture en cours.")
    f_stats.label_set("%d non soldées / %d soldées" % (F_NON_SOLDEE,
                                                       F_SOLDEE))

def f_valeur_tr_clicked(bt):
    """On affecte la valeur de la calculatrice a la valeur du ticket.
    """
    global BT_TR, VALEUR_TR, NOMBRES_VALEUR
    if NOMBRES_VALEUR:
        VALEUR_TR = NOMBRES_VALEUR
        BT_TR.label_set("%.2f €" % VALEUR_TR)
        nombres_raz(None)

def f_valeur_ancv_clicked(bt):
    """On affecte la valeur de la calculatrice a la valeur du ticket.
    """
    global BT_ANCV, VALEUR_ANCV, NOMBRES_VALEUR
    if NOMBRES_VALEUR:
        VALEUR_ANCV = NOMBRES_VALEUR
        BT_ANCV.label_set("%.2f €" % VALEUR_ANCV)
        nombres_raz(None)

def create_paiements():
    global VALEUR_ANCV, VALEUR_TR, win, BT_TR, BT_ANCV

    fr = elementary.Frame(win)
    fr.label_set("Mode de paiements")
    fr.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fr.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fr.show()

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    tb.show()
    fr.content_set(tb)

    p = PaiementType.objects.get(nom='Tic. Resto.')
    bt = elementary.Button(win)
    bt.label_set(p.nom)
    bt.callback_clicked_add(f_paiement_tr_clicked, p)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 0, 0, 1, 1)

    bt = elementary.Button(win)
    bt.label_set("%.2f €" % VALEUR_TR)
    bt.callback_clicked_add(f_valeur_tr_clicked)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 1, 0, 1, 1)
    BT_TR = bt

#    p = PaiementType.objects.get(nom='AMEX')
#    bt = elementary.Button(win)
#    bt.label_set(p.nom)
#    bt.callback_clicked_add(f_paiement_clicked, p)
#    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
#    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
#    bt.show()
#    tb.pack(bt, 2, 0, 1, 1)

    p = PaiementType.objects.get(nom='Cheque')
    bt = elementary.Button(win)
    bt.label_set(p.nom)
    bt.callback_clicked_add(f_paiement_clicked, p)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 3, 0, 1, 1)

    p = PaiementType.objects.get(nom='ANCV')
    bt = elementary.Button(win)
    bt.label_set(p.nom)
    bt.callback_clicked_add(f_paiement_ancv_clicked, p)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 0, 1, 1, 1)

    bt = elementary.Button(win)
    bt.label_set("%.2f €" % VALEUR_ANCV)
    bt.callback_clicked_add(f_valeur_ancv_clicked)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 1, 1, 1, 1)
    BT_ANCV = bt

    p = PaiementType.objects.get(nom='CB')
    bt = elementary.Button(win)
    bt.label_set(p.nom)
    bt.callback_clicked_add(f_paiement_clicked, p)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 2, 0, 1, 1)
#    tb.pack(bt, 2, 1, 1, 1)

    p = PaiementType.objects.get(nom='Espece')
    bt = elementary.Button(win)
    bt.label_set(p.nom)
    bt.callback_clicked_add(f_paiement_clicked, p)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 2, 1, 2, 1)

    return fr

def create_produits(id_categorie):
    c = Categorie.objects.get(id=id_categorie)

    fr = elementary.Frame(win)
    fr.label_set(c.nom)
    fr.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fr.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fr.show()

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    tb.homogenous_set(True)
    tb.show()
    fr.content_set(tb)

    ite = Produit.objects.filter(categorie=c,actif=True).iterator()
    for i in xrange(3):
        for j in xrange(8):
            bt = elementary.Button(win)
            try:
                p = ite.next()
                # si le nom du produit est trop long
                # alors la fenetre est trop large
                bt.label_set(p.nom[:16])
                bt.callback_clicked_add(p_clicked, p)
            except StopIteration:
                bt.label_set(" ")
            if os.path.isfile("images/couleurs/%s.png" % c.couleur.id):
                ic = elementary.Icon(win)
                ic.file_set("images/couleurs/%s.png" % c.couleur.id)
                ic.scale_set(0, 0)
                ic.show()
                bt.icon_set(ic)
            bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, \
                                    evas.EVAS_HINT_EXPAND)
            bt.size_hint_align_set(evas.EVAS_HINT_FILL, \
                                   evas.EVAS_HINT_FILL)
            bt.show()
            tb.pack(bt, i, j, 1, 1)

    fr.hide()
    return fr

def nombres_clicked(bt, nouveau):
    """chiffre peut etre 0..9 de type str"""
    global NOMBRES_VALEUR, NOMBRES_COEF, CPT_CAL
    logging.debug("valeur actuelle: %s / chiffre selectionne: %s / coef: %s" \
        % (NOMBRES_VALEUR,nouveau,NOMBRES_COEF))
    chiffre = Decimal(nouveau)
    if len("%.2f" % NOMBRES_VALEUR) < 8 \
            or NOMBRES_COEF == Decimal(-1) or NOMBRES_COEF == Decimal(-2):
        if NOMBRES_COEF == Decimal(0):
            NOMBRES_VALEUR = NOMBRES_VALEUR*10 + chiffre
        else:
            NOMBRES_VALEUR = NOMBRES_VALEUR + chiffre * 10 ** NOMBRES_COEF
            NOMBRES_COEF -= 1
        show_compteur(CPT_CAL, NOMBRES_VALEUR)
    else:
        notify_show("Le nombre est trop grand !")

def nombres_dot(bt):
    """prise en compte du point"""
    global NOMBRES_COEF
    NOMBRES_COEF = Decimal("-1.00")

def nombres_raz(bt):
    """chiffre peut etre 0..9 ou ."""
    logging.debug("RAZ partie nombres")
    global NOMBRES_COEF, NOMBRES_VALEUR, CPT_CAL
    NOMBRES_VALEUR = Decimal("0.00")
    NOMBRES_COEF = Decimal("0.00")
    show_compteur(CPT_CAL, NOMBRES_VALEUR)

def t_clicked(bt, table, notify):
    """Une table est selectionnee."""
    logging.debug("table selectionne: %s" % table.nom)
    global F_LISTE, F_INDEX
    notify.hide()
    F_LISTE[F_INDEX].set_table(table)
    f_update_liste()
    f_show()

def p_sub_clicked(bt, notify, produit):
    """un sous produit pour un menu a ete selectionne"""
    global F_LISTE, F_INDEX, VENDU_COURANT, NOTIFY_VENDU
    # on ajoute le produit
#    vendu = ProduitVendu(produit=produit, facture=F_LISTE[F_INDEX])
    vendu = ProduitVendu(produit=produit)
    vendu.save()
    VENDU_COURANT.contient.add(vendu)
    categorie = VENDU_COURANT.getFreeCategorie()
    notify.hide()
    if categorie:
        # il en reste
        NOTIFY_VENDU[VENDU_COURANT.produit.id][categorie.id].show()
    else:
        VENDU_COURANT.save()
        F_LISTE[F_INDEX].add(VENDU_COURANT)
        VENDU_COURANT = None
        f_show()

def f_paiement_clicked(bt, type_paiement):
    """type_paiement est un TypePaiement"""
    logging.debug("paiement selectionne de type: %s" % type_paiement.nom)
    global F_LISTE, F_INDEX, NOMBRES_VALEUR
    F_LISTE[F_INDEX].ajout_paiement(type_paiement, NOMBRES_VALEUR)
    nombres_raz(None)
    f_show()

def f_paiement_ancv_clicked(bt, type_paiement):
    """type_paiement est un TypePaiement"""
    logging.debug("paiement selectionne de type: %s" % type_paiement.nom)
    global F_LISTE, F_INDEX, VALEUR_ANCV, NOMBRES_VALEUR
    F_LISTE[F_INDEX].ajout_paiement(type_paiement, NOMBRES_VALEUR, VALEUR_ANCV)
    nombres_raz(None)
    f_show()

def f_paiement_tr_clicked(bt, type_paiement):
    """type_paiement est un TypePaiement"""
    logging.debug("paiement selectionne de type: %s" % type_paiement.nom)
    global F_LISTE, F_INDEX, VALEUR_TR, NOMBRES_VALEUR
    F_LISTE[F_INDEX].ajout_paiement(type_paiement, NOMBRES_VALEUR, VALEUR_TR)
    nombres_raz(None)
    f_show()

def p_clicked(bt, produit):
    """Handler lorsqu'un produit est selectionne.
    Si un nombre a ete renseigne, alors X produits sont ajoutes
    """
    logging.debug("produit selectionne: %s" % produit.nom)
    global F_LISTE, F_INDEX, NOTIFY_VENDU, VENDU_COURANT, NOMBRES_VALEUR
    if NOMBRES_VALEUR:
        nb = int(NOMBRES_VALEUR)
        nombres_raz(None)
    else:
        nb = 1
    if produit.est_un_menu():
        # il y a des sous produits a selectionner ?
        # on cree le produit de la vente
        VENDU_COURANT = ProduitVendu()
        #VENDU_COURANT.facture = F_LISTE[F_INDEX]
        VENDU_COURANT.produit = produit
        VENDU_COURANT.save()
        # dans ce cas on ignore le nombre de produits nb
        # on recupere la premiere categorie libre
        categorie = VENDU_COURANT.getFreeCategorie()
        NOTIFY_VENDU[VENDU_COURANT.produit.id][categorie.id].show()
        # la suite est effectuee par p_sub_clicked
    else:
        for i in xrange(nb):
            vendu = ProduitVendu()
            #vendu.facture = F_LISTE[F_INDEX]
            vendu.produit = produit
            vendu.save()
            F_LISTE[F_INDEX].add(vendu)
            f_show()

def m_label_update():
    global PB_LABEL, PB, MPD_CLIENT

    try:
        currentsong = MPD_CLIENT.currentsong()
        time_total = float(MPD_CLIENT.status()['time'].split(":")[1])
        time_current = float(MPD_CLIENT.status()['time'].split(":")[0])
        # 0.0 est le min et 1.0 le max
        PB.value_set(time_current/time_total)
        try:
            msg = currentsong['artist']+" / "+currentsong['album'] \
                                            +" / "+currentsong['title']
        except:
            msg = currentsong['file']
        if len(msg) > 63:
            msg = "%s..." % msg[:60]
        msg += " [%d/%d]" % (int(currentsong['pos'])+1, \
                                            len(MPD_CLIENT.playlist()))
    except:
        msg = "Aucune information disponible"
        PB.value_set(0.0)
        try:
            MPD_CLIENT.connect("127.0.0.1", 6600)
        except:
            msg = "Le son ne fonctionne pas (MPD off)"

    PB_LABEL.label_set(msg)

def music_update():
    """Mets a jour le bar de progression pour le son ainsi que le titre"""
    m_label_update()
    ecore.timer_add(5.0, music_update)

def f_menage():
    """On parcours les factures en cours pour trouver et enlever les
    factures soldees"""
    global F_LISTE, F_INDEX, F_SOLDEE, F_NON_SOLDEE
    index_change = False
    for f in F_LISTE:
        if f.est_soldee():
            logging.debug("facture soldee: %s" % f)
            F_LISTE.remove(f)
            index_change = True
            F_SOLDEE += 1
            F_NON_SOLDEE -= 1
            # si besoin on essaye de trouver le nombre de couverts
            if f.couverts == 0:
                guest = f.guest_couverts()
                if guest != 0:
                    f.couverts = guest
                    f.save()
    if not len(F_LISTE):
        logging.debug("liste des factures vides, on ajoute une nouvelle")
        f = Facture()
        f.save()
        F_LISTE.append(f)
        F_INDEX = 0
        F_NON_SOLDEE += 1
        f_update_liste()
    else:
        if index_change:
            # la liste a change donc on repart a 0
            F_INDEX = 0
            f_update_liste()

def f_etat_change(bt, item, etat):
    """Changement d'etat"""
    logging.debug("a faire !")
    bt.label_set(etat.nom)

def f_couverts_change(bt, nb, notify):
    global F_INDEX, F_LISTE
    F_LISTE[F_INDEX].set_couverts(int(nb))
    f_show()
    notify.hide()

def f_new(bt):
    """Si besoin on cree une nouvelle facture
    Sinon on remet le focus sur une facture vierge en mettant a jour la date
    """
    f_menage()
    global F_LISTE, F_INDEX, F_NON_SOLDEE
    vierge = False
    for i in xrange(len(F_LISTE)):
        if F_LISTE[i].est_vierge():
            vierge = True
            index = i
    if not vierge:
        logging.debug("pas de facture vierge, on en cree une")
        f = Facture()
        f.save()
        F_LISTE.append(f)
        F_INDEX = len(F_LISTE)-1
        F_NON_SOLDEE += 1
        f_update_liste()
    else:
        logging.debug("on se positionne sur la facture vierge")
        F_INDEX = index
    categorie_clicked(None, settings.POSSUM_DEFAULT_ID_CATEGORIE)
    f_show()

def f_prev(bt):
    """on parcours la liste des factures vers la gauche"""
    f_menage()
    global F_LISTE, F_INDEX
    if len(F_LISTE) > 1:
        if F_INDEX == 0:
            # on prend le dernier
            F_INDEX = len(F_LISTE)-1
        else:
            F_INDEX -= 1
    categorie_clicked(None, settings.POSSUM_DEFAULT_ID_CATEGORIE)
    f_show()

def f_next(bt):
    """on parcours la liste des factures vers la droite"""
    f_menage()
    global F_LISTE, F_INDEX
    if len(F_LISTE) > 1:
        if F_INDEX == len(F_LISTE)-1:
            # on prend le premier
            F_INDEX = 0
        else:
            F_INDEX += 1
    categorie_clicked(None, settings.POSSUM_DEFAULT_ID_CATEGORIE)
    f_show()

def categorie_clicked(bt, id):
    """id est un ID de categorie a afficher"""
    global FRAMES_PRODUITS
    logging.debug("changement de categorie: %d" % id)
    if FRAMES_PRODUITS["actif"] is not None:
        FRAMES_PRODUITS["actif"].hide()
    FRAMES_PRODUITS[id].show()
    FRAMES_PRODUITS["actif"] = FRAMES_PRODUITS[id]

def create_categories():
    fr = elementary.Frame(win)
    fr.label_set("Catégories")
    fr.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fr.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fr.show()

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    tb.homogenous_set(True)
    tb.show()
    fr.content_set(tb)

    liste = Categorie.objects.all()
    limit = liste.count()
    nb_ligne = (limit / 2)
    if (limit % 2) == 1:
        nb_ligne += 1
    ite = liste.iterator()
    for i in xrange(2):
        for j in xrange(nb_ligne):
            bt = elementary.Button(win)
            try:
                c = ite.next()
                bt.label_set(c.nom[:13])
                bt.callback_clicked_add(categorie_clicked, c.id)
                if os.path.isfile("images/couleurs/%s.png" % c.couleur.id):
                    ic = elementary.Icon(win)
                    ic.file_set("images/couleurs/%s.png" % c.couleur.id)
                    ic.scale_set(0, 0)
                    ic.show()
                    bt.icon_set(ic)
            except StopIteration:
                bt.label_set(" ")
            bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, \
                                    evas.EVAS_HINT_EXPAND)
            bt.size_hint_align_set(evas.EVAS_HINT_FILL, \
                                   evas.EVAS_HINT_FILL)
            bt.show()
            tb.pack(bt, i, j, 1, 1)

    return fr

def create_info():
    fr = elementary.Frame(win)
    fr.label_set("Informations")
    fr.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fr.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fr.show()

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fr.content_set(tb)
    tb.show()

    ic = elementary.Icon(win)
    ic.file_set("images/bandeau-128.png")
#    ic.size_hint_aspect_set(evas.EVAS_ASPECT_CONTROL_VERTICAL, 1, 1)
    ic.on_mouse_down_add(show_on_event, create_admin_access())
    ic.scale_set(0, 0)
    ic.show()
    tb.pack(ic, 0, 0, 3, 1)

    l = elementary.Label(win)
    l.label_set("version %s" % settings.VERSION)
    l.show()
    tb.pack(l, 0, 1, 3, 1)

    sp = elementary.Separator(win)
#    sp.horizontal_set(True)
    sp.show()
    tb.pack(sp, 3, 0, 1, 2)

    ck = elementary.Clock(win)
    ck.show()
    tb.pack(ck, 4, 0, 1, 1)

    l = elementary.Label(win)
    l.label_set(datetime.today().strftime("%A %d %B %Y"))
    l.show()
    tb.pack(l, 4, 1, 1, 1)

    sp = elementary.Separator(win)
    sp.show()
    tb.pack(sp, 5, 0, 1, 2)

    ic = elementary.Icon(win)
    ic.file_set("icons/saintsaens.png")
    ic.scale_set(0, 0)
    ic.on_mouse_down_add(show_on_event, create_admin_access())
    ic.show()
    tb.pack(ic, 6, 0, 1, 1)

    l = elementary.Label(win)
    l.label_set("Le Saint Saëns")
    l.show()
    tb.pack(l, 6, 1, 1, 1)

    return fr

def create_music():
    global PB, PB_LABEL

    fr = elementary.Frame(win)
    fr.label_set("Musique")
    fr.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fr.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fr.show()

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fr.content_set(tb)
    tb.show()

    PB = elementary.Progressbar(win)
    PB.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    PB.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    PB.show()
    tb.pack(PB, 0, 0, 4, 1)

    PB_LABEL = elementary.Label(win)
    PB_LABEL.label_set("Le titre de la chanson")
    PB_LABEL.show()
    tb.pack(PB_LABEL, 0, 1, 4, 1)

    bt = elementary.Button(win)
    bt.label_set("Enlever")
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.callback_clicked_add(m_remove)
    bt.show()
    tb.pack(bt, 0, 2, 1, 1)

    bt = elementary.Button(win)
    bt.label_set("<")
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.callback_clicked_add(m_prev)
    bt.show()
    tb.pack(bt, 1, 2, 1, 1)

    bt = elementary.Button(win)
    bt.label_set("Play")
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.callback_clicked_add(m_play)
    bt.show()
    tb.pack(bt, 2, 2, 1, 1)

    bt = elementary.Button(win)
    bt.label_set(">")
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.callback_clicked_add(m_next)

    bt.show()
    tb.pack(bt, 3, 2, 1, 1)

    # 1er lancement pour armer le timer
    music_update()
    return fr

def m_next(bt):
    global MPD_CLIENT
    try:
        MPD_CLIENT.next()
        self.m_label_update()
    except:
        logging.warning("probleme avec MPD")

def m_prev(bt):
    global MPD_CLIENT
    try:
        MPD_CLIENT.previous()
        self.m_label_update()
    except:
        logging.warning("problem")

def m_play(bt):
    global MPD_CLIENT
    try:
        MPD_CLIENT.clear()
        MPD_CLIENT.load("toute_la_musique")
        MPD_CLIENT.play()
        self.m_label_update()
    except:
        logging.warning("[mpd] play doesn't work")

def m_remove(bt):
    global MPD_CLIENT
    currentpos = MPD_CLIENT.currentsong()['pos']
    a_file = MPD_CLIENT.currentsong()['file']
    try:
        logging.debug("suppression du fichier %s a la position: %s" % \
                                                (a_file, currentpos))
        MPD_CLIENT.playlistdelete("toute_la_musique", currentpos)
        m_next(None)
    except:
        logging.warning("erreur lors de la suppression de %s a la "\
                                "position: %s" % (a_file, currentpos))

def show(bt, notify):
    """Permet d'afficher un panneau."""
    notify.show()

def show_on_event(bt, event, notify):
    """Permet d'afficher un panneau.
    event est le type d'evenement: clic gauche, clic droit, ...
    """
    notify.show()

def hide(bt, notify):
    notify.hide()

def notify_show(message):
    global win
    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    #notify.timeout_set(5)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    bx = elementary.Box(win)
    bx.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    #bx.horizontal_set(True)
    notify.content_set(bx)
    bx.show()

    lb = elementary.Label(win)
    lb.label_set(message)
    bx.pack_end(lb)
    lb.show()

    bt = elementary.Button(win)
    bt.label_set("Ok")
    bt.callback_clicked_add(hide, notify)
    bx.pack_end(bt)
    bt.show()
    notify.show()

def f_select(bt, item, numero_index):
    """Une facture est selectionnee, on l'active"""
    global F_LISTE, F_INDEX
    F_INDEX = numero_index
    f_show()

def f_update_liste():
    """Mets a jour le menu deroulant pour la selection d'une facture."""
    global f_label, F_INDEX, F_LISTE
    f_label.clear()
    for i in xrange(len(F_LISTE)):
        f_label.item_add(F_LISTE[i].show(), callback=f_select, \
                                                numero_index=i)
    f_label.label_set(F_LISTE[F_INDEX].show())

def create_facture():
    global f_label, f_stats, F_COUVERTS, F_ETAT, F_TABLE, \
        F_LISTE_PRODUITS, F_PAYER, F_TOTAL, F_LISTE_PAIEMENTS, F_TVA, \
        CPT_RESTE, CPT_TOTAL

    fr = elementary.Frame(win)
    fr.label_set("Facture")
    # definition de l'espace disponible (hori, vert)
    fr.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    # comment on utilise l'espace attribue (on remplit tout ou pas) (hori, vert)
    fr.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fr.show()

    tb = elementary.Table(win)
    tb.show()
    fr.content_set(tb)

    bt = elementary.Button(win)
    bt.label_set("<")
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.callback_clicked_add(f_prev)
    bt.show()
    tb.pack(bt, 0, 0, 1, 1)

    f_label = elementary.Hoversel(win)
    f_label.hover_parent_set(win)
    f_label.label_set("T-- --:--:-- --/--/--")
    f_label.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    f_label.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    f_label.show()
    tb.pack(f_label, 1, 0, 4, 1)

    bt = elementary.Button(win)
    bt.label_set(">")
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.callback_clicked_add(f_next)
    bt.show()
    tb.pack(bt, 5, 0, 1, 1)

    f_stats = elementary.Label(win)
    f_stats.label_set("? non soldées / ? soldées")
    f_stats.show()
    tb.pack(f_stats, 0, 1, 4, 1)

    bt = elementary.Button(win)
    bt.label_set("Nouvelle")
    bt.callback_clicked_add(f_new)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 4, 1, 2, 1)

    F_TABLE = elementary.Button(win)
    F_TABLE.label_set("T--")
    F_TABLE.callback_clicked_add(show, create_t_choix_frame())
    F_TABLE.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    F_TABLE.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    F_TABLE.show()
    tb.pack(F_TABLE, 0, 2, 2, 1)

    F_COUVERTS = elementary.Button(win)
    F_COUVERTS.label_set("0 couvert")
    F_COUVERTS.callback_clicked_add(show, create_c_choix_frame())
    F_COUVERTS.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    F_COUVERTS.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

    F_COUVERTS.show()
    tb.pack(F_COUVERTS, 2, 2, 2, 1)

    F_ETAT = elementary.Hoversel(win)
    F_ETAT.hover_parent_set(win)
    F_ETAT.label_set("État")
    for e in Etat.objects.iterator():
        F_ETAT.item_add(e.nom, callback=f_etat_change, etat=e)
    F_ETAT.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    F_ETAT.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    F_ETAT.show()
    tb.pack(F_ETAT, 4, 2, 2, 1)

    F_LISTE_PRODUITS = elementary.Genlist(win)
#    F_LISTE_PRODUITS = elementary.List(win)Genlist
    F_LISTE_PRODUITS.size_hint_weight_set(evas.EVAS_HINT_EXPAND, \
                                          evas.EVAS_HINT_EXPAND)
    F_LISTE_PRODUITS.size_hint_align_set(evas.EVAS_HINT_FILL, \
                                         evas.EVAS_HINT_FILL)
#    F_LISTE_PRODUITS.mode_set(elementary.ELM_LIST_LIMIT)
#    F_LISTE_PRODUITS.lower()
#    ic2 = elementary.Icon(win)
#    ic2.standard_set("remove")
#    ic2.scale_set(0, 0)
#    it2 = li.item_append("How", None, ic2)

#    if settings.DEBUG:
#        F_LISTE_PRODUITS.item_append("1 café                   2.30")
#    F_LISTE_PRODUITS.go()
    tb.pack(F_LISTE_PRODUITS, 0, 3, 6, 8)
    F_LISTE_PRODUITS.show()

    l = elementary.Label(win)
    l.label_set("Total (€):")
    l.show()
    tb.pack(l, 0, 11, 2, 1)

    table = create_compteur(CPT_TOTAL)
    tb.pack(table, 2, 11, 4, 1)

#    box = elementary.Box(win)
#    box.horizontal_set(True)
#    box.show()
#    affiche_nombre(box, 345)
#    F_TOTAL = box
#    tb.pack(box, 2, 11, 4, 1)

    bt = elementary.Button(win)
    bt.label_set("Tout supprimer")
    bt.callback_clicked_add(f_enlever_tous_les_produits)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 0, 12, 3, 1)

    bt = elementary.Button(win)
    bt.label_set("Enlever")
    bt.callback_clicked_add(f_enlever_produit)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 3, 12, 3, 1)

    F_TVA = elementary.Label(win)
    F_TVA.label_set("- TVA -")
    F_TVA.show()
    tb.pack(F_TVA, 0, 13, 6, 1)

    sp = elementary.Separator(win)
    sp.horizontal_set(True)
    sp.show()
    tb.pack(sp, 0, 14, 6, 1)

    F_LISTE_PAIEMENTS = elementary.Genlist(win)
#    F_LISTE_PAIEMENTS = elementary.List(win)
    F_LISTE_PAIEMENTS.size_hint_align_set(evas.EVAS_HINT_FILL, \
                                                    evas.EVAS_HINT_FILL)
    F_LISTE_PAIEMENTS.size_hint_weight_set(evas.EVAS_HINT_EXPAND, \
                                                evas.EVAS_HINT_EXPAND)
#    if settings.DEBUG:
#        F_LISTE_PAIEMENTS.item_append("CB               20.00")
#        F_LISTE_PAIEMENTS.item_append("Chéque            2.30")
#    F_LISTE_PAIEMENTS.go()
    tb.pack(F_LISTE_PAIEMENTS, 0, 15, 6, 2)
    F_LISTE_PAIEMENTS.show()

    l = elementary.Label(win)
    l.label_set("Reste (€):")
    l.show()
    tb.pack(l, 0, 17, 2, 1)

    table = create_compteur(CPT_RESTE)
    tb.pack(table, 2, 17, 4, 1)

#    box = elementary.Box(win)
#    box.horizontal_set(True)
#    box.show()
#    affiche_nombre(box, 12)
#    F_PAYER = box
#    tb.pack(box, 2, 17, 4, 1)

    bt = elementary.Button(win)
    bt.label_set("Tout supprimer")
    bt.callback_clicked_add(f_enlever_tous_les_paiements)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_EXPAND)
    bt.show()
    tb.pack(bt, 0, 18, 3, 1)

    bt = elementary.Button(win)
    bt.label_set("Enlever")
    bt.callback_clicked_add(f_enlever_paiement)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_EXPAND)
    bt.show()
    tb.pack(bt, 3, 18, 3, 1)

    f_update_liste()
    f_show()

    return fr

def show_compteur(CPT, nombre):
    global COMPTEUR_CAL, COMPTEUR_TOTAL, \
        COMPTEUR_RESTE, CPT_CAL, CPT_TOTAL, CPT_RESTE
    nb_chiffre = 8
    try:
        nb = "%08.2f" % nombre
    except:
#        nb = "00000000"
        logging.warning("nombre non recuperable")
        nb = "00000.00"

    if CPT == CPT_CAL:
        compteur = COMPTEUR_CAL
    elif CPT == CPT_TOTAL:
        compteur = COMPTEUR_TOTAL
    elif CPT == CPT_RESTE:
        compteur = COMPTEUR_RESTE
    else:
        logging.warning("CPT inconnu: %d" % CPT)
        return

    ancien = compteur['valeur']
    compteur['valeur'] = nb
    #logging.debug("ancienne valeur: %s" % ancien)
    #logging.debug("nouvelle valeur: %s" % compteur['valeur'])

    for case in xrange(nb_chiffre):
        new = compteur['valeur'][case]
        if new not in "0123456789.":
            new = "0"
        if ancien[case] != new:
            # on cache l'ancien et montre le nouveau
            compteur[case][ancien[case]].hide()
            compteur[case][new].show()

def create_compteur(CPT):
    """Cree une table et tous les IC qui vont bien

    La structure de données d'un compteur ressemble à:

    - compteur['valeur'] : la valeur affichée
    - compteur[0] : la case de gauche
    - compteur[1] : la case suivante
    - ...

    Chaque compteur[x] avec x de 0 à nb_chiffre contient toutes les
    ic affichables.

    """
    global win, COMPTEUR_CAL, COMPTEUR_TOTAL, \
        COMPTEUR_RESTE, CPT_CAL, CPT_TOTAL, CPT_RESTE
    nb_chiffre = 8

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    tb.homogenous_set(True)
    tb.show()

    compteur = {}
    compteur['valeur'] = "00000.00"

    for case in xrange(nb_chiffre):
        # pour chaque case afficher, on prepare toutes les possibilites
        compteur[case] = {}
        liste = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
        for i in liste:
            ic = elementary.Icon(win)
            ic.file_set("%s/digit_%s.png" \
                        % (settings.POSSUM_IMAGES_PATH, i))
            ic.scale_set(0, 0)
            ic.show()
            tb.pack(ic, case, 0, 1, 1)
            compteur[case][i] = ic
            if i != "0":
                ic.hide()
        # la virgule
        if case == nb_chiffre - 3:
            compteur[case]["0"].hide()
            compteur[case]["."].show()

    if CPT == CPT_CAL:
        COMPTEUR_CAL = compteur
    elif CPT == CPT_TOTAL:
        COMPTEUR_TOTAL = compteur
    elif CPT == CPT_RESTE:
        COMPTEUR_RESTE = compteur
    else:
        logging.warning("CPT inconnu: %d" % CPT)

    return tb

def create_nombres():
    fr = elementary.Frame(win)
    fr.label_set("Nombres")
    fr.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    fr.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fr.show()

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    tb.homogenous_set(True)
    tb.show()
    fr.content_set(tb)

    global CPT_CAL
    table = create_compteur(CPT_CAL)
    tb.pack(table, 0, 0, 3, 1)

    bt = elementary.Button(win)
    bt.label_set("7")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 0, 1, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("8")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 1, 1, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("9")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 2, 1, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("4")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 0, 2, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("5")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 1, 2, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("6")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 2, 2, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("1")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 0, 3, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("2")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 1, 3, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("3")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 2, 3, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("0")
    bt.callback_clicked_add(nombres_clicked, bt.label)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 0, 4, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set(".")
    bt.callback_clicked_add(nombres_dot)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.pack(bt, 1, 4, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("RAZ")
    bt.callback_clicked_add(nombres_raz)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    tb.pack(bt, 2, 4, 1, 1)

    return fr

def f_paiement_select(bt, item, paiement):
    """On enleve un paiement"""
    logging.debug("paiement selectionne dans la facture: %s" % paiement)
    global F_LISTE_PAIEMENT_COURANT
    F_LISTE_PAIEMENT_COURANT = paiement

def f_enlever_tous_les_paiements(bt):
    """Enleve tous les paiements dans la facture courante"""
    global F_LISTE, F_INDEX
    if F_LISTE[F_INDEX].paiements.count():
        F_LISTE[F_INDEX].del_all_paiements()
        f_show()
    else:
        logging.debug("la facture ne contient pas de paiements")

def f_enlever_paiement(bt):
    global F_LISTE, F_INDEX, F_LISTE_PAIEMENT_COURANT
    if F_LISTE_PAIEMENT_COURANT:
        F_LISTE[F_INDEX].del_paiement(F_LISTE_PAIEMENT_COURANT)
        f_show()
    else:
        notify_show("Vous devez d'abord sélectionner un paiement dans "\
                                                        "la facture")

def f_enlever_tous_les_produits(bt):
    """Enleve tous les produits dans la facture courante"""
    global F_LISTE_PRODUITS, F_LISTE, F_INDEX
    if F_LISTE[F_INDEX].produits.count():
        F_LISTE[F_INDEX].del_all_produits()
        f_show()
    else:
        logging.debug("la facture ne contient pas de produits")

def f_produit_select(bt, item, produit):
    """produit est de type ProduitVendu"""
    logging.debug("produit selectionne dans la facture")
    global F_LISTE_PRODUIT_COURANT
    F_LISTE_PRODUIT_COURANT = produit

def f_enlever_produit(bt):
    global F_LISTE, F_INDEX, F_LISTE_PRODUIT_COURANT
    if F_LISTE_PRODUIT_COURANT:
        # F_LISTE_PRODUIT_COURANT doit etre un ProduitVendu
        F_LISTE[F_INDEX].del_produit(F_LISTE_PRODUIT_COURANT)
        f_show()
    else:
        notify_show("Vous devez d'abord sélectionner un produit dans "\
                                                        "la facture")

def afficher_rapport_jour(bt):
    global RAPPORT_DATE
    logging.debug(RAPPORT_DATE)
    rapport = Facture().rapport_jour(RAPPORT_DATE)
    notify_imprimable("Rapport du jour", rapport)

def afficher_rapport_mois(bt):
    """affiche le rapport du mois précédent"""
    global RAPPORT_DATE
    rapport = Facture().rapport_mois(RAPPORT_DATE)
    notify_imprimable("Rapport du mois", rapport)

def imprimer_texte(bt, texte):
    """Imprime le texte
    - bt: lorsque l'impression est appelée à partir d'un bouton
    - texte sous la forme d'une liste de ligne: [ligne1, ligne2, ..]
    """
    try:
        #fd = io.open("/dev/usb/lp0", "w")
        fd = open("/dev/usb/lp0", "w")
        for ligne in texte:
            # on affiche le nombre d'element
            fd.write("%s\n" % ligne)
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\x1D\x56\x01")
        fd.close()
    except IOError:
        logging.warning("Erreur dans l'impression.")
        notify_show("<br>Erreur dans l'impression.<br>")

def imprimer(bt):
    """imprime une facture"""
    global F_INDEX, F_LISTE
    if F_LISTE[F_INDEX].produits.count() == 0:
        notify_show("La facture est vide.")
    else:
        # "/dev/usb/lp0" n'est pas un fichier
        #if not os.path.isfile("/dev/usb/lp0"):
        #    notify_show("L'imprimante n'est pas connectée.")
        #    return
        #else:
        ticket = F_LISTE[F_INDEX].ticket()
        imprimer_texte(bt, ticket)

def create_ihm():
#    global t_choix_frame

    bg = elementary.Background(win)
    win.resize_object_add(bg)
    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bg.show()

    win.autodel_set(True)
    # le conteneur general
    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
#    h.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    tb.show()
    win.resize_object_add(tb)

    create_notify_vendu()

    tb.pack(create_facture(), 0, 0, 2, 15)

    tb.pack(create_music(), 2, 0, 4, 2)
    tb.pack(create_info(), 2, 2, 4, 2)

    for c in Categorie.objects.iterator():
        FRAMES_PRODUITS[c.id] = create_produits(c.id)
        tb.pack(FRAMES_PRODUITS[c.id], 2, 4, 4, 9)
    categorie_clicked(tb, settings.POSSUM_DEFAULT_ID_CATEGORIE)

    tb.pack(create_paiements(), 2, 13, 4, 2)

    tb.pack(create_nombres(), 6, 0, 2, 4)
    tb.pack(create_categories(), 6, 4, 2, 10)

    bt = elementary.Button(win)
    bt.label_set("Imprimer le ticket")
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.callback_clicked_add(imprimer)
    bt.show()
    tb.pack(bt, 6, 14, 2, 1)

    create_admin_panel()

    win.cursor_set(CURSOR)
    win.show()

    elementary.run()
    elementary.shutdown()

if __name__ == "__main__":
    create_ihm()

