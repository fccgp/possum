from possum.base.models import Accompagnement, Sauce, Etat, \
    Categorie, Couleur, Cuisson, Facture, Log, LogType, Paiement, \
    PaiementType, Produit, ProduitVendu, Suivi, Table, Zone
from django.contrib import admin


admin.site.register(Accompagnement)
admin.site.register(Sauce)
admin.site.register(Cuisson)
admin.site.register(Log)
admin.site.register(LogType)
admin.site.register(PaiementType)
admin.site.register(Suivi)

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'surtaxe', 'prix_surtaxe')
admin.site.register(Zone, ZoneAdmin)

class TableAdmin(admin.ModelAdmin):
    list_display = ('zone', 'nom')
    list_filter = ['zone']
admin.site.register(Table, TableAdmin)

class CategorieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
admin.site.register(Categorie, CategorieAdmin)

class ProduitVenduAdmin(admin.ModelAdmin):
    list_display = ('facture', 'date', 'produit')
    list_filter = ['date']
#    fields = ['cuisson', 'sauce', 'accompagnement', 'contient']
admin.site.register(ProduitVendu, ProduitVenduAdmin)

class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'categorie')
    list_filter = ['categorie']
admin.site.register(Produit, ProduitAdmin)

class EtatAdmin(admin.ModelAdmin):
    list_display = ('priorite', 'nom')
admin.site.register(Etat, EtatAdmin)

class CouleurAdmin(admin.ModelAdmin):
    list_display = ('nom','red','green','blue')
admin.site.register(Couleur, CouleurAdmin)

class FactureAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_creation', 'couverts', 'montant_normal', 'montant_alcool')
    list_filter = ['date_creation']
    search_fields = ['id']
admin.site.register(Facture, FactureAdmin)

class PaiementAdmin(admin.ModelAdmin):
    list_display = ('facture', 'date', 'montant')
    list_filter = ['date']
admin.site.register(Paiement, PaiementAdmin)
