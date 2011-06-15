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
# a utiliser sous la forme: utils/convert_sqlite3-to-django.py

#DEBUG = True
DEBUG = False

if DEBUG:
    limit = "limit 2002"
else:
    limit = ""

import sys, os
import datetime
from decimal import Decimal
import progressbar

sys.path.append('/home/pos')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from possum.base.models import Accompagnement, Sauce, Etat, \
    Categorie, Couleur, Cuisson, Facture, Log, LogType, Paiement, \
    PaiementType, Produit, ProduitVendu, Suivi, Table, Zone

debut = datetime.datetime.now()

#print "> nettoyage de la base"
#os.system('su - postgres -c "dropdb possumdb"')
#os.system('su - postgres -c "createdb possumdb --encoding=UTF-8"')
#os.system('rm /home/pos/possum/data/django.db')

print "> creation de la base"
os.system('python manage.py syncdb --noinput > /dev/null')
# create a super user
from django.contrib.auth.models import User
if User.objects.all().count() == 0:
    u = User.objects.create(
        username='bonnegent',
        first_name='Bonnegent',
        last_name='Sebastien',
        email='possum@sensia.homelinux.org',
        is_superuser=True,
        is_staff=True,
        is_active=True
    )
    u.set_password('bonnegent')
    u.save()

# base src
import sqlite3
#cx = sqlite3.connect("/home/pos/possum/data/database")
cx = sqlite3.connect("/home/pos/possum/database-2010")
cu = cx.cursor()

def convert_prix(montant):
    """Convertie un montant sans virgule en string avec un ."""
    if montant > 0:
        signe = ""
    else:
        signe = "-"
    montant = str(abs(montant))
    nb = len(montant)
    if nb > 2:
        result = "%s%s.%s" % (signe, montant[:-2], montant[-2:])
    elif nb == 2:
        result = "%s0.%s" % (signe, montant)
    elif nb == 1:
        result = "%s0.0%s" % (signe, montant)
    else:
        result = "0.0"
    return result

print "> les couleurs"
cu.execute("select id,red,green,blue from couleurs")
for id,red,green,blue in cu.fetchall():
    couleur = Couleur(id=id, red=red, green=green, blue=blue)
    couleur.save()

Couleur_get = Couleur.objects.get
print "> les categories et les produits"
cu.execute("select id,nom_facture,nom_ihm,priorite_facture,majoration_terrasse,id_couleur,is_alcool,override_surtaxe from categories")
for id,nom_facture,nom_ihm,priorite_facture,majoration_terrasse,id_couleur,is_alcool,override_surtaxe in cu.fetchall():
    couleur = Couleur_get(pk=id_couleur)
    categorie = Categorie(id=id, nom=nom_ihm, priorite=priorite_facture, surtaxable=majoration_terrasse, alcool=is_alcool, disable_surtaxe=override_surtaxe, couleur=couleur)
    categorie.save()

    cu.execute("select id,nom_facture,nom_ihm,prix_ttc,actif from produits where id_categorie=%s" % categorie.id)
    for id,nom_facture,nom_ihm,prix_ttc,actif in cu.fetchall():
        produit = Produit(id=id, nom=nom_ihm, nom_facture=nom_facture, prix=convert_prix(prix_ttc), actif=actif, categorie=categorie)
        produit.save()

Produit_get = Produit.objects.get
Categorie_get = Categorie.objects.get
print "> les menus"
cu.execute("select id_formule,id_categorie from formules_categories")
for id_formule,id_categorie in cu.fetchall():
    formule = Produit_get(id=id_formule)
    categorie = Categorie_get(id=id_categorie)
    formule.categories_ok.add(categorie)
    formule.save()
cu.execute("select id_formule,id_produit from formules_produits")
for id_formule,id_produit in cu.fetchall():
    formule = Produit_get(id=id_formule)
    produit = Produit_get(id=id_produit)
    formule.produits_ok.add(produit)
    formule.save()

PaiementType_get = PaiementType.objects.get
print "> les modes de paiements"
cu.execute("select id,nom_facture,nom_ihm,priorite from modes_paiements")
for id,nom_facture,nom_ihm,priorite in cu.fetchall():
    if id == 4 or id == 6:
        pass
    else:
        type = PaiementType(id=id, nom=nom_ihm, nom_facture=nom_facture, priorite=priorite)
        type.save()
# on ajoute les valeurs des tickets
cu.execute("select id,nom_facture,nom_ihm,priorite from modes_paiements where id=4")
id,nom_facture,nom_ihm,priorite = cu.fetchone()
type = PaiementType_get(pk=3)
type.fixed_value = True
type.last_value = nom_facture
type.save()
cu.execute("select id,nom_facture,nom_ihm,priorite from modes_paiements where id=6")
id,nom_facture,nom_ihm,priorite = cu.fetchone()
type = PaiementType_get(pk=5)
type.fixed_value = True
type.last_value = nom_facture
type.save()

