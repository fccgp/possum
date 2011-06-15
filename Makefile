all: help

help:
	clear
	@echo ""
	@echo "Usage: make [commande]"
	@echo " - run:		runserver_plus"
	@echo " - ihm:		IHM EFL"
	@echo " - doc:		sphinx"
	@echo " - www:		publie la documentation"
	@echo " - lint :	django-lint / pylint"
	@echo " - sync :	syncdb"
	@echo " - model :	graph_models"
	@echo " - sh :		shell_plus"
	@echo " - tests :   lancement des tests"
	@echo " - newdb :	nouvelle base !!"
	@echo ""
	@echo ""

tests:
	@cd possum; ./manage.py test

run:
	@cd possum; python manage.py runserver_plus

doc:
	cd doc && make html
	cd _build/html && git commit -a && git push origin gh-pages

www:
	cp -a doc/_build/html/* /var/www/

uml:
	tools/uml.py

ihm:
	cd possum; python gui/efl.py

lint:
	-@pylint --rcfile=tools/pylint.rc possum/gui/efl.py possum/base/models.py > doc/qualite.html
#	pylint --rcfile=../tools/pylint.rc --import-graph=../tools/pylint.dot $SRCFILES > $OUTPU

#lint: model src/gui_efl.py base/models.py
#	-@pylint --rcfile=tools/pylint.rc src/gui_efl.py base/models.py > doc/qualite.html
#	-@pylint --rcfile=tools/pylint.rc --output-format=text src/gui_efl.py base/models.py > doc/qualite.txt
#	-@django-lint -r > doc/django-lint.txt
#	-@django-lint -r

model:
	cd possum; ./manage.py graph_models --output=../doc/images/models-base.png -g base

sync:
	cd possum; ./manage.py syncdb

sh:
	cd possum; ./manage.py shell_plus

newdb:
	utils/convert_sqlite3-to-django.py
	utils/remplacer_les_accents.py
	utils/menage_dans_les_tables.py
