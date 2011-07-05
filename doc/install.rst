Installation
============

Utilisateur
-----------

Tout d'abord, nous allons créer un utilisateur ''pos'' qui aura comme ''home'' : /home/pos:

::
  adduser pos

Enlightenment
-------------

On utilise la réversion 59661 qui correspond à la version officielle 1.0.1 des EFL.

::
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
  --srcrev=59661
  --instpath=/home/pos/e17
  --srcpath=/home/pos/e17_src/

  ./easy_e17.sh -i

  echo 'exec /home/pos/e17/bin/enlightenment_start' > ~/.xsession
  ln -sf ~/.xsession ~/.xinitrc

  dans ~/.bashrc
  export PATH="/home/pos/e17/bin:$PATH"
  export PYTHONPATH="/home/pos/e17/lib/python2.6/site-packages:$PYTHONPATH"
  export LD_LIBRARY_PATH="/home/pos/e17/lib:$LD_LIBRARY_PATH"


Ensuite il faut initialiser Enlightenment en lançant une session. Il y a plusieurs possibilités pour le faire:
- startx
- session gdm (expliquer comment faire)

Une fois connecté, au premier lancement vous avez quelques paramètres à configurer:
- Language: Français
- Profil: Minimaliste 
- Menus: Enlightenment Default

Clic gauche
- configuration > Fond d'écran
- Système > Dark_Gradient
 

Django
------

Installation de Django:

::
  sudo apt-get install python-django

Il est conseillé de prendre au minimum une version 1.2.3.

Il faudra également configurer une base de données, pour cela la documentation de Django
est bien faite: `Installation de Django <http://docs.django-fr.org/intro/install.html>`_


Serveur Mail + creation d'un manager ...
python-decimal

Possum
------

./manage.py syncdb

You just installed Django's auth system, which means you don't have any superusers defined.
Would you like to create one now? (yes/no): yes
Username (Leave blank to use 'pos'): my_login
E-mail address: my.login@example.org
Password: 
Password (again): 
Superuser created successfully.



dans /home/pos/possum

Pour créer des utilisateurs:

>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

# At this point, user is a User object that has already been saved
# to the database. You can continue to change its attributes
# if you want to change other fields.
>>> user.is_staff = True
>>> user.save()

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

Exemple de Matériels
--------------------

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