print "> les logs"
cu.execute("select id,nom from log_type")
pbar = progressbar.ProgressBar(maxval=len(cu.fetchall())).start()
cu.execute("select id,nom from log_type")
count = 1
for id,nom in cu.fetchall():
    pbar.update(count)
    count += 1
    logtype = LogType(id=id, nom=nom)
    logtype.save()

    cu.execute("select id,date from logs where id_log_type=%s" % logtype.id)
    for id,date in cu.fetchall():
        olddate = str(date)
        newdate = "%s-%s-%s %s:%s:%s" % (olddate[0:4],olddate[4:6],olddate[6:8],olddate[8:10],olddate[10:12],olddate[12:14])
        log = Log(id=id, date=newdate, type=logtype)
        log.save()
        log.date = newdate
        log.save()
pbar.finish()

print "> creation des etages et des tables"
cu.execute("select id,nom,surtaxe from etages")
for id,nom,surtaxe in cu.fetchall():
    zone = Zone(id=id, nom=nom, surtaxe=surtaxe, prix_surtaxe=convert_prix(20))
    zone.save()

    cu.execute("select id,nom from tables where id_etage=%s" % zone.id)
    for id,nom in cu.fetchall():
        table = Table(id=id, nom=nom, zone=zone)
        table.save()

print "> creation des etats"
etat = Etat(nom="apero", priorite=10)
etat.save()
etat = Etat(nom="entree", priorite=15)
etat.save()
etat = Etat(nom="plat", priorite=20)
etat.save()
etat = Etat(nom="dessert", priorite=25)
etat.save()
etat = Etat(nom="cafe", priorite=30)
etat.save()
etat = Etat(nom="solde", priorite=35)
etat.save()

print "> creation des cuissons"
couleur = Couleur_get(pk=1)
cuisson = Cuisson(nom="bleu", priorite=10, couleur=couleur)
cuisson.save()
cuisson = Cuisson(nom="saignant", priorite=15, couleur=couleur)
cuisson.save()
cuisson = Cuisson(nom="bien cuit", priorite=20, couleur=couleur)
cuisson.save()

print "> creation des accompagnements"
accompagnement = Accompagnement(nom="frites")
accompagnement.save()
accompagnement = Accompagnement(nom="haricots verts")
accompagnement.save()
accompagnement = Accompagnement(nom="gratin dauphinois")
accompagnement.save()

print "> creation des sauces"
sauce = Sauce(nom="bearnaise")
sauce.save()
sauce = Sauce(nom="poivre")
sauce.save()

last_nb = 0
now = datetime.datetime.now
last_date = now()

Table_get = Table.objects.get
print "> les factures"
cu.execute("select id,date_creation,date_paiement,ttc,ttc_alcool,id_table,nb_couverts from factures %s" % limit)
pbar = progressbar.ProgressBar(maxval=len(cu.fetchall())).start()
cu.execute("select id,date_creation,date_paiement,ttc,ttc_alcool,id_table,nb_couverts from factures %s" % limit)
count = 1
for id,date_creation,date_paiement,ttc,ttc_alcool,id_table,nb_couverts in cu.fetchall():
    pbar.update(count)
    count += 1

    olddate_creation = str(date_creation)
    newdate_creation = "%s-%s-%s %s:%s:%s" % (olddate_creation[0:4],olddate_creation[4:6],olddate_creation[6:8],olddate_creation[8:10],olddate_creation[10:12],olddate_creation[12:14])
#    olddate_paiement = str(date_paiement)
#    newdate_paiement = "%s-%s-%s %s:%s:%s" % (olddate_paiement[0:4],olddate_paiement[4:6],olddate_paiement[6:8],olddate_paiement[8:10],olddate_paiement[10:12],olddate_paiement[12:14])
    if id_table:
        table = Table_get(id=id_table)
#        facture = Facture(id=id, date_creation=newdate_creation, date_paiement=newdate_paiement, montant_normal=ttc, montant_alcool=ttc_alcool, table=table, couverts=nb_couverts)
        facture = Facture(id=id, date_creation=newdate_creation, montant_normal=convert_prix(ttc), montant_alcool=convert_prix(ttc_alcool), table=table, couverts=nb_couverts)
    else:
#        facture = Facture(id=id, date_creation=newdate_creation, date_paiement=newdate_paiement, montant_normal=ttc, montant_alcool=ttc_alcool, couverts=nb_couverts)
        facture = Facture(id=id, date_creation=newdate_creation, montant_normal=convert_prix(ttc), montant_alcool=convert_prix(ttc_alcool), couverts=nb_couverts)
    facture.save()
    facture.date_creation = newdate_creation

    cu.execute("select id,id_mode_paiement,valeur_unitaire,date,montant_ttc from paiements where id_facture=%d" % facture.id)
    for id,id_mode_paiement,valeur_unitaire,date,montant_ttc in cu.fetchall():
        olddate = str(date)
        newdate = "%s-%s-%s %s:%s:%s" % (olddate[0:4],olddate[4:6],olddate[6:8],olddate[8:10],olddate[10:12],olddate[12:14])
        type = PaiementType_get(id=id_mode_paiement)
        paiement = Paiement(id=id, type=type, facture=facture, montant=convert_prix(montant_ttc), date=newdate)
        paiement.save()
        paiement.date = newdate
        if paiement.type.fixed_value:
            # on calcule le nombre de tickets
