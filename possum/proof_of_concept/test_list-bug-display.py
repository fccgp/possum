#!/usr/bin/env python
# bug affichage 1
import elementary
import evas

def bt_clicked_ok(li, item):
    li.item_append("newline 1")
    item.delete()
    li.item_append("newline 2")

def bt_clicked_ko(li, item):
    item.delete()
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

    items = [("test1", bt_clicked_ok),
             ("test2", bt_clicked_ko)]

    li = elementary.List(win)
    li.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    li.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    box0.pack_end(li)
    li.show()

    for item in items:
        li.item_append(item[0], callback=item[1])

    li.go()

    win.resize(250,200)
    win.show()
    elementary.run()
    elementary.shutdown()
