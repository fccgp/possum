=============
Développement
=============

Lors d'un commit, on peut indiquer la référence à un ticket en indiquant dans les commentaires ''refs #234''.
On peut aussi fermer un ticket en indiquant ''fixes #234''.

Voici un exemple de commentaire: ''Ce commit concerne les refs #1, #2 et fixes #3''

Modèles
=======

Voici le schèma général des différentes classes utilisées.

.. image:: images/models-base.png
   :height: 100
   :width: 200
   :scale: 50
   :alt: Schéma des classes d'objets

À nouveau les différentes classes avec leurs héritages.

.. inheritance-diagram:: possum.base.models
   :parts: 1

La classe centrale, et donc la plus importante, est la classe Facture_.

Accompagnement
--------------

.. inheritance-diagram:: possum.base.models.Accompagnement
   :parts: 1

.. autoclass:: possum.base.models.Accompagnement
   :members:
.. _categorie:

Categorie
---------

.. inheritance-diagram:: possum.base.models.Categorie
   :parts: 1

.. autoclass:: possum.base.models.Categorie
   :members:

Couleur
-------

.. inheritance-diagram:: possum.base.models.Couleur
   :parts: 1

.. autoclass:: possum.base.models.Couleur
   :members:

Cuisson
-------

.. inheritance-diagram:: possum.base.models.Cuisson
   :parts: 1

.. autoclass:: possum.base.models.Cuisson
   :members:

Etat
----

.. inheritance-diagram:: possum.base.models.Etat
   :parts: 1

.. autoclass:: possum.base.models.Etat
   :members:

.. _Facture:

Facture
-------

.. inheritance-diagram:: possum.base.models.Facture
   :parts: 1

.. autoclass:: possum.base.models.Facture
   :members:

Log
---

.. inheritance-diagram:: possum.base.models.Log
   :parts: 1

.. autoclass:: possum.base.models.Log
   :members:

LogType
-------

.. inheritance-diagram:: possum.base.models.LogType
   :parts: 1

.. autoclass:: possum.base.models.LogType
   :members:

Paiement
--------

.. inheritance-diagram:: possum.base.models.Paiement
   :parts: 1

.. autoclass:: possum.base.models.Paiement
   :members:

PaiementType
------------

.. inheritance-diagram:: possum.base.models.PaiementType
   :parts: 1

.. autoclass:: possum.base.models.PaiementType
   :members:

Produit
-------

.. inheritance-diagram:: possum.base.models.Produit
   :parts: 1

.. autoclass:: possum.base.models.Produit
   :members:

ProduitVendu
------------

.. inheritance-diagram:: possum.base.models.ProduitVendu
   :parts: 1

.. autoclass:: possum.base.models.ProduitVendu
   :members:
.. _sauce:

Sauce
-----

.. inheritance-diagram:: possum.base.models.Sauce
   :parts: 1

.. autoclass:: possum.base.models.Sauce
   :members:
.. _suivi:

Suivi
-----

.. inheritance-diagram:: possum.base.models.Suivi
   :parts: 1

.. autoclass:: possum.base.models.Suivi
   :members:
.. _table:

Table
-----

.. inheritance-diagram:: possum.base.models.Table
   :parts: 1

.. autoclass:: possum.base.models.Table
   :members:
.. _zone:

Zone
----

.. autoclass:: possum.base.models.Zone
   :members:


Qualité
=======

La qualité générale de Possum est mesurée par Pylint.
La définition de tous les codes est `ici <http://pylint-messages.wikidot.com/all-codes>`_.

.. raw:: html
   :file: qualite.html