#            print paiement.montant
#            print paiement.valeur_unitaire
            paiement.valeur_unitaire = valeur_unitaire=convert_prix(valeur_unitaire)
            paiement.nb_tickets = int( Decimal(paiement.montant) / Decimal(paiement.valeur_unitaire) )
        paiement.save()
        facture.paiements.add(paiement)

    cu.execute("select id_produit from factures_produits where id_facture=%d" % facture.id)
    # liste des relations des sous produits deja pris
    deja_pris = []
    for [id_produit] in cu.fetchall():
        if produit:
            try:
                produit = Produit_get(id=id_produit)
                vendu = ProduitVendu(produit=produit, \
                        date=facture.date_creation, \
                        facture=facture, \
                        prix=produit.prix)
                vendu.save()
                vendu.date = facture.date_creation
#                facture.produits.add(vendu)

                sql = "select formules_produits.id_produit,factures_formules.id from factures_formules,formules_produits where factures_formules.id_facture=%d and factures_formules.id_formule_produit=formules_produits.id and formules_produits.id_formule=%d" % (facture.id, produit.id)
                cu.execute(sql)
                for row2 in cu.fetchall():
                    if row2[1] not in deja_pris:
                        if not vendu.isFull():
                            sub = ProduitVendu(
                                    produit=Produit_get(id=row2[0]), \
                                    facture=facture)
                            sub.save()
                            sub.date = facture.date_creation
                            sub.save()
#                            product.addProduit(self.db.getProductById(row2[0]))
                            vendu.contient.add(sub)
                            deja_pris.append(row2[1])
                vendu.save()
                facture.produits.add(vendu)
                #print "1 produit en plus pour id %d" % facture.id
#                self.produits.append(product)

            except Produit.DoesNotExist:
                print "! %d id_produit n'existe pas !" % id_produit
        else:
            print "[%s] id_produit == 0" % str(facture)

    facture.save()

pbar.finish()

# on remet en etat les index
from django.db import connection, transaction
cursor = connection.cursor()
for i in ["couleur", "paiementtype", "produit", "categorie", "logtype", "log", "zone", "table", "facture", "paiement"]:
    cursor.execute("SELECT setval('base_%s_id_seq', max(id)) FROM base_%s" % (i, i))
transaction.commit_unless_managed()

# \d base_couleur
#Couleur.objects.raw("SELECT setval('base_couleur_id_seq', max(id)) FROM base_couleur;")
#PaiementType.objects.raw("SELECT setval('base_paiementtype_id_seq', max(id)) FROM base_paiementtype;")
#Produit.objects.raw("SELECT setval('base_produit_id_seq', max(id)) FROM base_produit;")
#Categorie.objects.raw("SELECT setval('base_categorie_id_seq', max(id)) FROM base_categorie;")
#LogType.objects.raw("SELECT setval('base_logtype_id_seq', max(id)) FROM base_logtype;")
#Log.objects.raw("SELECT setval('base_log_id_seq', max(id)) FROM base_log;")
#Zone.objects.raw("SELECT setval('base_zone_id_seq', max(id)) FROM base_zone;")
#Table.objects.raw("SELECT setval('base_table_id_seq', max(id)) FROM base_table;")
#Facture.objects.raw("SELECT setval('base_facture_id_seq', max(id)) FROM base_facture;")
#Paiement.objects.raw("SELECT setval('base_paiement_id_seq', max(id)) FROM base_paiement;")

print "> correction des factures"
c = Categorie.objects.get(id=1)
for f in Facture.objects.exclude(restant_a_payer=0, produits__isnull=False):
    filter = Produit.objects.filter(prix=f.get_montant())
    count = filter.count()
    if count > 0:
        p = filter[0]
    else:
        nom = "recuperation ancienne base (%0.2f)" % f.get_montant()
        p = Produit(nom=nom, nom_facture=nom, prix=f.get_montant(), actif=False, categorie=c)
        p.save()
    vendu = ProduitVendu(produit=p, facture=f)
    vendu.save()
    f.produits.add(vendu)

interval = datetime.datetime.now() - debut

mn = interval.seconds / 60
sec = interval.seconds % 60
heures = mn / 60
mn = mn % 60

print "\n temps total: %dh %dm %ds (%d secondes)\n" % (heures, mn, sec, interval.seconds)

