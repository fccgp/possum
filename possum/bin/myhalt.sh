#!/bin/bash
# on remplace le /sbin/reboot par defaut en forcant
# une sauvegarde de la base et une copie a distance
# pour installer:
# ajouter ce script dans le stop de postgres

if [ -e /home/pos/pg/bd.dump.old ]
then
    mv /home/pos/pg/bd.dump.old /home/pos/pg/bd.dump.old.old
fi
if [ -e /home/pos/pg/bd.dump ]
then
    mv /home/pos/pg/bd.dump /home/pos/pg/bd.dump.old
fi
su postgres -c "/usr/bin/pg_dumpall --clean --file=/home/pos/pg/bd.dump"
/home/pos/bin/backup.sh
#echo "les parametres [$@]"
#/sbin/reboot.real $@
#/sbin/shutdown
#/sbin/reboot -h
#/sbin/shutdown -h 0

