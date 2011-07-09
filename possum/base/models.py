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

from django.db import models
import datetime
import logging
#import io
import os
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Avg, Max, Min, Sum

LONGUEUR_IHM = 60
LONGUEUR_FACTURE = 35

def remplissage(nb,  caractere,  largeur):
    """caractere est le caractere de remplissage"""
    milieu = caractere
    # on ajoute len(milieu) a nb
    nb += 1
    while nb < largeur:
        milieu += caractere
        nb += 1
    return milieu

# les classes generiques
class Nom(models.Model):
    nom = models.CharField(max_length=LONGUEUR_IHM)

    def __unicode__(self):
        return self.nom

    def __cmp__(self,other):
        return cmp(self.nom, other.nom)

    class Meta:
        abstract = True
        ordering = ['nom']

class NomDouble(Nom):
    nom_facture = models.CharField(max_length=LONGUEUR_FACTURE)

    class Meta:
        abstract = True

class Priorite(models.Model):
    priorite = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['priorite']

    def __cmp__(self, other):
        return cmp(self.priorite,other.priorite)

# les classes metiers
class Couleur(Nom):
    red = models.PositiveIntegerField(default=255)
    green = models.PositiveIntegerField(default=255)
    blue = models.PositiveIntegerField(default=255)

    def __unicode__(self):
        return "%s [%d / %d / %d]" % (self.nom, self.red, self.green, self.blue)

    def web(self):
        """Retourne la couleur sous la forme #ffe013
        """
        result = "#"
        for rgb in [self.red, self.green, self.blue]:
            tmp = hex(rgb).split('x')[1]
            if len(tmp) == 1:
                result += "0%s" % tmp
            elif len(tmp) == 2:
                result += tmp
            else:
                logging.warning("valeur trop grande")
        return result

class Cuisson(Nom, Priorite):
    """Cuisson d'un produit"""
    couleur = models.ForeignKey('Couleur', null=True, blank=True, related_name="cuisson-couleur")

class Sauce(Nom):
    """Sauce d'un produit"""
    couleur = models.ForeignKey('Couleur', null=True, blank=True, related_name="sauce-couleur")

class Accompagnement(Nom):
    """Accompagnement d'un produit"""
    couleur = models.ForeignKey('Couleur', null=True, blank=True, related_name="accompagnement-couleur")

class Etat(Nom, Priorite):
    """Etat d'une facture"""

    def __cmp__(self, other):
        return cmp(self.priorite,other.priorite)

class Suivi(models.Model):
    """Suivi des etats"""
    facture = models.ForeignKey('Facture', related_name="suivi-facture")
    etat = models.ForeignKey('Etat', related_name="suivi-etat")
    date = models.DateTimeField('depuis le', auto_now_add=True)

    def __unicode__(self):
        return "Facture %s : etat %s" % (self.facture, self.etat.nom)

class Categorie(Nom, Priorite):
    surtaxable = models.BooleanField("majoration terrasse")
    couleur = models.ForeignKey('Couleur', null=True, blank=True, related_name="categorie-couleur")
#    majoration_terrasse = models.BooleanField()
#    couleur = models.ForeignKey(Couleur)
    alcool = models.BooleanField(default=False)
    disable_surtaxe = models.BooleanField("peut enlever la surtaxe presente", default=False)

    def __cmp__(self,other):
        """
        Classement par priorite_facture (plus la valeur est petite,
        plus elle est prioritaire), puis par nom_ihm en cas d'égalité.

        >>> cat1 = Categorie(nom="nom1",priorite=1)
        >>> cat2 = Categorie(nom="nom2")
        >>> cat3 = Categorie(nom="nom3",priorite=1)
        >>> liste = []
        >>> liste.append(cat3)
        >>> liste.append(cat2)
        >>> liste.append(cat1)
        >>> liste
        [<Categorie: [0] [nom3]>, <Categorie: [0] [nom2]>, <Categorie: [0] [nom1]>]
        >>> liste.sort()
        >>> liste
        [<Categorie: [0] [nom2]>, <Categorie: [0] [nom1]>, <Categorie: [0] [nom3]>]
        """
        if self.priorite == other.priorite:
            return cmp(self.nom,other.nom)
        else:
            return cmp(self.priorite,other.priorite)

    def show(self):
        nb = Produit.objects.filter(categorie=self,actif=True).count()
        if self.surtaxable:
            # soumis a la majoration terrasse
            infos = "MAJ"
        else:
            infos = "___"
        if self.disable_surtaxe:
            # peut desactiver une eventuelle surtaxe
            infos += " DIS"
        else:
            infos += " ___"
#        return u"1 %s % 12.2f" % (self.produit.nom_facture, self.prix)
        return u"%-18s (% 3d produits)  [%s]" % (self.nom[:18], nb, infos)

class Produit(NomDouble):
    categorie = models.ForeignKey('Categorie', related_name="produit-categorie")
    choix_cuisson = models.BooleanField(default=False)
    choix_accompagnement = models.BooleanField(default=False)
    choix_sauce = models.BooleanField(default=False)
    # pour les menus / formules
    # categories authorisees
    categories_ok = models.ManyToManyField(Categorie)
    # produits authorises
    produits_ok = models.ManyToManyField('self')
    actif = models.BooleanField(default=True)
    # max_digits: la longueur totale du nombre (avec les décimaux)
    # decimal_places: la partie décimale
    # ici: 2 chiffres après la virgule et 5 chiffres pour la partie entière
    prix = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def __cmp__(self,other):
        if self.categorie == other.categorie:
            return cmp(self.nom,other.nom)
        else:
            return cmp(self.categorie,other.categorie)

    class Meta:
        ordering = ('categorie', 'nom')
#        ordering = ['-actif', 'nom']

    def __unicode__(self):
#        return u"[%s] %s (%.2f€)" % (self.categorie.nom, self.nom, self.prix)
        return u"%s" % self.nom

    def est_un_menu(self):
        if self.categories_ok.count():
            return True
        else:
            return False

    def show(self):
#        return u"1 %s % 12.2f" % (self.produit.nom_facture, self.prix)
        return u" 1 %-25s % 7.2f" % (self.nom_facture[:25], self.prix)

class ProduitVendu(models.Model):
    """le prix sert a affiche correctement les prix pour les surtaxes
    """
    date = models.DateTimeField(auto_now_add=True)
