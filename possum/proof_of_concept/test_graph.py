#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append('/home/pos')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from possum.base.models import Accompagnement, Sauce, Etat, \
    Categorie, Couleur, Cuisson, Facture, Log, LogType, Paiement, \
    PaiementType, Produit, ProduitVendu, Suivi, Table, Zone, \
    StatsJourCategorie, StatsJourGeneral, StatsJourProduit
#    StatsSemaineCategorie, StatsSemaineGeneral, StatsSemaineProduit

import datetime

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import dates

from django.db.models import Avg, Max, Min

# afficher stat:
#   meilleure semaine ca/ .. TM ...
#   meilleure jour
#   pire semaine
#   pire jour
# http://docs.djangoproject.com/en/dev/topics/db/aggregation/

# modifier graph, si plus de XXX points alors on regroupe par semaine..

def graph(output, data, legend=True):
    """
    - output : le fichier ou la requete de sortie
    - data : les donnees a afficher. On considere qu'elles sont triees
        de la plus vieille a la plus recente et sous la forme:
        [ [[les dates], [les donnees], [le label], [la couleur]], [], [] ]
    """
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)

    date_min = data[0][0][0]
    date_max = data[0][0][-1]
    for a_line in data:
        if a_line[0][0] < date_min:
            date_min = a_line[0][0]
        if a_line[0][-1] > date_max:
            date_max = a_line[0][-1]
        if len(a_line[0]) > 80:
            print "trop grand, on fait des moyennes par semaines"
            # on fait des moyennes par semaines
            # le dimanche regroupe la semaine du lundi au dimanche
            axe_x = []
            axe_y = []
            total = 0
            count = 0
            index = 0
            for i in a_line[0]:
                # on parcours les dates
                if i.isoweekday() == 7:
                    # c'est dimanche, on enregistre
                    axe_x.append(i)
                    if count == 0:
                        axe_y.append(0)
                    else:
                        axe_y.append(total / count)
                    total = 0
                    count = 0
                else:
                    count += 1
                    total += a_line[1][index]
                index += 1
        else:
            axe_x = a_line[0]
            axe_y = a_line[1]
        ax.plot_date(axe_x, axe_y, fmt='-', label=a_line[2], color=a_line[3])

    # en fonction du nombre de jours entre le debut et la fin,
    # on choisit le bon locator
    delta = date_max - date_min
    if delta.days > 600:
        fmt = dates.DateFormatter('%Y')
        ax.xaxis.set_major_formatter(fmt)
        ax.xaxis.set_major_locator(dates.YearLocator())
        ax.xaxis.set_minor_locator(dates.MonthLocator())
        fig.autofmt_xdate(bottom=0.18)
    elif delta.days > 50:
        fmt = dates.DateFormatter('%Y-%m')
        ax.xaxis.set_major_formatter(fmt)
        ax.xaxis.set_major_locator(dates.MonthLocator())
        ax.xaxis.set_minor_locator(dates.DayLocator())
        fig.autofmt_xdate(bottom=0.18)
    else:
        ax.xaxis.set_major_formatter(dates.DateFormatter('%m-%Y'))
        ax.xaxis.set_major_locator(dates.MonthLocator())
#        ax.xaxis.set_minor_formatter(dates.DateFormatter('%d-%m'))
        ax.xaxis.set_minor_locator(dates.DayLocator())
        fig.autofmt_xdate(bottom=0.18)

    # positionnement de la legende
    if legend:
        ax.legend(loc='best')
    ax.grid(True)

    canvas.print_png(output)

# nb par categorie
selection = []
index = 0
for categorie in Categorie.objects.iterator():
    tmp = []
    date = datetime.datetime.today()-datetime.timedelta(days=40)
    my_filter = StatsJourCategorie.objects.filter(categorie=categorie,date__gt=date).order_by("date")
    tmp.append([i.date for i in my_filter.iterator()])
    tmp.append([int(i.valeur) for i in my_filter.iterator()])
    tmp.append(categorie.nom)
    tmp.append(categorie.couleur.web())
    selection.append(tmp)
graph("/tmp/ca_categorie-62.png", selection, legend=False)
# ca par jour
selection = []
couleur = {}
couleur["ca_resto"] = "green"
couleur["ca_bar"] = "blue"
for nom in ["ca_resto", "ca_bar"]:
    log = LogType.objects.get(nom=nom)
    tmp = []
    date = datetime.datetime.today()-datetime.timedelta(days=40)
    my_filter = StatsJourGeneral.objects.filter(type=log,date__gt=date).order_by("date")
    print nom
    print my_filter.aggregate(Avg('valeur'), Max('valeur'), Min('valeur'))
    tmp.append([i.date for i in my_filter.iterator()])
    tmp.append([int(i.valeur) for i in my_filter.iterator()])
    tmp.append(log.description)
    tmp.append(couleur[nom])
    selection.append(tmp)
graph("/tmp/ca_par_jour-62.png", selection)
# CA depuis le debut
selection = []
couleur = {}
couleur["ca_resto"] = "green"
couleur["ca_bar"] = "blue"
for nom in ["ca_resto", "ca_bar"]:
    log = LogType.objects.get(nom=nom)
    tmp = []
    my_filter = StatsJourGeneral.objects.filter(type=log).order_by("date")
    print nom
    print my_filter.aggregate(Avg('valeur'), Max('valeur'), Min('valeur'))
    tmp.append([i.date for i in my_filter.iterator()])
    tmp.append([int(i.valeur) for i in my_filter.iterator()])
    tmp.append(log.description)
    tmp.append(couleur[nom])
    selection.append(tmp)
graph("/tmp/ca_par_jour.png", selection)


# ca par semaine
#%W
#http://homepage.mac.com/s_lott/books/python/html/p04/p04c05_time.html
#def fromisocalendar(y,w,d):
#   return datetime.strptime( "%04dW%02d-%d"%(y,w-1,d), "%YW%W-%w")

#selection = []
#couleur = {}
#couleur["ca_resto"] = "green"
#couleur["ca_bar"] = "blue"
#for nom in ["ca_resto", "ca_bar"]:
#    log = LogType.objects.get(nom=nom)
#    tmp = []
#    tmp.append([i.date for i in StatsSemaineGeneral.objects.filter(type=log).order_by("date")])
#    tmp.append([int(i.valeur) for i in StatsSemaineGeneral.objects.filter(type=log).order_by("date")])
#    tmp.append(log.description)
#    tmp.append(couleur[nom])
#    selection.append(tmp)
#graph("/tmp/ca_par_semaine.png", selection)

# resto par jour
selection = []
couleur = {}
couleur["nb_couverts"] = "green"
couleur["tm_resto"] = "blue"
for nom in ["nb_couverts", "tm_resto"]:
    log = LogType.objects.get(nom=nom)
    tmp = []
    date = datetime.datetime.today()-datetime.timedelta(days=40)
    my_filter = StatsJourGeneral.objects.filter(type=log,date__gt=date).order_by("date")
    print nom
    print my_filter.aggregate(Avg('valeur'), Max('valeur'), Min('valeur'))
    tmp.append([i.date for i in my_filter.iterator()])
    tmp.append([int(i.valeur) for i in my_filter.iterator()])
    tmp.append(log.description)
    tmp.append(couleur[nom])
    selection.append(tmp)
graph("/tmp/resto-40.png", selection)

#>>> Book.objects.aggregate(Avg('price'), Max('price'), Min('price'))
#{'price__avg': 34.35, 'price__max': Decimal('81.20'), 'price__min': Decimal('12.99')}
