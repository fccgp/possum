#!/usr/bin/env python
import elementary
import evas

index = 0

def bt_clicked_next(bt, li, item):
    li.item_append("newline 1")
    li.item_append("newline 2")

def bt_clicked_prev(bt, li, item):
    li.item_append("newline 3")

if __name__ == "__main__":
    def destroy(obj):
        elementary.exit()

    elementary.init()
    win = elementary.Window("test", elementary.ELM_WIN_BASIC)
    win.title_set("List")
    win.callback_destroy_add(destroy)

    bg = elementary.Background(win)
    win.resize_object_add(bg)
    bg.show()

    box0 = elementary.Box(win)
    win.resize_object_add(box0)
    box0.show()

    li = elementary.List(win)
    li.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    li.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    li.show()
    box0.pack_end(li)

    li.item_append("line 1")
    li.item_append("line 2")
    li.go()

    bt = elementary.Button(win)
    bt.label_set("Prev")
    bt.callback_clicked_add(bt_clicked_prev, li)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    box0.pack_end(bt)
    bt.show()

    bt = elementary.Button(win)
    bt.label_set("Next")
    bt.callback_clicked_add(bt_clicked_next, li)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    box0.pack_end(bt)
    bt.show()

    win.resize(250,200)
    win.show()
    elementary.run()
    elementary.shutdown()