#    facture = models.ForeignKey('Facture', related_name="produitvendu-facture")
    #facture = models.ForeignKey('Facture', limit_choices_to = {'date_creation__gt': datetime.datetime.today()})
    produit = models.ForeignKey('Produit', related_name="produitvendu-produit")
    cuisson = models.ForeignKey('Cuisson', null=True, blank=True, related_name="produitvendu-cuisson")
    prix = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    sauce = models.ForeignKey('Sauce', null=True, blank=True, related_name="produitvendu-sauce")
    accompagnement = models.ForeignKey('Accompagnement', null=True, blank=True, related_name="produitvendu-accompagnement")
    # dans le cas d'un menu, peut contenir d'autres produits
#    contient = models.ManyToManyField(Produit, null=True)
    contient = models.ManyToManyField('self')

    class Meta:
        ordering = ('produit',)

    def __unicode__(self):
        return u"%s" % self.produit.nom

    def isFull(self):
        """
        True si tous les élèments sous présents (les sous produits pour les formules)
        et False sinon.

        >>> vendu = ProduitVendu()
        >>> vendu.save()
        >>> vendu.isFull()
        True
        >>> cat1 = Categorie(nom="cat1")
        >>> cat1.save()
        >>> cat2 = Categorie(nom="cat2")
        >>> cat2.save()
        >>> vendu.categories_ok.add(cat1, cat2)
        >>> vendu.isFull()
        False
        >>> vendu.produits = [ 1 ]
        >>> vendu.isFull()
        False
        >>> vendu.produits = [ 1, 2 ]
        >>> vendu.isFull()
        True
        >>> vendu.produits = [ 1, 2, 3 ]
        >>> vendu.isFull()
        True
        """
        nb_produits = self.contient.count()
        nb_categories = self.produit.categories_ok.count()
        if nb_produits == nb_categories:
#            logging.debug("product is full")
            return True
        elif nb_produits > nb_categories:
 #           logging.warning("product id "+str(self.id)+" have more products that categories authorized")
            return True
        else:
#            logging.debug("product is not full")
            return False

    def __cmp__(self,other):
        if self.produit.categorie == other.produit.categorie:
            return cmp(self.produit.nom,other.produit.nom)
        else:
            return cmp(self.produit.categorie,other.produit.categorie)

    def est_un_menu(self):
        if self.produit.categories_ok.count():
            return True
        else:
            return False

    def show(self):
#        return u"1 %s % 12.2f" % (self.produit.nom_facture, self.prix)
        return u"1 %-25s % 7.2f" % (self.produit.nom_facture[:25], self.prix)

    def showSubProducts(self):
        return u"   - %s " % self.produit.nom_facture

    def getFreeCategorie(self):
        """Retourne la premiere categorie dans la liste categories_ok
        qui n'a pas de produit dans la partir 'contient'. Sinon retourne
        None

        >>> f = Facture(id=3)
        >>> cat1 = Categorie(id=1, nom="cat1")
        >>> cat2 = Categorie(id=2, nom="cat2")
        >>> produit1 = Produit(id=1, nom="p1", categorie=cat1)
        >>> produit2 = Produit(id=2, nom="p2", categorie=cat2)
        >>> vendu = ProduitVendu(id=1, produit=produit1, facture=f)
        >>> vendu.getFreeCategorie()
        0
        >>> produit1.categories_ok.add(cat1, cat2)
        >>> vendu.getFreeCategorie()
        0
        >>> sub = ProduitVendu(id=2, produit=produit1, facture=f)
        >>> vendu.contient.add(sub)
        >>> vendu.getFreeCategorie()
        1
        >>> sub = ProduitVendu(id=3, produit=produit2, facture=f)
        >>> sub.produit.categorie = cat2
        >>> vendu.contient.add(sub)
        >>> vendu.getFreeCategorie()
        0
        """
        if self.produit.categories_ok.count() > 0:
            for categorie in self.produit.categories_ok.order_by("priorite").iterator():
                if self.contient.filter(produit__categorie=categorie).count() == 0:
                    return categorie
        else:
            logging.warning("Product "+str(self.id)+" have no categories_ok, return None")
        return None

class Zone(Nom):
    surtaxe = models.BooleanField("zone surtaxée ?", default=False)
    prix_surtaxe = models.DecimalField(max_digits=4, decimal_places=2, default=0)
#    prix_surtaxe = models.PositiveIntegerField("surtaxe en centimes")

    def est_surtaxe(self):
#       logging.debug("surtaxe de %d centimes sur la zone %s" % (self.surtaxe))
        return self.surtaxe

class Table(Nom):
    zone = models.ForeignKey('Zone', related_name="table-zone")

    def est_surtaxe(self):
        if self.zone:
            result = self.zone.est_surtaxe()
        else:
            # par defaut, il n'y a pas de surtaxe
            result = False
        return result

class LogType(Nom):
    """Correspond au type de Log ainsi qu'au type de stats"""
#    pass
    description = models.CharField(max_length=200, blank=True)

class Log(models.Model):
    date = models.DateTimeField('creer le', auto_now_add=True)
    type = models.ForeignKey('LogType', related_name="log-logtype")

    class Meta:
        get_latest_by = 'date'

    def __unicode__(self):
        return "[%s] %s" % (self.date.strftime("%H:%M %d/%m/%Y"), self.type.nom)

class StatsJour(models.Model):
    """Modele pour les classes de statistiques."""
    date = models.DateField()
    valeur = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        get_latest_by = 'date'
        abstract = True

