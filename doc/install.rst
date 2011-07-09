Installation
============

Utilisateur
-----------

Tout d'abord, nous allons créer un utilisateur ''pos'' qui aura comme ''home'' : /home/pos:

::

  sudo adduser pos

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


Ensuite il faut initialiser Enlightenment en lançant une session. Le plus
simple est de se connecter en mode texte avec l'utilisateur POS puis 
lancer l'interface graphique avec la commande: startx

Une fois connecté, au premier lancement vous avez quelques paramètres 
à configurer:

- Language: Français
- Profil: Minimaliste 
- Menus: Enlightenment Default

Ensuite, on peut aussi changer le fond d'écran:

- clic gauche sur le fond d'écran
- configuration > Fond d'écran
- Système > Dark_Gradient
 

Django
------

Installation de Django:

::

  sudo apt-get install python-django python-werkzeug

Il est conseillé de prendre au minimum une version 1.2.3.

Il faudra également configurer une base de données, pour cela la documentation de Django
est bien faite: `Installation de Django <http://docs.django-fr.org/intro/install.html>`_


Possum
------

Création de la base pour l'application:

::

  ./manage.py syncdb
  
  You just installed Django's auth system, which means you don't have any superusers defined.
  Would you like to create one now? (yes/no): yes
  Username (Leave blank to use 'pos'): my_login
  E-mail address: my.login@example.org
  Password: 
  Password (again): 
  Superuser created successfully.


Il est préférable d'avoir un serveur de mail configurer sur le poste. En
effet, POSSUM peut envoyé des messages s'il y a des tentatives d'accès
au panneau d'administration ou des bugs.

::

  sudo apt-get install postfix bsd-mailx

  Système satellite : Tous les messages sont envoyés vers une autre machine, nommée un smarthost. 
  Nom de courrier : possum (ou le nom que vous voulez)
  Serveur relais SMTP (vide pour aucun) :
  Destinataire des courriels de « root » et de « postmaster » : votre_adresse_mail@example.org
  Autres destinations pour lesquelles le courrier sera accepté (champ vide autorisé) : possum, localhost.localdomain, localhost
  Faut-il forcer des mises à jour synchronisées de la file d'attente des courriels ? Non
  Réseaux internes : 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
  Taille maximale des boîtes aux lettres (en octets) : 0
  Caractère d'extension des adresses locales : +
  Protocoles internet à utiliser : tous
 
Si tout est bien configurer, vous devriez recevoir un mail avec comme
sujet ''test'' et dans le message la date d'envoie en utilisant la 
commande suivante:

::

  date | mail -s test root

On crée le groupe pour les managers:

::

  cd /home/pos/possum
  ./manage.py shell_plus
  g = Group(name='Managers')
  g.save()
  exit
  
On ajoute maintenant notre utilisateur au groupe des managers:

::

  cd /home/pos/possum
  ./manage.py shell_plus
  u = User.objects.get(username="my_login")
  u.groups.add(Group.objects.get(name='Managers'))
  u.save()
  exit

On peut également créer d'autres utilisateurs-managers:

::

  cd /home/pos/possum
  ./manage.py shell_plus
  u = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
  u.groups.add(Group.objects.get(name='Managers'))
  u.save()
  exit


L'installation est presque terminée, vous devez maintenant configurer
la sauvegarde automatique de la base de données. Cette partie dépend du
type de base que vous avez choisi. La plus simple étant la base sqlite,
sa sauvegarde se limite à la copie d'un fichier.

Configuration initiale
----------------------

Malheureusement, il n'y a pas encore d'interface web pour la modification
et la saisie des produits, cela doit être fait à la main pour le moment.

À partir de la version 0.5 une interface web de gestion sera en place et
la documentation sera faire à ce moment là.

Exemple de Matériels
--------------------

Pour finir, voici un exemple de matériels utilisés et qui fonctionne:

PC:

- carte Mini ITX VIA M6000G
- Asus EEE PC
- Shuttle SD11G5

Écran tactile:

- ELo Touch 1515L

À noter que le support de la part de EloTouch est plutôt 
moyen. Je vous conseille ce site: `EloTouchScreen <https://help.ubuntu.com/community/EloTouchScreen>`_

Imprimante à ticket:

- Epson MT M88 iv
