#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import elementary
import edje
import ecore
import evas

import sys, os
sys.path.append('/home/pos')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

from possum.base.models import LogType

#----- Notify -{{{-
def notify_close(bt, notify):
    notify.hide()

def add_check(obj):
    print "test check 4"

def notify_show(bt, win, orient):

    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(elementary.ELM_NOTIFY_ORIENT_CENTER)

    frame = elementary.Frame(win)
    frame.label_set("Graphiques")
    frame.show()

    notify.content_set(frame)

#    tb = elementary.Table(win)
    #tb.homogenous_set(True)
#    tb.show()
#    frame.content_set(tb)

    vbox = elementary.Box(win)
    vbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    vbox.show()
    frame.content_set(vbox)

    hbox = elementary.Box(win)
    hbox.horizontal_set(True)
    hbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    hbox.show()

    frame_data = elementary.Frame(win)
    frame_data.label_set("Données")
    frame_data.show()
    table_data = elementary.Table(win)
    table_data.show()
    frame_data.content_set(table_data)

    x_1 = 0
    y_1 = 0
    for log in LogType.objects.filter(id__gt=8).exclude(nom="maj_stats"):
        check = elementary.Check(win)
        check.label_set(log.description)
        check.callback_changed_add(add_check)
        check.show()
        table_data.pack(check, x_1, y_1, 1, 1)
        if x_1 > 2:
            x_1 = 0
            y_1 += 1
        else:
            x_1 += 1

    frame_type = elementary.Frame(win)
    frame_type.label_set("Type")
    frame_type.show()
    table_type = elementary.Table(win)
    table_type.show()
    frame_type.content_set(table_type)

    rd = elementary.Radio(win)
    rd.state_value_set(0)
    rd.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    rd.size_hint_align_set(evas.EVAS_HINT_FILL, 0.5)
    rd.label_set("entier")
    table_type.pack(rd, 0, 0, 1, 1)
    rd.show()
    rdg = rd

    rd = elementary.Radio(win)
    rd.state_value_set(1)
    rd.label_set("par mois")
    rd.group_add(rdg)
    table_type.pack(rd, 0, 1, 1, 1)
    rd.show()

    rd = elementary.Radio(win)
    rd.state_value_set(2)
    rd.group_add(rdg)
    rd.label_set("par semaine")
    table_type.pack(rd, 1, 0, 1, 1)
    rd.show()

    rd = elementary.Radio(win)
    rd.state_value_set(3)
    rd.group_add(rdg)
    rd.label_set("par année")
    table_type.pack(rd, 1, 1, 1, 1)
    rd.show()

    toggle = elementary.Toggle(win)
    toggle.label_set("Légende")
    toggle.states_labels_set("avec", "sans")
    toggle.show()
    toggle.state_set(True)
    table_type.pack(toggle, 0, 2, 2, 1)

    frame_interval = elementary.Frame(win)
    frame_interval.label_set("Interval")
    frame_interval.show()
    table_interval = elementary.Table(win)
    table_interval.show()
    frame_interval.content_set(table_interval)

    label = elementary.Label(win)
    label.label_set("Début:")
    label.show()
    table_interval.pack(label, 0, 0, 1, 1)

    button = elementary.Button(win)
    button.label_set("31")
    button.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    button.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    button.show()
    table_interval.pack(button, 1, 0, 1, 1)

    button = elementary.Button(win)
    button.label_set("Janvier")
    button.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    button.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    button.show()
    table_interval.pack(button, 2, 0, 1, 1)

    button = elementary.Button(win)
    button.label_set("2011")
    button.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    button.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    button.show()
    table_interval.pack(button, 3, 0, 1, 1)

    label = elementary.Label(win)
    label.label_set("Fin:")
    label.show()
    table_interval.pack(label, 0, 1, 1, 1)

    button = elementary.Button(win)
    button.label_set("31")
    button.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    button.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    button.show()
    table_interval.pack(button, 1, 1, 1, 1)

    button = elementary.Button(win)
    button.label_set("Décembre")
    button.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    button.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    button.show()
    table_interval.pack(button, 2, 1, 1, 1)

    button = elementary.Button(win)
    button.label_set("2011")
    button.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    button.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    button.show()
    table_interval.pack(button, 3, 1, 1, 1)

    bt = elementary.Button(win)
    bt.label_set("Afficher")
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    table_interval.pack(bt, 0, 2, 4, 1)

    hbox.pack_end(frame_data)
    hbox.pack_end(frame_type)
    hbox.pack_end(frame_interval)
    #tb.pack(frame_data, 0, 0, 3, 3)
    #tb.pack(frame_type, 3, 0, 2, 3)
    #tb.pack(frame_interval, 5, 0, 2, 3)

    vbox.pack_end(hbox)

#    frame_image = elementary.Frame(win)
#    frame_image.label_set("Interval")
#    frame_image.show()
#    table_interval = elementary.Table(win)
#    table_interval.show()
#    frame_interval.content_set(table_interval)

#    box_image = elementary.Box(win)
#    box_image.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
#    box_image.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    #win.resize_object_add(box0)
#    box_image.show()
#    frame_image.content_set(box_image)

#    bg = elementary.Background(win)
#    #frame_image.resize_object_add(bg)
#    bg.file_set("/tmp/ca_par_jour.png")
#    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
#    bg.show()
#    frame_image.content_set(bg)

    image = elementary.Image(win)
#    #image.size_set(300, 500)
    #image.resize(600, 400)
    image.file_set("ca_par_jour.png")
#    #image.size_hint_aspect_set(evas.EVAS_ASPECT_CONTROL_BOTH, 1, 1)
    image.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    image.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
#    #icon.scale_set(0, 0)
#    #win.resize_object_add(icon)
#    tb.pack(image, 0, 3, 7, 3)
    image.show()
    vbox.pack_end(image)
#    box_image.pack_end(image)

    #tb.pack(box_image, 0, 3, 7, 3)

    sp = elementary.Separator(win)
    sp.horizontal_set(True)
    sp.show()
    #tb.pack(sp, 0, 6, 7, 1)
    vbox.pack_end(sp)

    bt = elementary.Button(win)
    bt.label_set("Retour")
    bt.callback_clicked_add(notify_close, notify)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.show()
    #tb.pack(bt, 0, 7, 7, 1)
    vbox.pack_end(bt)

    notify.show()

def destroy(obj):
    elementary.exit()

def notify_clicked(obj, it):
    win = elementary.Window("notify", elementary.ELM_WIN_BASIC)
    win.callback_destroy_add(destroy)
    win.title_set("Notify test")
    win.autodel_set(True)
    #win.size_hint_min_set(160, 160)
    #win.size_hint_max_set(320, 320)
    win.resize(1024, 768)

    bg = elementary.Background(win)
    win.resize_object_add(bg)
    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bg.show()

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    win.resize_object_add(tb)
    tb.show()

    bt = elementary.Button(win)
    bt.label_set("Show notify")
    bt.callback_clicked_add(notify_show, win, elementary.ELM_NOTIFY_ORIENT_CENTER)
    tb.pack(bt, 0, 0, 1, 1)
    bt.show()

    notify_show(bt, win, elementary.ELM_NOTIFY_ORIENT_CENTER)

    win.show()


if __name__ == "__main__":
    elementary.init()
    notify_clicked(None, None)
    elementary.run()
    elementary.shutdown()