class StatsJourGeneral(StatsJour):
    """Les stats concernent un type
    (nb_couverts, nb_facture, nb_bar, ca_resto, ca_bar)"""
    type = models.ForeignKey('LogType',
                             null=True,
                             blank=True,
                             related_name="statsjour-logtype")

    def get_data(self, nom, date):
        """Cherche dans les stats, une donnee au nom et a la date
        indiquee et retourne sa valeur."""
        try:
            log = LogType.objects.get(nom=nom)
        except LogType.DoesNotExist:
            logging.debug("pas de LogType pour le nom: %s" % nom)
            return Decimal("0")
        try:
            stats = StatsJourGeneral.objects.get(date=date, type=log).valeur
            if stats:
                return stats
            else:
                return Decimal("0")
        except StatsJourGeneral.DoesNotExist:
            return Decimal("0")

    def get_max(self, nom):
        try:
            log = LogType.objects.get(nom=nom)
        except LogType.DoesNotExist:
            logging.debug("pas de LogType pour le nom: %s" % nom)
            return Decimal("0")
        result = StatsJourGeneral.objects.filter(type=log).aggregate(
                                        Max('valeur'))['valeur__max']
        if result:
            return result
        else:
            return Decimal("0")

    def get_avg(self, nom):
        try:
            log = LogType.objects.get(nom=nom)
        except LogType.DoesNotExist:
            logging.debug("pas de LogType pour le nom: %s" % nom)
            return Decimal("0")
        result = StatsJourGeneral.objects.filter(type=log).aggregate(
                                        Avg('valeur'))['valeur__avg']
        if result:
            return result
        else:
            return Decimal("0")

    def get_min(self, nom):
        try:
            log = LogType.objects.get(nom=nom)
        except LogType.DoesNotExist:
            logging.debug("pas de LogType pour le nom: %s" % nom)
            return Decimal("0")
        result = StatsJourGeneral.objects.filter(type=log).aggregate(
                                        Min('valeur'))['valeur__min']
        if result:
            return result
        else:
            return Decimal("0")


class StatsJourPaiement(StatsJour):
    """Les stats concernent les paiements :
    - nombre de paiements (ou nombre de tickets pour TR et ANCV)
    - montant total par paiement
    """
    paiement = models.ForeignKey('PaiementType',
                                null=True,
                                blank=True,
                                related_name="statsjour-paiement")
    nb = models.PositiveIntegerField(default=0)

class StatsJourProduit(StatsJour):
    """Les stats concernent un produit (nombre de produits vendus, CA)
    """
    produit = models.ForeignKey('Produit',
                                null=True,
                                blank=True,
                                related_name="statsjour-produit")
    nb = models.PositiveIntegerField(default=0)

class StatsJourCategorie(StatsJour):
    """Les stats concernent une categorie
    (CA genere par cette categorie)"""
    categorie = models.ForeignKey('Categorie',
                                  null=True,
                                  blank=True,
                                  related_name="statsjour-categorie")
    nb = models.PositiveIntegerField(default=0)

#class StatsSemaine(models.Model):
    #"""Statistique par semaine"""
    #annee = models.PositiveIntegerField(default=0)
    #semaine = models.PositiveIntegerField(default=0)
    #valeur = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    #class Meta:
        #abstract = True

#class StatsSemaineGeneral(StatsSemaine):
    #"""Les stats concernent un type
    #(nb_couverts, nb_facture, nb_bar, ca_resto, ca_bar)"""
    #type = models.ForeignKey('LogType',
                             #null=True,
                             #blank=True,
                             #related_name="statssemaine-logtype")

#class StatsSemaineProduit(StatsSemaine):
    #"""Les stats concernent un produit (nombre de produits vendus, CA)
    #"""
    #produit = models.ForeignKey('Produit',
                                #null=True,
                                #blank=True,
                                #related_name="statssemaine-produit")
    #nb = models.PositiveIntegerField(default=0)

#class StatsSemaineCategorie(StatsSemaine):
    #"""Les stats concernent une categorie
    #(CA genere par cette categorie)"""
    #categorie = models.ForeignKey('Categorie',
                                  #null=True,
                                  #blank=True,
                                  #related_name="statssemaine-categorie")


class PaiementType(Priorite, NomDouble):
    """Type de paiment"""
    fixed_value = models.BooleanField("ticket ?", default=False)
#    last_value = models.PositiveIntegerField("dernière valeur", default=0)

class Paiement(models.Model):
    """valeur_unitaire: pour gerer les montants des tickets restos"""
    #facture = models.ForeignKey('Facture', related_name="paiement-facture")
    type = models.ForeignKey('PaiementType', related_name="paiement-type")
#    montant = models.IntegerField("TTC")
#    valeur_unitaire = models.PositiveIntegerField(default=1)
    montant = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    valeur_unitaire = models.DecimalField(max_digits=9, decimal_places=2, default=1)
    date = models.DateTimeField('encaisser le', auto_now_add=True)
    nb_tickets = models.PositiveIntegerField(default=0)

    class Meta:
        get_latest_by = 'date'

    def __unicode__(self):
        if self.type.fixed_value:
            return u"%-20s % 8.2f €    (%d tickets x %5.2f €)" % ( \
                    self.type.nom, self.montant, self.nb_tickets, \
                    self.valeur_unitaire)
        else:
            return u"%-20s % 8.2f €" % (self.type.nom, self.montant)

    def __cmp__(self,other):
        return cmp(self.date.date,other.date.date)

    def show(self):
        return str(self)

class Facture(models.Model):
    date_creation = models.DateTimeField('creer le', auto_now_add=True)
    table = models.ForeignKey('Table', null=True, blank=True, related_name="facture-table")
    couverts = models.PositiveIntegerField("nombre de couverts", default=0)
    produits = models.ManyToManyField('ProduitVendu',
        related_name="les produits facturés",
        limit_choices_to = {'date__gt': datetime.datetime.today()})
    montant_normal = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    montant_alcool = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    paiements = models.ManyToManyField('Paiement',
        related_name="les paiements",
        limit_choices_to = {'date__gt': datetime.datetime.today()})
    restant_a_payer = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    etats = models.ManyToManyField('Suivi', related_name="le suivi")
    saved_in_stats = models.BooleanField(default=False)

    class Meta:
        get_latest_by = 'id'

    def __unicode__(self):
        if self.id:
            id = self.id
        else:
            id = 0
        if self.date_creation:
