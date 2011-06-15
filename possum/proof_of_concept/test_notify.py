#!/usr/bin/env python
import os
import elementary
import edje
import ecore
import evas

#----- Notify -{{{-
def notify_close(bt, notify):
    notify.hide()

def notify_show(bt, win, orient):
    notify = elementary.Notify(win)
    notify.repeat_events_set(False)
    notify.orient_set(orient)

    bx = elementary.Box(win)
    bx.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bx.horizontal_set(True)
    notify.content_set(bx)
    bx.show()

    lb = elementary.Label(win)
    lb.label_set("Text notification")
    bx.pack_end(lb)
    lb.show()

    bt = elementary.Button(win)
    bt.label_set("Close")
    bt.callback_clicked_add(notify_close, notify)
    bx.pack_end(bt)
    bt.show()
    notify.show()

def notify_show_sleep(bt, win, orient):
    notify_show(bt, win, orient)
    import time
    time.sleep(5)

def destroy(obj):
    elementary.exit()

def notify_clicked(obj, it):
    win = elementary.Window("notify", elementary.ELM_WIN_BASIC)
    win.callback_destroy_add(destroy)
    win.title_set("Notify test")
    win.autodel_set(True)
    win.size_hint_min_set(160, 160)
    win.size_hint_max_set(320, 320)
    win.resize(320, 320)

    bg = elementary.Background(win)
    win.resize_object_add(bg)
    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bg.show()

    tb = elementary.Table(win)
    tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    win.resize_object_add(tb)
    tb.show()

    bt = elementary.Button(win)
    bt.label_set("Show notify without sleep")
    bt.callback_clicked_add(notify_show, win, elementary.ELM_NOTIFY_ORIENT_CENTER)
    tb.pack(bt, 0, 0, 1, 1)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("Show notify with sleep (5 seconds)")
    bt.callback_clicked_add(notify_show_sleep, win, elementary.ELM_NOTIFY_ORIENT_CENTER)
    tb.pack(bt, 0, 1, 1, 1)
    bt.show()

    win.show()

if __name__ == "__main__":
    elementary.init()
    notify_clicked(None, None)
    elementary.run()
    elementary.shutdown()
