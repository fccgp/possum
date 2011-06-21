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

Enlightenment
-------------

cd /home/pos
wget http://omicron.homeip.net/projects/easy_e17/easy_e17.sh
chmod u+x ./easy_e17.sh
cat .easy_e17.conf
--srcmode=full 
--low 
--disable-notification
--packagelist=full 
--skip=mpdule,emprint,screenshot,exalt,enjoy,wlan,eweather,alarm,calendar,cpu,drawer,efm_nav,efm_path,efm_pathbar,everything-mpris,everything-pidgin,everything-tracker,everything-wallpaper,everything-websearch,eweather,exalt-client,exebuf,execwatch,itask,itask-ng,flame,forecasts,iiirk,mail,mem,moon,net,news,notification,eooorg,penguins,photo,places,quickaccess,rain,skel,slideshow,snow,taskbar,tclock,tiling,uptime,weather,winlist-ng,winselector,emotion,libeweather,enlil,python-emotion,e_phys,editje,elicit,elsa,emote,empower,enki,ephoto,Eterm,expedite,exquisite,eyelight,image-viewer,rage,language,diskio,deskshow,ethumb,python-ethumb,shellementary
--cflags=-O2,-march=native,-s
--asuser
--srcrev=55768
--instpath=/home/pos/e17
--srcpath=/home/pos/e17_src/

./easy_e17.sh -i


INSTALL NOTES:
--------------------------------------------------------------------------------
The most incredible and really unbelievable dream has become true:
You compiled e17 successfully!

Starting e17:
Create a file ~/.xsession with the line 'exec /home/pos/e17/bin/enlightenment_start'.
Add a link to this file using 'ln -s ~/.xsession ~/.xinitrc'.

If you're using a login manager (GDM/KDM), select the session type 'default' in them.
If you're using the startx command, simply execute it now.

Note: e17 is still not released and it won't be in the near future. So don't
ask for a stable release. e17 is still very buggy and only for experienced users
who know what they do...

Rasterman didn't write this script so don't ask him for help with it.

Hint: From now on you can easily keep your installation up to date.
Simply run easy_e17.sh with -u instead of -i .

We hope you will enjoy your trip into e17... Have fun!
--------------------------------------------------------------------------------

ADD THESE ENVIRONMENT VARIABLES:
--------------------------------------------------------------------------------
export PATH="/home/pos/e17/bin:$PATH"
export PYTHONPATH="/home/pos/e17/lib/python2.6/site-packages:$PYTHONPATH"
export LD_LIBRARY_PATH="/home/pos/e17/lib:$LD_LIBRARY_PATH"
--------------------------------------------------------------------------------




PostgreSQL
----------

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