#            print self.date_creation
#            date = self.date_creation.strftime("%Y/%m/%d %H:%M")
            date = self.date_creation.strftime("%H:%M %d/%m")
        else:
            date = "--:-- --/--"
        total = self.total()
        return u"%s F%06d" % (date, id)

    def __cmp__(self, other):
        """
            Les factures sont triees par date_creation.
            D'abord les plus récentes, puis les plus vielles.
        """
        return cmp(self.date_creation,other.date_creation)

    def guest_couverts(self):
        """Essaye de deviner le nombre de couverts"""
        nb = {}
        categories = ["Entrees", "Plats", "Desserts"]
        for categorie in categories:
            nb[categorie] = 0
        for vendu in self.produits.iterator():
            if vendu.produit.categorie.nom in categories:
                nb[vendu.produit.categorie.nom] += 1
            for sous_produit in vendu.contient.iterator():
                if sous_produit.produit.categorie.nom in categories:
                    nb[sous_produit.produit.categorie.nom] += 1
        return max(nb.values())

    def set_couverts(self, nb):
        """Change le nombre de couvert"""
        self.couverts = nb
        self.save()

    def set_table(self, table):
        """Change la table de la facture
        On prend en compte le changement de tarification si changement
        de zone.
        """
        surtaxe_avant = self.est_surtaxe()
        self.table = table
        self._changement_de_surtaxe(surtaxe_avant, self.est_surtaxe())
        self.save()

    def _changement_de_surtaxe(self, surtaxe_avant, surtaxe_apres):
        """ajoute ou enleve les surtaxes pour la terrasse
        Les 2 parametres sont des booleens

        Attention: pour enlever ou ajouter la surtaxe, on utilise la
        surtaxe de la nouvelle table (on ne connait pas l'ancienne). Le
        montant de la surtaxe doit donc etre la meme que la surtaxe soit
        active ou pas sur la zone.
        """
        #logging.debug("")
        if surtaxe_avant != surtaxe_apres:
            logging.debug("changement de surtaxe")
            # on enleve ou on ajoute
            if surtaxe_avant:
                # on enleve
                multi = Decimal("-1")
            else:
                # on ajoute
                multi = Decimal("1")
            for vendu in self.produits.iterator():
                if vendu.produit.categorie.surtaxable:
                    vendu.prix += self.table.zone.prix_surtaxe * multi
                    vendu.save()
                    if vendu.produit.categorie.alcool:
                        self.montant_alcool += self.table.zone.prix_surtaxe * multi
                    else:
                        self.montant_normal += self.table.zone.prix_surtaxe * multi
                    self.restant_a_payer += self.table.zone.prix_surtaxe * multi

    def nb_soldee_jour(self, date):
        """Nombre de facture soldee le jour 'date'"""
        if date.hour > 5:
            date_min = datetime.datetime(date.year, date.month, date.day, 5)
        else:
            tmp = date - datetime.timedelta(days=1)
            date_min = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        tmp = date_min + datetime.timedelta(days=1)
        date_max = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        return Facture.objects.filter(date_creation__gt=date_min, \
                                        date_creation__lt=date_max, \
                                        restant_a_payer=0).exclude( \
                                        produits__isnull=True).count()

    def non_soldees(self):
        """Retourne la liste des factures non soldees"""
        liste = []
        for i in Facture.objects.exclude(restant_a_payer=0).iterator():
            liste.append(i)
        for i in Facture.objects.filter(produits__isnull=True).iterator():
            liste.append(i)
        return liste

    def add(self, vendu):
        """Ajout d'un produit à la facture.
        Si c'est le premier produit alors on modifie la date de creation
        """
        if self.produits.count() == 0:
            self.date_creation = datetime.datetime.now()

        vendu.prix = vendu.produit.prix
        vendu.save()
        if vendu.prix:
            surtaxe_avant = self.est_surtaxe()
            self.produits.add(vendu)
            # ici on utilise surtaxe_avant car le cas du changement de
            # tarification est traite sur toute la facture
            if vendu.produit.categorie.surtaxable and surtaxe_avant:
                vendu.prix += self.table.zone.prix_surtaxe
                vendu.save()
            if vendu.produit.categorie.alcool:
                self.montant_alcool += vendu.prix
            else:
                self.montant_normal += vendu.prix
            self.restant_a_payer += vendu.prix

            # il y a modification de la surtaxe du a l'ajout d'un produit ?
            # cas d'une table surtaxee avec alcool qui achete de la nourriture
            self._changement_de_surtaxe(surtaxe_avant, self.est_surtaxe())
        else:
            # on a certainement a faire a une reduction
            # -10%
            if vendu.produit.nom == "Remise -10%":
                vendu.prix = self.get_montant() / Decimal("-10")
                vendu.save()
                logging.debug("la remise est de: %s" % vendu.prix)
                self.produits.add(vendu)
                self.restant_a_payer += vendu.prix
                self.montant_normal += vendu.prix
            else:
                logging.debug("cette remise n'est pas connue")
        #self.produits.order_by('produit')
        self.save()

    def del_produit(self, vendu):
        """On enleve un produit à la facture.
        
        Si le montant est négatif après le retrait d'un élèment,
        c'est qu'il reste certainement une remise, dans
        ce cas on enlève tous les produits.
        """
        if vendu in self.produits.all():
            self.produits.remove(vendu)
            #prix = vendu.produit.prix
            #if vendu.produit.categorie.surtaxable and self.est_surtaxe():
            #    prix += self.table.zone.prix_surtaxe
            if vendu.produit.categorie.alcool:
                self.montant_alcool -= vendu.prix
            else:
                self.montant_normal -= vendu.prix
            self.restant_a_payer -= vendu.prix
            vendu.delete()
            self.save()
            if self.get_montant() < Decimal("0"):
                self.del_all_produits()
        else:
            logging.warning("[%s] on essaye de supprimer un produit "\
                            "qui n'est pas dans la facture" % self)

    def del_all_produits(self):
        """On supprime tous les produits"""
        if self.produits.count():
            for vendu in self.produits.iterator():
                vendu.delete()
            self.produits.clear()
            self.montant_alcool = Decimal("0")
            self.montant_normal = Decimal("0")

            for paiement in self.paiements.iterator():
                paiement.delete()
            self.paiements.clear()
            self.restant_a_payer = Decimal("0")
            self.save()
        else:
            logging.debug("la facture ne contient pas de produits")

    def del_all_paiements(self):
        """On supprime tous les paiements"""
        if self.paiements.count():
            for paiement in self.paiements.iterator():
                paiement.delete()
            self.paiements.clear()
            self.restant_a_payer = self.get_montant()
            self.save()

    def del_paiement(self, paiement):
        """On supprime un paiement"""
        if paiement in self.paiements.all():
            self.restant_a_payer += paiement.montant
            self.paiements.remove(paiement)
            paiement.delete()
            self.save()
        else:
            logging.warning("[%s] on essaye de supprimer un paiement "\
                            "qui n'est pas dans la facture: %s %s %s %s"\
                            % (self, paiement.id, paiement.date,\
                            paiement.type.nom, paiement.montant))

    def get_users(self):
        """Donne la liste des noms d'utilisateurs"""
        users = []
        for user in User.objects.order_by('username').iterator():
            if user.is_active:
                users.append(user.username)
        return users

    def get_last_connected(self):
        try:
            return User.objects.order_by('last_login')[0].username
        except:
            return "aucun utilisateur"

    def authenticate(self, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.groups.filter(name='Managers').count() == 1:
                return True
            else:
                logging.debug("utilisateur non authorise: %s" % username)
                return False
        else:
            logging.debug("erreur avec: %s / %s" % (username, password))
            return False

    def getTvaNormal(self):
        """
            calcul la TVA
            On arrondi seulement à 1 parce que les 2 décimals sont dans la partie entière du montant
            # la TVA est sur le HT !!
        """
        #return self.montant_normal - ((self.montant_normal*100)/Decimal("105.5"))
        return self.montant_normal * (Decimal("0.055") / Decimal("1.055"))

    def getTvaAlcool(self):
        #return self.montant_alcool - ((self.montant_alcool*100)/Decimal("119.6"))
        return self.montant_alcool * (Decimal("0.196") / Decimal("1.196"))

    def get_resume(self):
        return "%s %s %d" % (self.table.nom, self.date_creation, self.montant)

    def get_montant(self):
        return self.montant_normal + self.montant_alcool

    def ajout_paiement(self, modepaiement, montant, valeur_unitaire=Decimal("1.0")):
        """
        modepaiement est un TypePaiement
        montant est un Decimal

        Si le montant est superieur au restant du alors on rembourse en
        espece.
        """
        logging.debug("Nouveau paiement")
        if self.restant_a_payer <= Decimal("0"):
            logging.info("[%s] nouveau paiement ignore car restant"\
                            " a payer <= 0 (%5.2f)"
                            % (self,self.restant_a_payer))
            return False

        paiement = Paiement()
        paiement.type = modepaiement
        paiement.valeur_unitaire = valeur_unitaire
        #paiement.facture = self
        if self.produits:
            # le montant est-il indique ?
            if montant == Decimal("0"):
                # on droit en trouver un
                if modepaiement.fixed_value:
                    # on doit trouver le nombre de ticket
                    paiement.nb_tickets = int(self.restant_a_payer / valeur_unitaire)
                    if paiement.nb_tickets == 0:
                        # on enregistre 1 ticket et un rendu de monnaie
                        # en espece
                        paiement.nb_tickets = 1
                        paiement.montant = valeur_unitaire
                    else:
                        paiement.montant = valeur_unitaire * paiement.nb_tickets
                else:
                    paiement.montant = self.restant_a_payer
            else:
                # le montant est indique
                if modepaiement.fixed_value:
                    # dans ce cas le montant est le nombre de ticket
                    paiement.nb_tickets = int(montant)
                    paiement.montant = paiement.nb_tickets * valeur_unitaire
                else:
                    paiement.montant = montant
            # on enregistre ce paiement
            paiement.save()
            self.paiements.add(paiement)
            # regularisation si le montant est superieur au montant du
            if paiement.montant > self.restant_a_payer:
                monnaie = Paiement()
                monnaie.type = PaiementType.objects.get(nom="Espece")
                #monnaie.facture = self
                monnaie.montant = self.restant_a_payer - paiement.montant
                monnaie.save()
                self.paiements.add(monnaie)
                self.restant_a_payer -= monnaie.montant
            self.restant_a_payer -= paiement.montant
            self.save()
        else:
            logging.debug("pas de produit, donc rien n'a payer")

    def total(self):
        return self.montant_alcool + self.montant_normal

    def est_soldee(self):
        """La facture a été utilisée et soldée"""
        if self.restant_a_payer == 0 and self.produits.count() > 0:
            return True
        else:
            return False

    def est_un_repas(self):
        """Est ce que la facture contient un element compris dans les
        categories entrees, plats, desserts ou formules
        """
        for vendu in self.produits.iterator():
            if vendu.produit.categorie.nom in ["Entrees", "Plats", \
                                               "Desserts","Formules"]:
                return True
        return False

    def est_vierge(self):
        """La facture est vierge"""
        if self.restant_a_payer == 0 and self.produits.count() == 0:
            return True
        else:
            return False

    def est_surtaxe(self):
        """
        Table is surtaxed et il n'y a pas de nourriture.
        """
        for produit in self.produits.all():
            #logging.debug("test with produit: %s and categorie id: %d" % (produit.nom, produit.categorie.id))
            if produit.produit.categorie.disable_surtaxe:
                #logging.debug("pas de surtaxe")
                return False
        if self.table:
            return self.table.est_surtaxe()
        else:
            return False

    def check_path(self, path):
        """Verifie l'existance du chemin et cree le repertoire si besoin
        '"""
        path_splitted = path.split("/")
        for i in xrange(len(path_splitted)):
            if path_splitted[i]:
                tmp = "/".join(path_splitted[:i+1])
                if not os.path.exists(tmp):
                    os.mkdir(tmp)

    def rapport_mois(self, mois):
        """Retourne dans une liste le rapport du mois 'mois'
        'mois' est de type datetime.today()

        exemple:

        -- CA mensuel 12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        """
        logging.debug(mois)
        date_min = datetime.datetime(mois.year, mois.month, 1, 5)
        # on est le mois suivant (32 c'est pour etre sur de ne pas
        # tomber sur le 31 du mois)
        tmp = date_min + datetime.timedelta(days=32)
        # modulo pour le cas de decembre + 1 = janvier
        date_max = datetime.datetime(tmp.year, tmp.month, 1, 5)
        texte = []
        texte.append("    -- CA mensuel %s --" % mois.strftime("%m/%Y"))
        selection = StatsJourPaiement.objects.filter( \
                            date__gte=date_min, \
                            date__lt=date_max)
        for paiement in PaiementType.objects.iterator():
            total = selection.filter(paiement=paiement).aggregate(Sum('valeur'))['valeur__sum']
            if total > 0:
                texte.append("%-20s %10.2f" % (paiement.nom, total))
        selection = StatsJourGeneral.objects.filter( \
                            date__gte=date_min, \
                            date__lt=date_max)
        ca = selection.filter(type=LogType.objects.get(nom="ca")).aggregate(Sum('valeur'))['valeur__sum']
        if ca == None:
            ca = 0.0

        # IMPORTANT:
        #   ici on ne se sert pas des stats 'tva_normal' et 'tva_alcool'
        #   car il y a des erreurs d'arrondies à cause des additions
        #   successives
        montant_normal = selection.filter(type=LogType.objects.get(nom="montant_normal")).aggregate(Sum('valeur'))['valeur__sum']
        if montant_normal == None:
            tva_normal = 0.0
        else:
            tva_normal = montant_normal*(Decimal("0.055") / Decimal("1.055"))
        montant_alcool = selection.filter(type=LogType.objects.get(nom="montant_alcool")).aggregate(Sum('valeur'))['valeur__sum']
        if montant_alcool == None:
            tva_alcool = 0.0
        else:
            tva_alcool = montant_alcool*(Decimal("0.196") / Decimal("1.196"))

        texte.append("%-20s %10.2f" % ("total TTC:", ca))
        texte.append("%-20s %10.2f" % ("total TVA  5.5:", tva_normal))
        texte.append("%-20s %10.2f" % ("total TVA 19.6:", tva_alcool))
        return texte

    def rapport_mois_old(self, mois):
        """Retourne dans une liste le rapport du mois 'mois'
        'mois' est de type datetime.today()

        exemple:

        -- CA mensuel 12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        """
        date_min = datetime.datetime(mois.year, mois.month, 1, 5)
        # on est le mois suivant (32 c'est pour etre sur de ne pas
        # tomber sur le 31 du mois)
        tmp = date_min + datetime.timedelta(days=32)
        # modulo pour le cas de decembre + 1 = janvier
        date_max = datetime.datetime(tmp.year, tmp.month, 1, 5)
        total = Decimal("0")
        tva_normal = Decimal("0")
        tva_alcool = Decimal("0")
        paiements = {}
        for p in PaiementType.objects.iterator():
            paiements[p.nom] = Decimal("0")
        #nb_f = 0
        for f in Facture.objects.filter( \
                            date_creation__gt=date_min, \
                            date_creation__lt=date_max).iterator():
            if f.est_soldee():
                #nb_f += 1
                for p in f.paiements.iterator():
                    paiements[p.type.nom] += p.montant
                total += f.get_montant()
                tva_normal += f.getTvaNormal()
                tva_alcool += f.getTvaAlcool()
                #print "nb facture: %d" % nb_f
                #print "total: %s" % total
        # enregistrement
        #self.check_path(settings.PATH_TICKET)
        #filename = "%s/%s" % (settings.PATH_TICKET, \
        #                        mois.strftime("mois-%Y%m"))
        #fd = open(filename, "w")
        texte = []
        #fd.write("    -- CA mensuel %s --\n" % mois.strftime("%m/%Y"))
        texte.append("    -- CA mensuel %s --" % mois.strftime("%m/%Y"))
        for p in PaiementType.objects.iterator():
            if paiements[p.nom]:
                texte.append("%-20s %10.2f" % (p.nom, paiements[p.nom]))
                #fd.write("%-20s %10.2f\n" % (p.nom, paiements[p.nom]))
        texte.append("%-20s %10.2f" % ("total TTC:", total))
        texte.append("%-20s %10.2f" % ("total TVA  5.5:", tva_normal))
        texte.append("%-20s %10.2f" % ("total TVA 19.6:", tva_alcool))
        #fd.write("%-20s %10.2f\n" % ("total TTC:", total))
        #fd.write("%-20s %10.2f\n" % ("total TVA  5.5:", tva_normal))
        #fd.write("%-20s %10.2f\n" % ("total TVA 19.6:", tva_alcool))
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.close()
        #return filename
        return texte

    def get_factures_du_jour(self, date):
        """Retourne la liste des factures soldees du jour 'date'"""
        date_min = datetime.datetime(date.year, date.month, date.day, 5)
        tmp = date_min + datetime.timedelta(days=1)
        date_max = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        return Facture.objects.filter( \
                                      date_creation__gt=date_min, \
                                      date_creation__lt=date_max, \
                                      restant_a_payer = 0).exclude(\
                                      produits__isnull = True)

    def rapport_jour(self, date):
        """Retourne le rapport du jour sous la forme d'une liste
        'jour' est de type datetime.today()

        exemple:
        -- 15/12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        Menu E/P :            16
        Menu P/D :            16
        Menu Tradition :      16

        Salade cesar :         6
        ...

        plat ...
        """
        logging.debug(date)
        texte = []
        if date == None:
            logging.warning("la date fournie est inconnue")
            return texte
        stats = StatsJourGeneral()
        texte.append("       -- %s --" % date.strftime("%d/%m/%Y"))
        texte.append("CA TTC (% 4d fact.): %11.2f" % (
                                    stats.get_data("nb_factures", date),
                                    stats.get_data("ca", date)))
        # IMPORTANT:
        #   ici on ne se sert pas des stats 'tva_normal' et 'tva_alcool'
        #   car il y a des erreurs d'arrondies à cause des additions
        #   successives
        tva_normal = stats.get_data("montant_normal", date)*(Decimal("0.055") / Decimal("1.055"))
        texte.append("%-20s %11.2f" % ("total TVA  5.5:", tva_normal))
        tva_alcool = stats.get_data("montant_alcool", date)*(Decimal("0.196") / Decimal("1.196"))
        texte.append("%-20s %11.2f" % ("total TVA 19.6:", tva_alcool))
        for stats in StatsJourPaiement.objects.filter(date=date)\
                                              .order_by("paiement")\
                                              .iterator():
            texte.append("%-15s (%d) %11.2f" % (stats.paiement.nom,
                                                stats.nb,
                                                stats.valeur))
        texte.append(" ")
        for cate in ["Formules", "Entrees", "Plats", "Desserts"]:
            try:
                categorie = Categorie.objects.get(nom=cate)
                stats = StatsJourCategorie.objects.get(date=date,
                                                    categorie=categorie)
                texte.append("%-21s %10d" % (cate, stats.nb))
                for stats in StatsJourProduit.objects.filter(date=date, produit__categorie=categorie).order_by("produit").iterator():
                    texte.append(" %-20s %10d" % (stats.produit.nom, stats.nb))
                texte.append(" ")
            except StatsJourCategorie.DoesNotExist:
                continue
        return texte

    def rapport_jour_old(self, date):
        """Retourne le rapport du jour sous la forme d'une liste
        'jour' est de type datetime.today()

        exemple:
        -- 15/12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        Menu E/P :            16
        Menu P/D :            16
        Menu Tradition :      16

        Salade cesar :         6
        ...

        plat ...
        """
        logging.debug(date)
        date_min = datetime.datetime(date.year, date.month, date.day, 5)
        tmp = date_min + datetime.timedelta(days=1)
        date_max = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        total = Decimal("0")
        tva_normal = Decimal("0")
        tva_alcool = Decimal("0")
        nb_plats = {}
        categories = ["Formules", "Entrees", "Plats", "Desserts"]
        for cate in categories:
            nb_plats[cate] = {}
            nb_plats[cate]['total'] = 0
        paiements = {}
        for p in PaiementType.objects.iterator():
            paiements[p.nom] = Decimal("0")
        nb_factures = 0
        for f in Facture.objects.filter( \
                            date_creation__gt=date_min, \
                            date_creation__lt=date_max).iterator():
            if f.est_soldee():
                nb_factures += 1
                for p in f.paiements.iterator():
                    paiements[p.type.nom] += p.montant
                for p in f.produits.iterator():
                    nom = p.produit.categorie.nom
                    if nom in categories:
                        if p.produit.nom in nb_plats[nom]:
                            nb_plats[nom][p.produit.nom] += 1
                        else:
                            nb_plats[nom][p.produit.nom] = 1
                        nb_plats[nom]['total'] += 1
                total += f.get_montant()
                tva_normal += f.getTvaNormal()
                tva_alcool += f.getTvaAlcool()
        # enregistrement
        #self.check_path(settings.PATH_TICKET)
        #filename = "%s/%s" % (settings.PATH_TICKET, \
        #                        date.strftime("jour-%Y%m%d"))
        #fd = open(filename, "w")
        texte = []
        #fd.write("       -- %s --\n" % date.strftime("%d/%m/%Y"))
        #fd.write("CA TTC (% 4d fact.): %11.2f\n" % (nb_factures, total))
        #fd.write("%-20s %11.2f\n" % ("total TVA  5.5:", tva_normal))
        #fd.write("%-20s %11.2f\n" % ("total TVA 19.6:", tva_alcool))
        texte.append("       -- %s --" % date.strftime("%d/%m/%Y"))
        texte.append("CA TTC (% 4d fact.): %11.2f" % (nb_factures, total))
        texte.append("%-20s %11.2f" % ("total TVA  5.5:", tva_normal))
        texte.append("%-20s %11.2f" % ("total TVA 19.6:", tva_alcool))
        for p in PaiementType.objects.iterator():
            if paiements[p.nom]:
                #fd.write("%-20s %11.2f\n" % (p.nom, paiements[p.nom]))
                texte.append("%-20s %11.2f" % (p.nom, paiements[p.nom]))
        for cate in categories:
            if nb_plats[cate]:
                if nb_plats[cate]['total'] > 0:
#                    fd.write("%-21s %10d\n" % (cate, nb_plats[cate]['total']))
                    texte.append("%-21s %10d" % (cate, nb_plats[cate]['total']))
                    for p in nb_plats[cate]:
                        if p != "total":
                            texte.append(" %-20s %10d" % (p, nb_plats[cate][p]))
#                            fd.write(" %-20s %10d\n" % (p, nb_plats[cate][p]))
#        fd.write("\n")
#        fd.write("\n")
#        fd.write("\n")
#        fd.write("\n")
#        fd.write("\n")
#        fd.close()
#        return filename
        return texte

    def get_working_date(self):
        """Retourne la journee de travail officiel
        (qui fini a 5h du matin)"""
        tmp = self.date_creation
        if tmp:
            if tmp.hour < 5:
                # jour de travail precedent
                return tmp - datetime.timedelta(days=1)
            else:
                return tmp
        else:
            logging.warning("la facture n'a pas de date_creation")
            return None

    def maj_stats_avec_nouvelles_factures(self):
        """Calcule les stats pour toutes les nouvelles factures
        soldées."""
        selection = Facture.objects.filter(saved_in_stats=False)
        logging.info("parcours des factures")
        for facture in selection.iterator():
            facture.maj_stats()


    def maj_stats(self):
        """Calcule les statistiques pour cette facture
        si elle est soldée"""
        try:
            nb_factures = LogType.objects.get(nom="nb_factures")
            nb_couverts = LogType.objects.get(nom="nb_couverts")
            nb_bar = LogType.objects.get(nom="nb_bar")
            ca = LogType.objects.get(nom="ca")
            tva_alcool = LogType.objects.get(nom="tva_alcool")
            tva_normal = LogType.objects.get(nom="tva_normal")
            montant_alcool = LogType.objects.get(nom="montant_alcool")
            montant_normal = LogType.objects.get(nom="montant_normal")
            ca_resto = LogType.objects.get(nom="ca_resto")
            ca_bar = LogType.objects.get(nom="ca_bar")
            tm_bar = LogType.objects.get(nom="tm_bar")
            tm_resto = LogType.objects.get(nom="tm_resto")
        except LogType.DoesNotExist:
            logging.warning("il manque un type, abandon")
            return

        if self.est_soldee():
            date = self.get_working_date()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=nb_factures)[0]
            stats.valeur += 1
            stats.save()
            tmp_montant = self.get_montant()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=ca)[0]
            stats.valeur += tmp_montant
            stats.save()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=tva_alcool)[0]
            stats.valeur += self.getTvaAlcool()
            stats.save()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=tva_normal)[0]
            stats.valeur += self.getTvaNormal()
            stats.save()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=montant_alcool)[0]
            stats.valeur += self.montant_alcool
            stats.save()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=montant_normal)[0]
            stats.valeur += self.montant_normal
            stats.save()
            if self.est_un_repas():
                # nb_couverts
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=nb_couverts)[0]
                if self.couverts == 0:
                    self.couverts = self.guest_couverts()
                    self.save()
                stats.valeur += self.couverts
                tmp_couverts = stats.valeur
                stats.save()
                # ca_resto
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=ca_resto)[0]
                stats.valeur += tmp_montant
                tmp_ca = stats.valeur
                stats.save()
                # tm_resto
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=tm_resto)[0]
                if tmp_couverts == 0:
                    stats.valeur = 0
                else:
                    stats.valeur = tmp_ca / tmp_couverts
                stats.save()
            else:
                # nb_bar
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=nb_bar)[0]
                stats.valeur += 1
                tmp_couverts = stats.valeur
                stats.save()
                # ca_bar
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=ca_bar)[0]
                stats.valeur += tmp_montant
                tmp_ca = stats.valeur
                stats.save()
                # tm_bar
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=tm_bar)[0]
                if tmp_couverts == 0:
                    stats.valeur = 0
                else:
                    stats.valeur = tmp_ca / tmp_couverts
                stats.save()
            for vendu in self.produits.iterator():
                # produit
                stats = StatsJourProduit.objects.get_or_create(date=date, produit=vendu.produit)[0]
                stats.valeur += vendu.prix
                stats.nb += 1
                stats.save()
                for sous_vendu in vendu.contient.iterator():
                    # il n'y a pas de CA donc on ne le compte pas
                    stats = StatsJourProduit.objects.get_or_create(date=date, produit=sous_vendu.produit)[0]
                    stats.nb += 1
                    stats.save()
                    # categorie
                    stats = StatsJourCategorie.objects.get_or_create(date=date, categorie=sous_vendu.produit.categorie)[0]
                    stats.nb += 1
                    stats.save()
                # categorie
                stats = StatsJourCategorie.objects.get_or_create(date=date, categorie=vendu.produit.categorie)[0]
                stats.valeur += vendu.prix
                stats.nb += 1
                stats.save()
            for paiement in self.paiements.iterator():
                stats = StatsJourPaiement.objects.get_or_create(date=date, paiement=paiement.type)[0]
                stats.valeur += paiement.montant
                if paiement.nb_tickets > 0:
                    stats.nb += paiement.nb_tickets
                else:
                    stats.nb += 1
                stats.save()
            self.saved_in_stats = True
            self.save()

    def ticket(self):
        """Retourne le ticket sous la forme d'une liste de ligne.
        """
        #self.check_path(settings.PATH_TICKET)
        #filename = "%s/%s" % (settings.PATH_TICKET, \
        #        self.date_creation.strftime("%Y%m%d%H%M%S"))
        #fd = open(filename, "w")
        texte = []
        #fd.write("           le Saint Saens\n")
        #fd.write("       -----------------------\n")
        #fd.write("       sarl Brasserie des Arts\n")
        #fd.write("       SIRET: 502 922 032 00011\n")
        #fd.write("        tel: 02.35.71.03.12\n")
        #fd.write("      120 rue du General Leclerc\n")
        #fd.write("             76000 Rouen\n")
        #fd.write("\n")
        texte.append("           le Saint Saens")
        texte.append("       -----------------------")
        texte.append("       sarl Brasserie des Arts")
        texte.append("       SIRET: 502 922 032 00011")
        texte.append("        tel: 02.35.71.03.12")
        texte.append("      120 rue du General Leclerc")
        texte.append("             76000 Rouen")
        texte.append(" ")
        if self.table != None:
            table = self.table
        else:
            table = "T--"
        #fd.write("%s - table: %s\n" % (self.date_creation.strftime("%d/%m/%Y %H:%M"), table))
        #fd.write("=======================================\n")
        texte.append("%s - table: %s" % (self.date_creation.strftime("%d/%m/%Y %H:%M"), table))
        texte.append("=======================================")
        for vendu in self.produits.order_by( \
                            "produit__categorie__priorite").iterator():
            #fd.write("  %s\n" % vendu.show())
            texte.append("  %s" % vendu.show())
        #fd.write("=======================================\n")
        texte.append("=======================================")
        if self.est_surtaxe():
            #fd.write("   Total (terrasse) : % 8.2f Euros\n" % self.total())
            texte.append("   Total (terrasse) : % 8.2f Euros" % self.total())
        else:
            #fd.write("   Total            : % 8.2f Euros\n" % self.total())
            texte.append("   Total            : % 8.2f Euros" % self.total())
        #fd.write("      dont TVA 5,5  : % 8.2f Euros\n" % self.getTvaNormal())
        #fd.write("      dont TVA 19,6 : % 8.2f Euros\n" % self.getTvaAlcool())
        #fd.write("=======================================\n")
        texte.append("      dont TVA 5,5  : % 8.2f Euros" % self.getTvaNormal())
        texte.append("      dont TVA 19,6 : % 8.2f Euros" % self.getTvaAlcool())
        texte.append("=======================================")
