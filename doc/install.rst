Installation
============

Requis
------

postgres / django / EFL

Matériels
---------

Ceci est la liste des matériels utilisés.

ubuntu on:
Mini ITX VIA M6000G
1Go DDR 400Mhz
Hard Disk 80Go P-ATA
Asus EEE PC
ELo Touch 1515L         support moyen de la part de EloTouch
Epson MT M88 iv         imprimante à ticket

écran tactile
https://help.ubuntu.com/community/EloTouchScreen

PosgreSQL
---------

Django
------

Possum
------

dans /home/pos/possum

Apache
------

Pour accèder à la partie d'administration, il nous faudra un serveur web.

::

  > sudo apt-get install libapache2-mod-wsgi
  > cat /etc/apache2/ssleay.cnf

  RANDFILE                = /dev/urandom

  [ req ]
  default_bits            = 2048
  default_keyfile         = privkey.pem
  distinguished_name      = req_distinguished_name
  prompt                  = no
  policy                  = policy_anything

  [ req_distinguished_name ]
  commonName              = @HostName@

  > sudo make-ssl-cert /etc/apache2/ssleay.cnf /etc/ssl/private/localhost.pem
  > sudo a2enmod ssl
  > sudo a2dissite default
  > cat /etc/apache2/sites-available/possum

  A REMPLIR !!

  > sudo a2ensite possum
  > sudo /etc/init.d/apache2 restart

Suivre la documentation: http://docs.djangoproject.com/en/1.2/howto/deployment/modwsgi/

Configuration
-------------

init de la base
comment renseigner la base ?
ne pas oublier de sauvegarder la base de données !!

Sauvegarde
----------

sauvegarde complète de la base:
    pg_dumpall --clean --file=bd.dump

sauvegarde seulement de certaines tables:
    pg_dump --clean --file=bd-stats.dump -t base_statsjourcategorie -t base_statsjourgeneral -t base_statsjourproduit -t base_statssemainecategorie -t base_statssemainegeneral -t base_statssemaineproduit possumdb

Restauration
------------
/usr/bin/psql -f possum-20100109.dump postgres

/usr/bin/psql -f bd-stats.dump possumdb

