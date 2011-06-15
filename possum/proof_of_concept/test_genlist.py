#!/usr/bin/env python
import os
import elementary
import edje
import ecore
import evas

#----- common -{{{-
# comment est afficher l'item dans la liste
def gl_label_get(obj, part, item_data):
    return "Item # %i" % (item_data,)

def gl_icon_get(obj, part, data):
    ic = elementary.Icon(obj)
    return ic

def gl_state_get(obj, part, item_data):
    return False

def gl_sel(gli, gl, *args, **kwargs):
    print "selection item %s on genlist %s" % (gli, gl)
#    print "selection item %d" % item_data
# -}}}-

#----- Genlist -{{{-
def genlist_clicked():
    win = elementary.Window("Genlist", elementary.ELM_WIN_BASIC)
    win.title_set("Genlist test")
    win.autodel_set(True)

    bg = elementary.Background(win)
    win.resize_object_add(bg)
    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bg.show()

    bx = elementary.Box(win)
    win.resize_object_add(bx)
    bx.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bx.show()

    gl = elementary.Genlist(win)
#    def _gl_selected(gl, gli, *args, **kwargs):
#        print "selection d'un item: %d" % item_data
#    gl.callback_selected_add(_gl_selected)
    # normalement pas besoin
    #def _gl_clicked(gl, gli):
    #    print "clicked"
    #gl.callback_clicked_add(_gl_clicked)
    #def _gl_longpressed(gl, gli, *args, **kwargs):
    #    print "longpressed"
    #gl.callback_longpressed_add(_gl_longpressed)
    gl.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    gl.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bx.pack_end(gl)
    gl.show()

    #over = evas.Rectangle(win.evas_get())
    #over.color_set(0, 0, 0, 0)

    #def _gl_move(evas, evt, gl):
    #    gli = gl.at_xy_item_get(evt.position.canvas.x, evt.position.canvas.y)
    #    if gli:
    #        print "over %s", gli
    #    else:
    #        print "over none"
    #over.event_callback_add(evas.EVAS_CALLBACK_MOUSE_DOWN, _gl_move, gl)

    #over.repeat_events_set(True)
    #over.show()
    #over.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    #win.resize_object_add(over)

    itc1 = elementary.GenlistItemClass(item_style="default",
                                       label_get_func=gl_label_get,
                                       icon_get_func=gl_icon_get,
                                       state_get_func=gl_state_get)

    bt_50 = elementary.Button(win)
    bt_50.label_set("Go to 50")
    bt_50.show()
    bx.pack_end(bt_50)

    bt_1500 = elementary.Button(win)
    bt_1500.label_set("Go to 1500")
    bt_1500.show()
    bx.pack_end(bt_1500)

    def raz(bt):
        gl.clear()
        for i in xrange(30):
            gl.item_append(itc1, i, func=gl_sel)

    bt = elementary.Button(win)
    bt.label_set("RAZ")
    bt._callback_add("clicked", raz)
    bt.show()
    bx.pack_end(bt)


    for i in xrange(0, 2000):
        print "gli = gl.item_append(itc1, i, func=gl_sel)"
        gli = None
        if i == 50:
            def _bt50_cb(button, gli):
                print "gli.bring_in()"
            bt_50._callback_add("clicked", _bt50_cb, gli)
        elif i == 1500:
            def _bt1500_cb(button, gli):
                print "gli.middle_bring_in()"
            bt_1500._callback_add("clicked", _bt1500_cb, gli)

    win.resize(480, 800)
    win.show()

# }}}


#----- Main -{{{-
if __name__ == "__main__":
    def destroy(obj):
        elementary.exit()

    elementary.init()
    genlist_clicked()

    elementary.run()
    elementary.shutdown()

# }}}
# vim:foldmethod=marker