# il y a 70 tirets
#       fd.write("----------------------------------------------------------------------\n")
        #fd.write(" Service tous les jours de 7h a 22h30\n")
        #fd.write("   sauf le mardi soir, mercredi soir\n")
        #fd.write("          et le dimanche soir\n")
        #fd.write("\n")
        #fd.write("       - Merci de votre visite -\n")
        #fd.write("\n")
        texte.append(" Service tous les jours de 7h a 22h30")
        texte.append("   sauf le mardi soir, mercredi soir")
        texte.append("          et le dimanche soir")
        texte.append(" ")
        texte.append("       - Merci de votre visite -")
        texte.append(" ")
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.close()
        #return filename
        return texte

    def show(self):
        if self.table:
            table = self.table.nom
        else:
            table = "T--"
        if self.date_creation:
            date = self.date_creation.strftime("%H:%M:%S %d/%m/%y")
        else:
            date = "--:--:-- --/--/--"
        return "%s %s" % (table, date)

    def showPaiements(self):
        result = []
        for paiement in self.paiements.all():
            deb = "%s " % paiement.type.nom_facture
            if paiement.type.fixed_value:
                deb += "(%s x %.0f) " % (paiement.valeur_unitaire, paiement.nb_tickets)
            fin = " %.2f " % paiement.montant
            result.append(deb+remplissage(len(deb+fin), ".", 30)+fin)
        return result

